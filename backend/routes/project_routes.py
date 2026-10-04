import os
import werkzeug.utils
from flask import Blueprint, request, jsonify, g, current_app
from backend.extensions import db, limiter
from backend.models import Project, Upload, Scan
from backend.services.auth_middleware import token_required
from backend.scanner.extractor import create_temp_extract_dir, safe_extract_zip
from backend.services.github_service import fetch_github_manifests
from backend.celery_worker import trigger_scan_task

project_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

ALLOWED_EXTENSIONS = {'zip', 'json', 'txt', 'lock', 'xml', 'gradle', 'mod', 'toml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_dir_size(dirpath):
    """Calculates total size of all files in directory safely across Windows & Unix."""
    total_size = 0
    if not os.path.exists(dirpath):
        return 0
    for root, _, files in os.walk(dirpath):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size

@project_bp.route('', methods=['GET'])
@token_required
def list_user_projects():
    """Lists all projects owned by the authenticated user."""
    user = g.current_user
    projects = Project.query.filter_by(user_id=user.id).order_by(Project.created_at.desc()).all()

    result = []
    for p in projects:
        last_scan = Scan.query.filter_by(project_id=p.id).order_by(Scan.created_at.desc()).first()
        result.append({
            'id': p.id,
            'name': p.name,
            'ecosystem': p.ecosystem or 'Multi-ecosystem',
            'repository_url': p.repository_url,
            'created_at': p.created_at.isoformat(),
            'last_scan': {
                'id': last_scan.id,
                'status': last_scan.status,
                'risk_score': last_scan.risk_score,
                'total_dependencies': last_scan.total_dependencies,
                'created_at': last_scan.created_at.isoformat()
            } if last_scan else None
        })
    return jsonify({'projects': result})

@project_bp.route('/upload-zip', methods=['POST'])
@token_required
@limiter.limit("20 per minute")
def upload_zip_project():
    """Handles ZIP archive upload, creates Project & Scan, triggers background analysis."""
    user = g.current_user
    if 'file' not in request.files:
        return jsonify({'error': 'No zip file provided in upload.'}), 400

    file = request.files['file']
    project_name = request.form.get('project_name', '').strip() or file.filename.rsplit('.', 1)[0]
    deployment_model = request.form.get('deployment_model', 'HOSTED').strip()

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a .zip archive.'}), 400

    # Save temp zip file
    extract_dir = create_temp_extract_dir()
    zip_path = os.path.join(extract_dir, 'upload.zip')
    file.save(zip_path)

    try:
        safe_extract_zip(zip_path, extract_dir)
        if os.path.exists(zip_path):
            os.remove(zip_path)  # Delete raw zip file immediately after parsing
    except ValueError as err:
        return jsonify({'error': str(err)}), 400

    # Create DB records
    project = Project(user_id=user.id, name=project_name)
    db.session.add(project)
    db.session.commit()

    upload = Upload(
        project_id=project.id,
        filename=file.filename,
        upload_type='zip',
        file_size=get_dir_size(extract_dir)
    )
    db.session.add(upload)

    scan = Scan(project_id=project.id, user_id=user.id, status='QUEUED', deployment_model=deployment_model)
    db.session.add(scan)
    db.session.commit()

    # Trigger background worker scan pipeline
    trigger_scan_task(current_app._get_current_object(), scan.id, extract_dir)

    return jsonify({
        'message': 'Zip file uploaded and scan queued successfully.',
        'project_id': project.id,
        'scan_id': scan.id
    }), 201

@project_bp.route('/upload-github', methods=['POST'])
@token_required
@limiter.limit("20 per minute")
def upload_github_project():
    """Handles GitHub repository URL upload, fetches manifest files safely, queues scan."""
    user = g.current_user
    data = request.get_json() or {}
    github_url = data.get('github_url', '').strip()
    project_name = data.get('project_name', '').strip()
    deployment_model = data.get('deployment_model', 'HOSTED').strip()

    if not github_url:
        return jsonify({'error': 'GitHub repository URL is required.'}), 400

    if not project_name:
        parts = github_url.rstrip('/').split('/')
        project_name = parts[-1] if len(parts) > 0 else 'GitHub Project'

    extract_dir = create_temp_extract_dir()

    try:
        fetch_github_manifests(github_url, extract_dir)
    except ValueError as err:
        return jsonify({'error': str(err)}), 400

    project = Project(user_id=user.id, name=project_name, repository_url=github_url)
    db.session.add(project)
    db.session.commit()

    upload = Upload(project_id=project.id, filename='github_repo', upload_type='github')
    db.session.add(upload)

    scan = Scan(project_id=project.id, user_id=user.id, status='QUEUED', deployment_model=deployment_model)
    db.session.add(scan)
    db.session.commit()

    trigger_scan_task(current_app._get_current_object(), scan.id, extract_dir)

    return jsonify({
        'message': 'GitHub repository fetched and scan queued successfully.',
        'project_id': project.id,
        'scan_id': scan.id
    }), 201

@project_bp.route('/upload-manifests', methods=['POST'])
@token_required
@limiter.limit("20 per minute")
def upload_manifests_project():
    """Handles upload of individual or multiple manifest/lock files."""
    user = g.current_user
    files = request.files.getlist('files')
    project_name = request.form.get('project_name', '').strip() or 'Manifest Project'
    deployment_model = request.form.get('deployment_model', 'HOSTED').strip()

    if not files:
        return jsonify({'error': 'No manifest or lock files uploaded.'}), 400

    extract_dir = create_temp_extract_dir()

    for file in files:
        if file and allowed_file(file.filename):
            safe_name = werkzeug.utils.secure_filename(file.filename) or file.filename
            save_path = os.path.join(extract_dir, safe_name)
            file.save(save_path)

    project = Project(user_id=user.id, name=project_name)
    db.session.add(project)
    db.session.commit()

    upload = Upload(project_id=project.id, filename=f"{len(files)} files", upload_type='manifests')
    db.session.add(upload)

    scan = Scan(project_id=project.id, user_id=user.id, status='QUEUED', deployment_model=deployment_model)
    db.session.add(scan)
    db.session.commit()

    trigger_scan_task(current_app._get_current_object(), scan.id, extract_dir)

    return jsonify({
        'message': 'Manifest files uploaded and scan queued successfully.',
        'project_id': project.id,
        'scan_id': scan.id
    }), 201
