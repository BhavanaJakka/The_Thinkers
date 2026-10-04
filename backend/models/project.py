import uuid
from datetime import datetime, timezone
from backend.extensions import db

def generate_uuid():
    return str(uuid.uuid4())

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    ecosystem = db.Column(db.String(50), nullable=True)  # npm, pypi, maven, etc.
    repository_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    uploads = db.relationship('Upload', backref='project', cascade="all, delete-orphan")
    scans = db.relationship('Scan', backref='project', cascade="all, delete-orphan")

class Upload(db.Model):
    __tablename__ = 'uploads'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_type = db.Column(db.String(50), nullable=False)  # zip, github, manifests
    file_size = db.Column(db.BigInteger, nullable=True)
    status = db.Column(db.String(50), default='PROCESSED')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
