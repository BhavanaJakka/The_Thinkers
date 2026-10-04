import os
import random
import string
import jwt
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, current_app
from backend.extensions import db, mail
from backend.models import User, SecurityProfile, OTPCode, AuditLog
from flask_mail import Message

SECURITY_QUESTIONS = [
    "What was the name of your first school?",
    "What is your mother's maiden name?",
    "What was the name of your first pet?",
    "What city were you born in?",
    "What is your favorite book or movie?"
]

def hash_secret(secret_text: str) -> str:
    """Hashes secret data like passwords or security answers using Werkzeug default hash."""
    return generate_password_hash(secret_text)

def verify_secret(hashed_text: str, plain_text: str) -> bool:
    """Verifies plain text against stored hash."""
    return check_password_hash(hashed_text, plain_text)

def generate_otp_code() -> str:
    """Generates a 6-digit OTP string."""
    return "".join(random.choices(string.digits, k=6))

def send_otp_email(user_email: str, otp_code: str, purpose: str):
    """Sends OTP email via Flask-Mail if configured, else logs safely."""
    subject = "Deptrix - Verification OTP Code" if purpose == 'VERIFY_ACCOUNT' else "Deptrix - Password Reset OTP Code"
    body = f"""Hello,

Your 6-digit verification OTP code for Deptrix is: {otp_code}

This code will expire in 10 minutes. Do not share this OTP with anyone.

Regards,
Deptrix Supply Chain Security Team
"""
    try:
        if current_app.config.get('MAIL_USERNAME'):
            msg = Message(subject=subject, recipients=[user_email], body=body)
            mail.send(msg)
        else:
            print(f"[MAIL MOCK SMTP] Sent to {user_email} | Subject: {subject} | OTP: {otp_code}")
    except Exception as e:
        print(f"[MAIL ERROR] Failed to send email to {user_email}: {e}")

def send_sms_otp(mobile_number: str, otp_code: str):
    """Sends SMS OTP to registered 10-digit mobile number."""
    print(f"[SMS GATEWAY MOCK] Dispatched SMS OTP {otp_code} to +91-{mobile_number}")

def create_otp_record(user_id: str, purpose: str) -> tuple[str, str | None]:
    """Generates and stores a hashed OTP for user. Enforces 60s resend cooldown."""
    existing = OTPCode.query.filter_by(user_id=user_id, purpose=purpose).order_by(OTPCode.created_at.desc()).first()
    now = datetime.now(timezone.utc)
    
    if existing and existing.resend_cooldown > now:
        wait_seconds = int((existing.resend_cooldown - now).total_seconds())
        return "", f"Please wait {wait_seconds} seconds before requesting a new OTP."

    otp_plain = generate_otp_code()
    otp_hash = hash_secret(otp_plain)
    expires_at = now + timedelta(minutes=10)
    resend_cooldown = now + timedelta(seconds=60)

    otp_record = OTPCode(
        user_id=user_id,
        code_hash=otp_hash,
        purpose=purpose,
        expires_at=expires_at,
        attempts=0,
        resend_cooldown=resend_cooldown
    )
    db.session.add(otp_record)
    db.session.commit()

    return otp_plain, None

def verify_otp_record(user_id: str, purpose: str, input_otp: str) -> tuple[bool, str]:
    """Verifies standard OTP code against stored hash."""
    now = datetime.now(timezone.utc)
    otp_record = OTPCode.query.filter_by(user_id=user_id, purpose=purpose).order_by(OTPCode.created_at.desc()).first()

    if not otp_record:
        return False, "Invalid or expired OTP."

    if otp_record.expires_at < now:
        return False, "OTP has expired. Please request a new one."

    if otp_record.attempts >= 5:
        return False, "Maximum OTP verification attempts exceeded. Please request a new OTP."

    otp_record.attempts += 1
    db.session.commit()

    if verify_secret(otp_record.code_hash, input_otp):
        db.session.delete(otp_record)
        db.session.commit()
        return True, "OTP verified successfully."

    return False, f"Incorrect OTP. {5 - otp_record.attempts} attempts remaining."

def log_audit_event(user_id: str | None, event_type: str, details: dict = None):
    """Log security and authentication events."""
    ip_address = request.remote_addr if request else "127.0.0.1"
    user_agent = request.headers.get("User-Agent") if request else "System"
    audit = AuditLog(
        user_id=user_id,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {}
    )
    db.session.add(audit)
    db.session.commit()

def generate_jwt_token(user_id: str, token_type='access') -> str:
    """Generates signed JWT token for user authentication."""
    secret = current_app.config['JWT_SECRET_KEY']
    expires_delta = current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] if token_type == 'access' else current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
    payload = {
        'sub': user_id,
        'type': token_type,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + expires_delta
    }
    return jwt.encode(payload, secret, algorithm='HS256')

def decode_jwt_token(token: str) -> dict | None:
    """Decodes and validates JWT token."""
    secret = current_app.config['JWT_SECRET_KEY']
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except Exception:
        return None
