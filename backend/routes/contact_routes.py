from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from backend.extensions import limiter, mail
from backend.models.schemas import ContactSchema
from flask_mail import Message

contact_bp = Blueprint('contact', __name__, url_prefix='/api/contact')

@contact_bp.route('', methods=['POST'])
@limiter.limit("5 per minute")
def submit_contact_form():
    """Validates and sends contact form messages."""
    data = request.get_json() or {}
    schema = ContactSchema()
    try:
        validated = schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    subject = f"[Deptrix Contact Form] {validated['subject']}"
    body = f"""New contact message received:

Name: {validated['name']}
Email: {validated['email']}
Subject: {validated['subject']}

Message:
{validated['message']}
"""
    try:
        msg = Message(
            subject=subject,
            recipients=['nalawadeomkar0508@gmail.com'],
            reply_to=validated['email'],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        print(f"[CONTACT FORM MOCK] Email from {validated['email']}: {validated['message']}")

    return jsonify({'message': 'Thank you! Your message has been sent successfully to Omkar Nalawade.'}), 200
