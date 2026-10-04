import uuid
from datetime import datetime, timezone
from backend.extensions import db

def generate_uuid():
    return str(uuid.uuid4())

class Scan(db.Model):
    __tablename__ = 'scans'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(50), default='QUEUED')  # QUEUED, PARSING, QUERYING_OSV, ANALYZING_RISKS, COMPLETED, FAILED
    progress = db.Column(db.Integer, default=0)
    deployment_model = db.Column(db.String(50), default='HOSTED')  # HOSTED, INTERNAL, DISTRIBUTED
    total_dependencies = db.Column(db.Integer, default=0)
    risk_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    dependencies = db.relationship('Dependency', backref='scan', cascade="all, delete-orphan")
    dependency_edges = db.relationship('DependencyEdge', backref='scan', cascade="all, delete-orphan")
    findings = db.relationship('Finding', backref='scan', cascade="all, delete-orphan")
    suspicious_signals = db.relationship('SuspiciousSignal', backref='scan', cascade="all, delete-orphan")
    license_findings = db.relationship('LicenseFinding', backref='scan', cascade="all, delete-orphan")
    attack_paths = db.relationship('AttackPath', backref='scan', cascade="all, delete-orphan")
    report = db.relationship('Report', backref='scan', uselist=False, cascade="all, delete-orphan")

class Package(db.Model):
    __tablename__ = 'packages'
    __table_args__ = (
        db.Index('idx_ecosystem_name_version', 'ecosystem', 'name', 'version'),
    )
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    ecosystem = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(100), nullable=False)
    license_spdx = db.Column(db.String(100), nullable=True)
    maintainers = db.Column(db.JSON, nullable=True)
    release_date = db.Column(db.DateTime, nullable=True)
    is_top_package = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Dependency(db.Model):
    __tablename__ = 'dependencies'
    __table_args__ = (
        db.Index('idx_dep_scan_id', 'scan_id'),
    )
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False)
    package_id = db.Column(db.String(36), db.ForeignKey('packages.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(100), nullable=False)
    ecosystem = db.Column(db.String(50), nullable=False)
    is_direct = db.Column(db.Boolean, default=True)
    depth = db.Column(db.Integer, default=0)
    parent_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    findings = db.relationship('Finding', backref='dependency', cascade="all, delete-orphan")
    suspicious_signals = db.relationship('SuspiciousSignal', backref='dependency', cascade="all, delete-orphan")
    license_findings = db.relationship('LicenseFinding', backref='dependency', cascade="all, delete-orphan")

class DependencyEdge(db.Model):
    __tablename__ = 'dependency_edges'
    __table_args__ = (
        db.Index('idx_edge_scan_id', 'scan_id'),
    )
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False)
    parent_package = db.Column(db.String(255), nullable=False)
    parent_version = db.Column(db.String(100), nullable=False)
    child_package = db.Column(db.String(255), nullable=False)
    child_version = db.Column(db.String(100), nullable=False)

class Advisory(db.Model):
    __tablename__ = 'advisories'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    osv_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    ecosystem = db.Column(db.String(50), nullable=False)
    package_name = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(50), default='MEDIUM')  # CRITICAL, HIGH, MEDIUM, LOW
    cvss_score = db.Column(db.Float, nullable=True)
    fixed_versions_json = db.Column(db.JSON, nullable=True)
    raw_jsonb = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Finding(db.Model):
    __tablename__ = 'findings'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False, index=True)
    dependency_id = db.Column(db.String(36), db.ForeignKey('dependencies.id', ondelete='CASCADE'), nullable=False, index=True)
    advisory_id = db.Column(db.String(36), db.ForeignKey('advisories.id', ondelete='CASCADE'), nullable=False, index=True)
    severity = db.Column(db.String(50), nullable=False)
    fixed_version = db.Column(db.String(100), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class SuspiciousSignal(db.Model):
    __tablename__ = 'suspicious_signals'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False, index=True)
    dependency_id = db.Column(db.String(36), db.ForeignKey('dependencies.id', ondelete='CASCADE'), nullable=False, index=True)
    signal_type = db.Column(db.String(100), nullable=False)  # TYPOSQUATTING, UNMAINTAINED, INSTALL_SCRIPT, VERY_NEW, MALICIOUS_OSV
    severity = db.Column(db.String(50), default='HIGH')
    description = db.Column(db.Text, nullable=False)
    distance_target = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class LicenseFinding(db.Model):
    __tablename__ = 'license_findings'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False, index=True)
    dependency_id = db.Column(db.String(36), db.ForeignKey('dependencies.id', ondelete='CASCADE'), nullable=False, index=True)
    license_spdx = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=False)  # COMPATIBLE, CONFLICT, UNKNOWN
    conflict_with = db.Column(db.String(100), nullable=True)
    risk_level = db.Column(db.String(50), default='LOW')  # HIGH, MEDIUM, LOW
    description = db.Column(db.Text, nullable=True)

class AttackPath(db.Model):
    __tablename__ = 'attack_paths'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False, index=True)
    target_dependency_id = db.Column(db.String(36), db.ForeignKey('dependencies.id', ondelete='CASCADE'), nullable=False)
    path_nodes_json = db.Column(db.JSON, nullable=False)
    depth = db.Column(db.Integer, default=1)
    severity_rank = db.Column(db.Float, default=0.0)

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    scan_id = db.Column(db.String(36), db.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    risk_score = db.Column(db.Float, default=0.0)
    summary_jsonb = db.Column(db.JSON, nullable=False)
    recommendations_jsonb = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
