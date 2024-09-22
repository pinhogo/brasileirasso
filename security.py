from functools import wraps
from flask import request, jsonify
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv('API_KEY', 'sua_chave_secreta')


def require_api_key(protected_methods=None):
    if protected_methods is None:
        protected_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.method.upper() in protected_methods:
                api_key = request.headers.get('x-api-key')
                if not api_key:
                    return jsonify({"error": "API key missing"}), 401
                if api_key != API_KEY:
                    return jsonify({"error": "Invalid API key"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator