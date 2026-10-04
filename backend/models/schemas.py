import re
from marshmallow import Schema, fields, validate, validates, ValidationError

class SignUpStep1Schema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    confirm_password = fields.String(required=True)
    mobile = fields.String(required=True)
    captcha_answer = fields.String(required=True)
    captcha_token = fields.String(required=True)

    @validates('name')
    def validate_name(self, value):
        if not re.match(r'^[A-Za-z\s]+$', value):
            raise ValidationError('Name must contain only letters and spaces.')

    @validates('password')
    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit.')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', value):
            raise ValidationError('Password must contain at least one special character/symbol.')

    @validates('mobile')
    def validate_mobile(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValidationError('Mobile number must be exactly 10 digits.')

class SignUpStep2Schema(Schema):
    email = fields.Email(required=True)
    question_index = fields.Integer(required=True, validate=validate.Range(min=0, max=4))
    answer = fields.String(required=True, validate=validate.Length(min=3, max=30))

    @validates('answer')
    def validate_answer(self, value):
        if not re.match(r'^[A-Za-z0-9\s]+$', value):
            raise ValidationError('Security answer must contain only letters, numbers, and spaces.')

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class VerifyOTPSchema(Schema):
    email = fields.Email(required=True)
    otp = fields.String(required=True, validate=validate.Length(equal=6))

class ForgotPasswordInitSchema(Schema):
    email = fields.Email(required=True)

class ForgotPasswordResetSchema(Schema):
    email = fields.Email(required=True)
    otp = fields.String(required=True, validate=validate.Length(equal=6))
    question_index = fields.Integer(required=True, validate=validate.Range(min=0, max=4))
    answer = fields.String(required=True, validate=validate.Length(min=3, max=30))
    new_password = fields.String(required=True, validate=validate.Length(min=8))

    @validates('new_password')
    def validate_new_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit.')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', value):
            raise ValidationError('Password must contain at least one special character.')

class ContactSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    subject = fields.String(required=True, validate=validate.Length(min=3, max=150))
    message = fields.String(required=True, validate=validate.Length(min=10, max=2000))
