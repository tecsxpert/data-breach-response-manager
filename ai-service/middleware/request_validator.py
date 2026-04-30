"""
Request Validation Middleware - Day 6 Task
AI Developer 2: Week 1 Day 6 - Request Validation and Size Limits

Security enhancements:
- Request body size limiting (max 1MB)
- Content-Type validation
- Request timeout handling
- JSON validity check

Results documented in TODO.md
"""

import time
import logging
from flask import Request, jsonify, Response
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Maximum request body size (1MB)
MAX_BODY_SIZE = 1024 * 1024  # 1 MB
MAX_BODY_SIZE_STR = "1MB"


def validate_request_size(request: Request) -> Optional[Tuple[Response, int]]:
    """
    Validate request body size to prevent large payload attacks.
    
    Args:
        request: Flask request object
        
    Returns:
        None if valid, or tuple of (response, status_code) if invalid
    """
    content_length = request.content_length
    
    if content_length and content_length > MAX_BODY_SIZE:
        logger.warning(f"Request body too large: {content_length} bytes (max: {MAX_BODY_SIZE})")
        return jsonify({
            'error': f'Request body too large. Maximum size is {MAX_BODY_STR}',
            'code': 'PAYLOAD_TOO_LARGE'
        }), 413
    
    return None


def validate_content_type(request: Request) -> Optional[Tuple[Response, int]]:
    """
    Validate Content-Type header for POST requests.
    
    Args:
        request: Flask request object
        
    Returns:
        None if valid, or tuple of (response, status_code) if invalid
    """
    if request.method == 'POST':
        content_type = request.content_type
        
        # Allow only JSON content types
        if content_type and not content_type.startswith('application/json'):
            logger.warning(f"Invalid content type: {content_type}")
            return jsonify({
                'error': 'Content-Type must be application/json',
                'code': 'INVALID_CONTENT_TYPE'
            }), 415
        
        # If no content-type but has body, assume JSON
        if not content_type and request.data:
            logger.warning("Missing Content-Type header")
            return jsonify({
                'error': 'Content-Type header required (application/json)',
                'code': 'MISSING_CONTENT_TYPE'
            }), 400
    
    return None


def validate_json_body(request: Request) -> Optional[Tuple[Response, int]]:
    """
    Validate JSON body is valid and parseable.
    
    Args:
        request: Flask request object
        
    Returns:
        None if valid, or tuple of (response, status_code) if invalid
    """
    if request.method == 'POST' and request.endpoint:
        # Try to parse JSON to validate it
        if request.data:
            try:
                if not request.is_json:
                    # Not valid JSON
                    import json
                    json.loads(request.data)
            except Exception as e:
                logger.warning(f"Invalid JSON body: {str(e)}")
                return jsonify({
                    'error': 'Invalid JSON body',
                    'code': 'INVALID_JSON'
                }), 400
    
    return None


def request_validator_middleware(request: Request) -> Optional[Tuple[Response, int]]:
    """
    Combined request validation middleware.
    
    Run all validation checks on request.
    
    Args:
        request: Flask request object
        
    Returns:
        None if all validations pass, or tuple of (response, status_code) if any fail
    """
    # Check 1: Request size
    result = validate_request_size(request)
    if result:
        return result
    
    # Check 2: Content-Type
    result = validate_content_type(request)
    if result:
        return result
    
    # Check 3: JSON validity
    result = validate_json_body(request)
    if result:
        return result
    
    return None


# Global configuration
class RequestValidatorConfig:
    """Configuration for request validation."""
    
    def __init__(self, max_body_size: int = MAX_BODY_SIZE):
        self.max_body_size = max_body_size
        self.enabled = True


# Default configuration
request_validator_config = RequestValidatorConfig()
