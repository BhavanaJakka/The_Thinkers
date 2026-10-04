from flask import Blueprint, jsonify, make_response, g, current_app, request
from backend.extensions import db, limiter
from backend.models import Scan, Report, Project, Dependency, Finding, SuspiciousSignal, LicenseFinding, AttackPath, Advisory, Upload
from backend.services.auth_middleware import token_required
from backend.services.report_service import generate_pdf_report
from backend.scanner.extractor import create_temp_extract_dir
from backend.celery_worker import trigger_scan_task

scan_bp = Blueprint('scans', __name__, url_prefix='/api/scans')

@scan_bp.route('/<scan_id>/status', methods=['GET'])
@token_required
def get_scan_status(scan_id):
    """Returns scan progress and status."""
    user = g.current_user
    existing_scan = Scan.query.get(scan_id)
    if not existing_scan:
        return jsonify({'error': 'Scan not found.'}), 404
    if existing_scan.user_id != user.id:
        return jsonify({'error': 'Unauthorized access to scan status.'}), 403

    return jsonify({
        'scan_id': existing_scan.id,
        'status': existing_scan.status,
        'progress': existing_scan.progress,
        'total_dependencies': existing_scan.total_dependencies,
        'risk_score': existing_scan.risk_score,
        'error_message': existing_scan.error_message
    })

@scan_bp.route('/<scan_id>/report', methods=['GET'])
@token_required
def get_scan_report(scan_id):
    """Returns full scan report JSON with complete project details and package inventory."""
    user = g.current_user
    existing_scan = Scan.query.get(scan_id)
    if not existing_scan:
        return jsonify({'error': 'Scan not found.'}), 404
    if existing_scan.user_id != user.id:
        return jsonify({'error': 'Unauthorized access to scan report.'}), 403

    scan = existing_scan
    project = Project.query.get(scan.project_id)
    upload = Upload.query.filter_by(project_id=project.id).order_by(Upload.created_at.desc()).first() if project else None
    report = Report.query.filter_by(scan_id=scan.id).first()

    # Gather all dependencies
    dependencies = Dependency.query.filter_by(scan_id=scan.id).all()
    
    # Gather findings
    findings = Finding.query.filter_by(scan_id=scan.id).all()
    findings_list = []
    finding_dep_ids = set()
    for f in findings:
        dep = next((d for d in dependencies if d.id == f.dependency_id), None)
        adv = Advisory.query.get(f.advisory_id)
        finding_dep_ids.add(f.dependency_id)
        findings_list.append({
            'id': f.id,
            'dependency_id': f.dependency_id,
            'dependency_name': dep.name if dep else 'Unknown',
            'dependency_version': dep.version if dep else 'Unknown',
            'severity': f.severity,
            'fixed_version': f.fixed_version or 'N/A',
            'summary': f.summary,
            'osv_id': adv.osv_id if adv else 'N/A',
            'cvss_score': adv.cvss_score if adv else 0.0,
            'details': adv.details if adv else ''
        })

    # Gather suspicious signals (excluding INFO benign scripts from report list or filtering by severity)
    suspicious = SuspiciousSignal.query.filter_by(scan_id=scan.id).filter(SuspiciousSignal.severity != 'INFO').all()
    suspicious_list = []
    suspicious_dep_ids = set()
    for s in suspicious:
        dep = next((d for d in dependencies if d.id == s.dependency_id), None)
        suspicious_dep_ids.add(s.dependency_id)
        suspicious_list.append({
            'id': s.id,
            'dependency_id': s.dependency_id,
            'dependency_name': dep.name if dep else 'Unknown',
            'signal_type': s.signal_type,
            'severity': s.severity,
            'description': s.description,
            'distance_target': s.distance_target
        })

    # Gather license findings (HIGH and MEDIUM risk findings)
    licenses = LicenseFinding.query.filter_by(scan_id=scan.id).filter(LicenseFinding.risk_level.in_(['HIGH', 'MEDIUM'])).all()
    license_list = []
    license_conflict_dep_ids = set()
    for l in licenses:
        dep = next((d for d in dependencies if d.id == l.dependency_id), None)
        if l.status == 'CONFLICT' or l.risk_level in ['HIGH', 'MEDIUM']:
            license_conflict_dep_ids.add(l.dependency_id)
        license_list.append({
            'id': l.id,
            'dependency_id': l.dependency_id,
            'dependency_name': dep.name if dep else 'Unknown',
            'license_spdx': l.license_spdx,
            'status': l.status,
            'conflict_with': l.conflict_with,
            'risk_level': l.risk_level,
            'description': l.description
        })

    # Build package inventory list
    dep_list = []
    all_license_findings = LicenseFinding.query.filter_by(scan_id=scan.id).all()
    for d in dependencies:
        lic = next((l.license_spdx for l in all_license_findings if l.dependency_id == d.id), 'UNKNOWN')
        status = 'SAFE'
        if d.id in finding_dep_ids:
            sev = next((f.severity for f in findings if f.dependency_id == d.id), 'HIGH')
            status = f'{sev} VULNERABLE'
        elif d.id in suspicious_dep_ids:
            sig = next((s.signal_type for s in suspicious if s.dependency_id == d.id), 'SUSPICIOUS')
            status = f'{sig} MALWARE'
        elif d.id in license_conflict_dep_ids:
            status = 'LICENSE RISK'

        dep_list.append({
            'id': d.id,
            'name': d.name,
            'version': d.version,
            'ecosystem': d.ecosystem,
            'is_direct': d.is_direct,
            'depth': d.depth,
            'parent_name': d.parent_name or 'App Root',
            'license': lic,
            'status': status
        })

    # Gather attack paths
    paths = AttackPath.query.filter_by(scan_id=scan.id).order_by(AttackPath.severity_rank.desc()).all()
    attack_path_list = []
    for p in paths:
        target_dep = next((d for d in dependencies if d.id == p.target_dependency_id), None)
        attack_path_list.append({
            'id': p.id,
            'target_node': target_dep.name if target_dep else 'Target Node',
            'path_nodes': p.path_nodes_json,
            'depth': p.depth,
            'severity_rank': p.severity_rank
        })

    return jsonify({
        'scan_id': scan.id,
        'project_id': project.id if project else None,
        'project_name': project.name if project else 'Scan Report',
        'repository_url': project.repository_url if project else None,
        'ecosystem': project.ecosystem if project else 'npm',
        'upload_type': upload.upload_type if upload else 'file',
        'file_size': upload.file_size if upload else 0,
        'status': scan.status,
        'risk_score': scan.risk_score,
        'harmfulness_percent': (report.summary_jsonb.get('harmfulness_percent') if report and report.summary_jsonb and 'harmfulness_percent' in report.summary_jsonb else int(scan.risk_score)),
        'total_dependencies': scan.total_dependencies,
        'created_at': scan.created_at.isoformat(),
        'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
        'summary': report.summary_jsonb if report else {},
        'recommendations': report.recommendations_jsonb if report else {},
        'dependencies': dep_list,
        'findings': findings_list,
        'suspicious_signals': suspicious_list,
        'license_findings': license_list,
        'attack_paths': attack_path_list
    })

@scan_bp.route('/<scan_id>/pdf', methods=['GET'])
@token_required
def export_scan_pdf(scan_id):
    """Exports scan report as PDF file."""
    user = g.current_user
    scan = Scan.query.get(scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found.'}), 404
    if scan.user_id != user.id:
        return jsonify({'error': 'Unauthorized access to PDF export.'}), 403

    report_response = get_scan_report(scan_id)
    scan_data = report_response.get_json()

    pdf_bytes = generate_pdf_report(scan_data)

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=deptrix-report-{scan.id[:8]}.pdf'
    return response

@scan_bp.route('/<scan_id>/rescan', methods=['POST'])
@token_required
def rescan_project(scan_id):
    """Triggers re-scan for existing project."""
    user = g.current_user
    scan = Scan.query.get(scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found.'}), 404
    if scan.user_id != user.id:
        return jsonify({'error': 'Unauthorized access.'}), 403

    extract_dir = create_temp_extract_dir()

    new_scan = Scan(
        project_id=scan.project_id,
        user_id=user.id,
        status='QUEUED',
        deployment_model=scan.deployment_model
    )
    db.session.add(new_scan)
    db.session.commit()

    trigger_scan_task(current_app._get_current_object(), new_scan.id, extract_dir)

    return jsonify({
        'message': 'Re-scan queued successfully.',
        'new_scan_id': new_scan.id
    })

@scan_bp.route('/history', methods=['GET'])
@token_required
def list_scan_history():
    """Lists history of all previous scans for current user with risk scores for trend comparison."""
    user = g.current_user
    scans = Scan.query.filter_by(user_id=user.id).order_by(Scan.created_at.desc()).all()

    history = []
    for s in scans:
        proj = Project.query.get(s.project_id)
        upload = Upload.query.filter_by(project_id=s.project_id).order_by(Upload.created_at.desc()).first()
        history.append({
            'id': s.id,
            'project_name': proj.name if proj else 'Unknown Project',
            'ecosystem': proj.ecosystem if proj else 'npm',
            'upload_type': upload.upload_type if upload else 'file',
            'status': s.status,
            'risk_score': s.risk_score,
            'total_dependencies': s.total_dependencies,
            'created_at': s.created_at.isoformat(),
            'completed_at': s.completed_at.isoformat() if s.completed_at else None
        })

    return jsonify({'history': history})

@scan_bp.route('/<scan_id>', methods=['DELETE'])
@token_required
def delete_scan_history_item(scan_id):
    """Deletes a specific scan history log and its associated data."""
    user = g.current_user
    scan = Scan.query.get(scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found.'}), 404
    if scan.user_id != user.id:
        return jsonify({'error': 'Unauthorized access.'}), 403

    db.session.delete(scan)
    db.session.commit()
    return jsonify({'message': 'Scan history log deleted successfully.', 'scan_id': scan_id}), 200

@scan_bp.route('/history', methods=['DELETE'])
@token_required
def clear_all_scan_history():
    """Deletes all scan history logs for the authenticated user."""
    user = g.current_user
    scans = Scan.query.filter_by(user_id=user.id).all()
    count = len(scans)
    for s in scans:
        db.session.delete(s)
    db.session.commit()
    return jsonify({'message': f'Successfully cleared {count} scan history log(s).', 'deleted_count': count}), 200

