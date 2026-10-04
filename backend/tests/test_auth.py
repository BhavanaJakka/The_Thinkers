import pytest
from backend.models.schemas import SignUpStep1Schema, SignUpStep2Schema
from marshmallow import ValidationError

def test_signup_step1_validation_success():
    schema = SignUpStep1Schema()
    data = {
        'name': 'Omkar Nalawade',
        'email': 'test@diptrix.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!',
        'mobile': '9876543210',
        'captcha_answer': '15',
        'captcha_token': 'abc-123'
    }
    validated = schema.load(data)
    assert validated['email'] == 'test@diptrix.com'

def test_signup_step1_invalid_password():
    schema = SignUpStep1Schema()
    data = {
        'name': 'Omkar Nalawade',
        'email': 'test@diptrix.com',
        'password': 'simplepassword',  # missing uppercase, digit, special char
        'confirm_password': 'simplepassword',
        'mobile': '9876543210',
        'captcha_answer': '15',
        'captcha_token': 'abc-123'
    }
    with pytest.raises(ValidationError):
        schema.load(data)

def test_signup_step2_security_question():
    schema = SignUpStep2Schema()
    data = {
        'email': 'test@diptrix.com',
        'question_index': 2,
        'answer': 'Fluffy Dog'
    }
    validated = schema.load(data)
    assert validated['question_index'] == 2
