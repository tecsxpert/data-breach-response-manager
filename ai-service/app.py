from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.groq_client import GroqClient
from middleware.input_sanitizer import sanitize_input_middleware
from middleware.rate_limiter import rate_limit_middleware, add_rate_limit_headers
from middleware.audit_logger import audit_log_middleware
from dotenv import load_dotenv
import os
import time

load_dotenv()

app = Flask(__name__)

# Initialize Flask-Limiter with 30 requests per minute
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["30 per minute"],
    storage_uri="memory://"
)

groq_client = GroqClient(api_key=os.getenv('GROQ_API_KEY'))

@app.before_request
def before_request():
    """Apply input sanitization and rate limiting middleware to all requests."""
    request._start_time = time.time()
    if request.method == 'POST' and request.endpoint:
        # Rate limiting check
        result = rate_limit_middleware(request)
        if result:
            return result
        # Input sanitization check
        result = sanitize_input_middleware(request)
        if result:
            return result

@app.after_request
def after_request(response):
    """Add rate limit headers to response."""
    # Audit logging
    try:
        duration_ms = None
        if hasattr(request, '_start_time'):
            duration_ms = (time.time() - request._start_time) * 1000
        audit_log_middleware(request, response, duration_ms=duration_ms)
    except Exception as e:
        app.logger.error(f"Audit logging error: {str(e)}")
    
    return add_rate_limit_headers(response)

@app.route('/describe', methods=['POST'])
def describe_breach():
    data = getattr(request, '_sanitized_json', request.json)
    
    # Validate required field
    if not data or 'breach_data' not in data:
        return jsonify({'error': 'Missing required field: breach_data'}), 400
    
    response = groq_client.describe_breach(data['breach_data'])
    return jsonify({'analysis': response})

@app.errorhandler(Exception)
def handle_error(e):
    """Handle errors and log exceptions."""
    from middleware.audit_logger import log_exception
    log_exception(request)
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

