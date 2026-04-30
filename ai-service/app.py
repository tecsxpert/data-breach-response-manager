from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.groq_client import GroqClient
from middleware.input_sanitizer import sanitize_input_middleware
from middleware.rate_limiter import rate_limit_middleware, add_rate_limit_headers
from dotenv import load_dotenv
import os

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
    if request.method == 'POST' and request.endpoint:
        # Rate limiting check
        result = rate_limit_middleware(request)
        if result:
            return result
        # Input sanitization check
        return sanitize_input_middleware(request)

@app.after_request
def after_request(response):
    """Add rate limit headers to response."""
    return add_rate_limit_headers(response)

@app.route('/describe', methods=['POST'])
def describe_breach():
    data = getattr(request, '_sanitized_json', request.json)
    response = groq_client.describe_breach(data['breach_data'])
    return jsonify({'analysis': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

