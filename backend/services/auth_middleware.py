from functools import wraps
from flask import request, jsonify, g
from backend.services.auth_service import decode_jwt_token
from backend.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check HTTP-only cookie first
        if 'access_token' in request.cookies:
            token = request.cookies.get('access_token')
        elif 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authentication token missing or invalid.'}), 401

        payload = decode_jwt_token(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({'error': 'Token is invalid or expired.'}), 401

        user = User.query.get(payload['sub'])
        if not user or user.is_locked:
            return jsonify({'error': 'User account not found or locked.'}), 403

        g.current_user = user
        return f(*args, **kwargs)
    return decorated
