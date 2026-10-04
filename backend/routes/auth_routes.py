import uuid
import random
import string
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, make_response, current_app, g
from marshmallow import ValidationError
from backend.extensions import db, limiter
from backend.models import User, SecurityProfile, OTPCode
from backend.models.schemas import (
    SignUpStep1Schema, SignUpStep2Schema, LoginSchema,
    VerifyOTPSchema, ForgotPasswordInitSchema, ForgotPasswordResetSchema
)
from backend.services.auth_service import (
    hash_secret, verify_secret, create_otp_record, verify_otp_record,
    send_otp_email, send_sms_otp, log_audit_event, generate_jwt_token, decode_jwt_token,
    SECURITY_QUESTIONS
)
from backend.services.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

CAPTCHAS = {}

@auth_bp.route('/captcha', methods=['GET'])
def get_captcha():
    """Generates simple math captcha."""
    num1 = random.randint(10, 99)
    num2 = random.randint(1, 9)
    op = random.choice(['+', '-'])
    answer = str(num1 + num2) if op == '+' else str(num1 - num2)
    captcha_text = f"{num1} {op} {num2} = ?"
    captcha_token = str(uuid.uuid4())
    CAPTCHAS[captcha_token] = answer
    return jsonify({
        'captcha_token': captcha_token,
        'captcha_text': captcha_text
    })

@auth_bp.route('/security-questions', methods=['GET'])
def get_security_questions():
    """Returns list of 5 available security questions."""
    return jsonify({'questions': SECURITY_QUESTIONS})

@auth_bp.route('/signup-step1', methods=['POST'])
@limiter.limit("10 per minute")
def signup_step1():
    """Handles step 1 of registration: name, email, password, mobile, captcha validation."""
    data = request.get_json() or {}
    schema = SignUpStep1Schema()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    if validated['password'] != validated['confirm_password']:
        return jsonify({'errors': {'confirm_password': ['Passwords do not match.']}}), 400

    captcha_token = validated.get('captcha_token')
    captcha_answer = validated.get('captcha_answer').strip()
    expected_answer = CAPTCHAS.pop(captcha_token, None)

    if not expected_answer or captcha_answer != expected_answer:
        return jsonify({'errors': {'captcha_answer': ['Invalid or expired captcha. Please try again.']}}), 400

    existing_user = User.query.filter_by(email=validated['email'].lower()).first()
    if existing_user:
        return jsonify({'errors': {'email': ['Email address is already registered.']}}), 400

    user = User(
        name=validated['name'],
        email=validated['email'].lower(),
        password_hash=hash_secret(validated['password']),
        mobile=validated['mobile'],
        is_verified=False
    )
    db.session.add(user)
    db.session.commit()

    log_audit_event(user.id, "SIGNUP_STEP1_COMPLETED", {"email": user.email})

    return jsonify({
        'message': 'Step 1 completed successfully.',
        'email': user.email,
        'user_id': user.id
    }), 200

@auth_bp.route('/signup-step2', methods=['POST'])
@limiter.limit("10 per minute")
def signup_step2():
    """Handles step 2 of registration: security question & answer, sends OTP."""
    data = request.get_json() or {}
    schema = SignUpStep2Schema()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    user = User.query.filter_by(email=validated['email'].lower()).first()
    if not user:
        return jsonify({'error': 'User session not found. Please complete Step 1 first.'}), 404

    normalized_answer = validated['answer'].strip().lower()
    sec_profile = SecurityProfile(
        user_id=user.id,
        question_index=validated['question_index'],
        answer_hash=hash_secret(normalized_answer)
    )
    db.session.add(sec_profile)
    db.session.commit()

    otp_plain, error_msg = create_otp_record(user.id, 'VERIFY_ACCOUNT')
    if error_msg:
        return jsonify({'error': error_msg}), 429

    send_otp_email(user.email, otp_plain, 'VERIFY_ACCOUNT')
    send_sms_otp(user.mobile, otp_plain)

    log_audit_event(user.id, "SIGNUP_STEP2_OTP_SENT", {"email": user.email})

    return jsonify({
        'message': 'Security profile saved. A 6-digit OTP has been sent via email and SMS.',
        'email': user.email
    }), 200

@auth_bp.route('/verify-otp', methods=['POST'])
@limiter.limit("10 per minute")
def verify_otp():
    """Verifies account activation email/SMS OTP."""
    data = request.get_json() or {}
    schema = VerifyOTPSchema()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    user = User.query.filter_by(email=validated['email'].lower()).first()
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    success, msg = verify_otp_record(user.id, 'VERIFY_ACCOUNT', validated['otp'])
    if not success:
        return jsonify({'error': msg}), 400

    user.is_verified = True
    db.session.commit()

    log_audit_event(user.id, "ACCOUNT_VERIFIED", {"email": user.email})

    access_token = generate_jwt_token(user.id, 'access')
    refresh_token = generate_jwt_token(user.id, 'refresh')

    resp = make_response(jsonify({
        'message': 'Account verified successfully!',
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'mobile': user.mobile}
    }))
    resp.set_cookie('access_token', access_token, httponly=True, samesite='Lax', max_age=7200)
    resp.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', max_age=604800)
    return resp

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Logs user in with rate-limiting and account lockout protection."""
    data = request.get_json() or {}
    schema = LoginSchema()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    email = validated['email'].lower()
    user = User.query.filter_by(email=email).first()

    if not user:
        log_audit_event(None, "LOGIN_FAILED_UNKNOWN_USER", {"email": email})
        return jsonify({'error': 'Invalid email or password.'}), 401

    now = datetime.now(timezone.utc)
    if user.is_locked:
        if user.lock_until and user.lock_until > now:
            wait_min = int((user.lock_until - now).total_seconds() / 60) + 1
            return jsonify({'error': f'Account locked due to multiple failed attempts. Try again in {wait_min} minutes.'}), 423
        else:
            user.is_locked = False
            user.failed_attempts = 0
            user.lock_until = None
            db.session.commit()

    if not verify_secret(user.password_hash, validated['password']):
        user.failed_attempts += 1
        if user.failed_attempts >= 5:
            user.is_locked = True
            user.lock_until = now + timedelta(minutes=15)
            db.session.commit()
            log_audit_event(user.id, "ACCOUNT_LOCKED", {"email": email})
            return jsonify({'error': 'Account locked due to 5 failed attempts. Please try again in 15 minutes.'}), 423
        db.session.commit()
        log_audit_event(user.id, "LOGIN_FAILED_WRONG_PASSWORD", {"email": email, "attempts": user.failed_attempts})
        return jsonify({'error': 'Invalid email or password.'}), 401

    if not user.is_verified:
        return jsonify({'error': 'Account email is not verified yet.', 'requires_otp': True, 'email': user.email}), 403

    user.failed_attempts = 0
    user.is_locked = False
    user.lock_until = None
    db.session.commit()

    access_token = generate_jwt_token(user.id, 'access')
    refresh_token = generate_jwt_token(user.id, 'refresh')

    log_audit_event(user.id, "LOGIN_SUCCESS", {"email": email})

    resp = make_response(jsonify({
        'message': 'Login successful.',
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'mobile': user.mobile}
    }))
    resp.set_cookie('access_token', access_token, httponly=True, samesite='Lax', max_age=7200)
    resp.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax', max_age=604800)
    return resp

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logs user out by clearing auth cookies."""
    resp = make_response(jsonify({'message': 'Logged out successfully.'}))
    resp.delete_cookie('access_token')
    resp.delete_cookie('refresh_token')
    return resp

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Returns profile info for currently logged in user."""
    user = g.current_user
    sec_profile = SecurityProfile.query.filter_by(user_id=user.id).first()
    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'mobile': user.mobile,
            'is_verified': user.is_verified,
            'question_index': sec_profile.question_index if sec_profile else 0,
            'security_question': SECURITY_QUESTIONS[sec_profile.question_index] if sec_profile else 'Not set',
            'created_at': user.created_at.isoformat()
        }
    })

@auth_bp.route('/forgot-password/init-mobile', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password_init_mobile():
    """Sends 6-digit SMS OTP to registered mobile number for password recovery."""
    data = request.get_json() or {}
    mobile = data.get('mobile', '').strip()
    if not mobile or len(mobile) != 10:
        return jsonify({'error': 'Please enter a valid 10-digit mobile number.'}), 400

    user = User.query.filter_by(mobile=mobile).first()
    if user:
        otp_plain, error_msg = create_otp_record(user.id, 'RESET_PASSWORD_MOBILE')
        if not error_msg:
            send_sms_otp(user.mobile, otp_plain)
            log_audit_event(user.id, "FORGOT_PASSWORD_MOBILE_OTP_SENT", {"mobile": mobile})

    return jsonify({
        'message': 'If an account exists with this mobile number, a 6-digit SMS OTP code has been sent.',
        'mobile': mobile
    }), 200

@auth_bp.route('/forgot-password/reset-mobile', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password_reset_mobile():
    """Resets password via mobile SMS OTP verification."""
    data = request.get_json() or {}
    mobile = data.get('mobile', '').strip()
    otp = data.get('otp', '').strip()
    new_password = data.get('new_password', '').strip()

    user = User.query.filter_by(mobile=mobile).first()
    if not user:
        return jsonify({'error': 'Invalid request.'}), 400

    otp_ok, otp_msg = verify_otp_record(user.id, 'RESET_PASSWORD_MOBILE', otp)
    if not otp_ok:
        return jsonify({'error': otp_msg}), 400

    user.password_hash = hash_secret(new_password)
    user.is_locked = False
    user.failed_attempts = 0
    user.lock_until = None
    db.session.commit()

    log_audit_event(user.id, "PASSWORD_RESET_MOBILE_SUCCESS", {"mobile": mobile})

    return jsonify({'message': 'Password has been reset successfully via Mobile SMS OTP.'}), 200

@auth_bp.route('/forgot-password/init', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password_init():
    """Initiates password reset process via Email OTP."""
    data = request.get_json() or {}
    schema = ForgotPasswordInitSchema()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    email = validated['email'].lower()
    user = User.query.filter_by(email=email).first()

    if user:
        otp_plain, error_msg = create_otp_record(user.id, 'RESET_PASSWORD')
        if not error_msg:
            send_otp_email(user.email, otp_plain, 'RESET_PASSWORD')
            log_audit_event(user.id, "FORGOT_PASSWORD_OTP_SENT", {"email": email})

    return jsonify({
        'message': 'If an account exists with this email, a 6-digit OTP code has been sent via SMTP mailer.',
        'email': email
    }), 200

@auth_bp.route('/forgot-password/reset', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password_reset():
    """Verifies OTP, security question answer, and resets user password."""
    data = request.get_json() or {}
    schema = ForgotPasswordResetSchema()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    email = validated['email'].lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid request.'}), 400

    otp_ok, otp_msg = verify_otp_record(user.id, 'RESET_PASSWORD', validated['otp'])
    if not otp_ok:
        return jsonify({'error': otp_msg}), 400

    sec_profile = SecurityProfile.query.filter_by(user_id=user.id).first()
    if not sec_profile or sec_profile.question_index != validated['question_index']:
        return jsonify({'error': 'Security question verification failed.'}), 400

    normalized_answer = validated['answer'].strip().lower()
    if not verify_secret(sec_profile.answer_hash, normalized_answer):
        log_audit_event(user.id, "FORGOT_PASSWORD_SECURITY_ANSWER_FAILED", {"email": email})
        return jsonify({'error': 'Incorrect security question answer.'}), 400

    user.password_hash = hash_secret(validated['new_password'])
    user.is_locked = False
    user.failed_attempts = 0
    user.lock_until = None
    db.session.commit()

    log_audit_event(user.id, "PASSWORD_RESET_SUCCESS", {"email": email})

    return jsonify({'message': 'Password has been reset successfully. You can now log in.'}), 200
