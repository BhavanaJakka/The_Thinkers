import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'diptrix-dev-super-secret-key-32bytes-min!')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'diptrix-jwt-dev-secret-key-998877!')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # DB fallback to SQLite if PostgreSQL connection fails or not specified in dev/test
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///diptrix.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Flask-Mail config
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@diptrix.local')
    
    CORS_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')]
    
    # Upload limits
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
