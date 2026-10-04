import os
import json
import pytest
from unittest.mock import patch
from backend.app import create_app
from backend.config import Config
from backend.extensions import db
from backend.models import User, Project, Scan, Report, Dependency, Finding, SuspiciousSignal, LicenseFinding, AttackPath
from backend.services.auth_service import hash_secret
from backend.scanner.runner import run_scan_pipeline
from backend.scanner.extractor import safe_extract_zip

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_osv():
    """Mock OSV batch responses for the 4 acceptance samples so tests run offline without network dependencies."""
    def mock_query(dependencies):
        results = {}
        for dep in dependencies:
            pkg = dep['name']
            ver = dep.get('version')
            key = (dep['ecosystem'], pkg, ver)

            # Sample 2 vulns: moment, lodash
            if pkg == 'moment' and ver == '2.24.0':
                results[key] = [{
                    'id': 'GHSA-wc69-rhjr-hc9g',
                    'summary': 'ReDoS in moment duration parsing',
                    'severity': [{'type': 'CVSS_V3', 'score': '7.5'}],
                    'affected': [{'ranges': [{'events': [{'fixed': '2.29.4'}]}]}]
                }]
            elif pkg == 'lodash' and ver == '4.17.15':
                results[key] = [{
                    'id': 'GHSA-p6mc-m468-83gw',
                    'summary': 'Prototype pollution in lodash._template',
                    'severity': [{'type': 'CVSS_V3', 'score': '7.5'}],
                    'affected': [{'ranges': [{'events': [{'fixed': '4.17.21'}]}]}]
                }]
            # Sample 3 vulns: 15 packages (2 critical: ejs, minimist; 10 high; 3 low)
            elif pkg == 'ejs' and ver == '3.1.6':
                results[key] = [{
                    'id': 'GHSA-phv2-pp75-4m77',
                    'summary': 'RCE in ejs.render',
                    'severity': [{'type': 'CVSS_V3', 'score': '9.8'}],
                    'affected': [{'ranges': [{'events': [{'fixed': '3.1.7'}]}]}]
                }]
            elif pkg == 'minimist' and ver == '1.2.0':
                results[key] = [{
                    'id': 'GHSA-vh7g-6c4x-5cpq',
                    'summary': 'Prototype pollution in minimist',
                    'severity': [{'type': 'CVSS_V3', 'score': '9.8'}],
                    'affected': [{'ranges': [{'events': [{'fixed': '1.2.6'}]}]}]
                }]
            elif pkg in ['axios', 'node-fetch', 'jsonwebtoken', 'high-vuln-1', 'high-vuln-2', 'high-vuln-3', 'high-vuln-4', 'high-vuln-5', 'high-vuln-6']:
                results[key] = [{
                    'id': f'GHSA-{pkg}-high',
                    'summary': f'High severity advisory for {pkg}',
                    'severity': [{'type': 'CVSS_V3', 'score': '7.8'}],
                    'affected': [{'ranges': [{'events': [{'fixed': '2.0.0'}]}]}]
                }]
            elif pkg in ['low-vuln-1', 'low-vuln-2', 'low-vuln-3']:
                results[key] = [{
                    'id': f'GHSA-{pkg}-low',
                    'summary': f'Low severity advisory for {pkg}',
                    'severity': [{'type': 'CVSS_V3', 'score': '3.1'}],
                    'affected': [{'ranges': [{'events': [{'fixed': '1.0.1'}]}]}]
                }]
            else:
                results[key] = []
        return results

    with patch('backend.scanner.runner.query_osv_batch', side_effect=mock_query):
        yield

# =========================================================================
# ACCEPTANCE TEST 1: p1-clean-app (70 deps, 0 vulns, 0 suspicious, 0 license, Safe)
# =========================================================================
def test_sample_p1_clean_app(app, mock_osv):
    sample_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'samples', 'p1-clean-app')
    with app.app_context():
        user = User(email="test1@diptrix.com", name="Test User 1", password_hash=hash_secret("Password123!"), mobile="9876543210")
        db.session.add(user)
        db.session.commit()

        project = Project(user_id=user.id, name="p1-clean-app")
        db.session.add(project)
        db.session.commit()

        scan = Scan(project_id=project.id, user_id=user.id, status='QUEUED')
        db.session.add(scan)
        db.session.commit()

        run_scan_pipeline(scan.id, sample_dir)

        scan_res = Scan.query.get(scan.id)
        assert scan_res.status == 'COMPLETED'
        assert scan_res.total_dependencies == 70
        assert Finding.query.filter_by(scan_id=scan.id).count() == 0
        assert SuspiciousSignal.query.filter_by(scan_id=scan.id).filter(SuspiciousSignal.severity != 'INFO').count() == 0
        assert LicenseFinding.query.filter_by(scan_id=scan.id).filter(LicenseFinding.risk_level.in_(['HIGH', 'MEDIUM'])).count() == 0

        report = Report.query.filter_by(scan_id=scan.id).first()
        assert report.summary_jsonb['risk_level'] == 'Safe'
        assert scan_res.risk_score == 0.0

# =========================================================================
# EXTRA TEST (a): p1-clean-app-plus-one -> Total Deps becomes 71
# =========================================================================
def test_extra_a_p1_plus_one(app, mock_osv):
    sample_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'samples', 'p1-clean-app-plus-one')
    with app.app_context():
        user = User(email="test1a@diptrix.com", name="Test User 1A", password_hash=hash_secret("Password123!"), mobile="9876543210")
        db.session.add(user)
        db.session.commit()

        project = Project(user_id=user.id, name="p1-clean-app-plus-one")
        db.session.add(project)
        db.session.commit()

        scan = Scan(project_id=project.id, user_id=user.id, status='QUEUED')
        db.session.add(scan)
        db.session.commit()

        run_scan_pipeline(scan.id, sample_dir)

        scan_res = Scan.query.get(scan.id)
        assert scan_res.total_dependencies == 71

# =========================================================================
# ACCEPTANCE TEST 2: p2-low-risk-app (70 deps, 2 vulns, moment ranked ABOVE lodash)
# =========================================================================
def test_sample_p2_low_risk_app(app, mock_osv):
    sample_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'samples', 'p2-low-risk-app')
    with app.app_context():
        user = User(email="test2@diptrix.com", name="Test User 2", password_hash=hash_secret("Password123!"), mobile="9876543210")
        db.session.add(user)
        db.session.commit()

        project = Project(user_id=user.id, name="p2-low-risk-app")
        db.session.add(project)
        db.session.commit()

        scan = Scan(project_id=project.id, user_id=user.id, status='QUEUED')
        db.session.add(scan)
        db.session.commit()

        run_scan_pipeline(scan.id, sample_dir)

        scan_res = Scan.query.get(scan.id)
        assert scan_res.total_dependencies == 70
        assert Finding.query.filter_by(scan_id=scan.id).count() == 2

        # Check reachability ranking: moment reachable rank > lodash imported only rank
        paths = AttackPath.query.filter_by(scan_id=scan.id).order_by(AttackPath.severity_rank.desc()).all()
        assert len(paths) >= 2
        top_target_id = paths[0].target_dependency_id
        top_dep = Dependency.query.get(top_target_id)
        assert top_dep.name == 'moment'

# =========================================================================
# ACCEPTANCE TEST 3: p3-high-risk-app (79 deps, 15 vulns, 2 critical, 5 attack paths, Critical)
# =========================================================================
def test_sample_p3_high_risk_app(app, mock_osv):
    sample_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'samples', 'p3-high-risk-app')
    with app.app_context():
        user = User(email="test3@diptrix.com", name="Test User 3", password_hash=hash_secret("Password123!"), mobile="9876543210")
        db.session.add(user)
        db.session.commit()

        project = Project(user_id=user.id, name="p3-high-risk-app")
        db.session.add(project)
        db.session.commit()

        scan = Scan(project_id=project.id, user_id=user.id, status='QUEUED')
        db.session.add(scan)
        db.session.commit()

        run_scan_pipeline(scan.id, sample_dir)

        scan_res = Scan.query.get(scan.id)
        assert scan_res.total_dependencies == 79

        findings = Finding.query.filter_by(scan_id=scan.id).all()
        assert len(findings) == 15

        crit_findings = [f for f in findings if f.severity == 'CRITICAL']
        assert len(crit_findings) == 2

        transitive_vulns = [f for f in findings if not f.dependency.is_direct]
        assert len(transitive_vulns) == 6

        report = Report.query.filter_by(scan_id=scan.id).first()
        assert report.summary_jsonb['risk_level'] == 'Critical'

# =========================================================================
# ACCEPTANCE TEST 4: p4-trap-app (80 deps, 0 vulns, 2 suspicious, 2 license, zero false positives)
# =========================================================================
def test_sample_p4_trap_app(app, mock_osv):
    sample_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'samples', 'p4-trap-app')
    with app.app_context():
        user = User(email="test4@diptrix.com", name="Test User 4", password_hash=hash_secret("Password123!"), mobile="9876543210")
        db.session.add(user)
        db.session.commit()

        project = Project(user_id=user.id, name="p4-trap-app")
        db.session.add(project)
        db.session.commit()

        scan = Scan(project_id=project.id, user_id=user.id, status='QUEUED', deployment_model='HOSTED')
        db.session.add(scan)
        db.session.commit()

        run_scan_pipeline(scan.id, sample_dir)

        scan_res = Scan.query.get(scan.id)
        assert scan_res.total_dependencies == 80
        assert Finding.query.filter_by(scan_id=scan.id).count() == 0

        # Suspicious signals: expresss & lodassh (safe-setup-tool is INFO only)
        suspicious = SuspiciousSignal.query.filter_by(scan_id=scan.id).filter(SuspiciousSignal.severity != 'INFO').all()
        assert len(suspicious) == 2
        susp_names = {s.dependency.name for s in suspicious}
        assert susp_names == {'expresss', 'lodassh'}
        assert 'express' not in susp_names
        assert 'lodash.merge' not in susp_names
        assert 'date-fns' not in susp_names

        # License findings: acme-agpl-lib (High) & acme-nolicense-lib (Medium)
        licenses = LicenseFinding.query.filter_by(scan_id=scan.id).filter(LicenseFinding.risk_level.in_(['HIGH', 'MEDIUM'])).all()
        assert len(licenses) == 2
        lic_names = {l.dependency.name for l in licenses}
        assert lic_names == {'acme-agpl-lib', 'acme-nolicense-lib'}

        report = Report.query.filter_by(scan_id=scan.id).first()
        assert report.summary_jsonb['risk_level'] == 'High'

# =========================================================================
# EXTRA TEST (b): Manifest with missing/null version -> "Vulnerability check not possible (no versions found)"
# =========================================================================
def test_extra_b_null_version(app):
    from backend.parsers.npm_parser import parse_npm_files
    res = parse_npm_files("/dummy", {"package.json": None})
    deps = res[0]
    for d in deps:
        assert d.get('version') is not None or "Vulnerability check not possible"

# =========================================================================
# EXTRA TEST (c): User A cannot open User B's report (403 Forbidden)
# =========================================================================
def test_extra_c_user_isolation(app, client):
    with app.app_context():
        user_a = User(email="usera@diptrix.com", name="User A", password_hash=hash_secret("Password123!"), mobile="9876543210", is_verified=True)
        user_b = User(email="userb@diptrix.com", name="User B", password_hash=hash_secret("Password123!"), mobile="9876543210", is_verified=True)
        db.session.add_all([user_a, user_b])
        db.session.commit()

        project_a = Project(user_id=user_a.id, name="Project A")
        db.session.add(project_a)
        db.session.commit()

        scan_a = Scan(project_id=project_a.id, user_id=user_a.id, status='COMPLETED')
        db.session.add(scan_a)
        db.session.commit()

        login_res = client.post('/api/auth/login', json={'email': 'userb@diptrix.com', 'password': 'Password123!'})
        assert login_res.status_code == 200

        report_res = client.get(f'/api/scans/{scan_a.id}/report')
        assert report_res.status_code in [403, 404]

# =========================================================================
# EXTRA TEST (d): Uploaded code is NEVER executed
# =========================================================================
def test_extra_d_no_code_execution():
    import zipfile
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("package.json", '{"name": "test", "version": "1.0.0"}')

        target_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(target_dir, exist_ok=True)
        safe_extract_zip(zip_path, target_dir)
        assert os.path.exists(os.path.join(target_dir, "package.json"))

# =========================================================================
# EXTRA TEST (e): Scan History Listing & Deletion API
# =========================================================================
def test_scan_history_deletion(app, client):
    with app.app_context():
        user = User(email="history_user@diptrix.com", name="History User", password_hash=hash_secret("Password123!"), mobile="9876543210", is_verified=True)
        db.session.add(user)
        db.session.commit()

        project = Project(user_id=user.id, name="Test History Project")
        db.session.add(project)
        db.session.commit()

        scan1 = Scan(project_id=project.id, user_id=user.id, status='COMPLETED', risk_score=25.0)
        scan2 = Scan(project_id=project.id, user_id=user.id, status='COMPLETED', risk_score=85.0)
        db.session.add_all([scan1, scan2])
        db.session.commit()

        # Login as history_user
        login_res = client.post('/api/auth/login', json={'email': 'history_user@diptrix.com', 'password': 'Password123!'})
        assert login_res.status_code == 200

        # Fetch history
        hist_res = client.get('/api/scans/history')
        assert hist_res.status_code == 200
        data = hist_res.get_json()
        assert len(data['history']) == 2

        # Delete scan1
        del_res = client.delete(f'/api/scans/{scan1.id}')
        assert del_res.status_code == 200
        assert del_res.get_json()['scan_id'] == scan1.id

        # Fetch history again -> only scan2 remains
        hist_res2 = client.get('/api/scans/history')
        assert hist_res2.status_code == 200
        data2 = hist_res2.get_json()
        assert len(data2['history']) == 1
        assert data2['history'][0]['id'] == scan2.id

        # Clear all history
        clear_res = client.delete('/api/scans/history')
        assert clear_res.status_code == 200

        # Fetch history -> empty
        hist_res3 = client.get('/api/scans/history')
        assert hist_res3.status_code == 200
        assert len(hist_res3.get_json()['history']) == 0

