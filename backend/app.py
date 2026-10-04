import os
from flask import Flask, jsonify, request, send_from_directory
from backend.config import Config
from backend.extensions import db, migrate, mail, limiter, cors
from backend.routes.auth_routes import auth_bp
from backend.routes.project_routes import project_bp
from backend.routes.scan_routes import scan_bp
from backend.routes.contact_routes import contact_bp

def create_app(config_class=Config):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(__name__, static_folder=root_dir, static_url_path='')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(contact_bp)

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: http: data: blob:;"
        return response

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'Deptrix API', 'version': '1.0.0'})

    # Serve static frontend root
    @app.route('/')
    def index():
        return send_from_directory(root_dir, 'index.html')

    @app.route('/<path:path>')
    def catch_all(path):
        if os.path.exists(os.path.join(root_dir, path)):
            return send_from_directory(root_dir, path)
        return send_from_directory(root_dir, 'index.html')

    # Create tables automatically for local SQLite/Postgres dev setup
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
