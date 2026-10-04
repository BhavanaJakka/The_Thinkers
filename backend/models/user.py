import uuid
from datetime import datetime, timezone
from backend.extensions import db

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    failed_attempts = db.Column(db.Integer, default=0)
    lock_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    security_profile = db.relationship('SecurityProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    otp_codes = db.relationship('OTPCode', backref='user', cascade="all, delete-orphan")
    projects = db.relationship('Project', backref='user', cascade="all, delete-orphan")
    scans = db.relationship('Scan', backref='user', cascade="all, delete-orphan")
    reports = db.relationship('Report', backref='user', cascade="all, delete-orphan")
    audit_logs = db.relationship('AuditLog', backref='user', cascade="all, delete-orphan")

class SecurityProfile(db.Model):
    __tablename__ = 'security_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    question_index = db.Column(db.Integer, nullable=False)
    answer_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class OTPCode(db.Model):
    __tablename__ = 'otp_codes'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    code_hash = db.Column(db.String(255), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # 'VERIFY_ACCOUNT' or 'RESET_PASSWORD'
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    resend_cooldown = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
