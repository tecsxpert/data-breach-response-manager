import re
import html
import logging
from typing import Any, Dict, Optional, Tuple
from flask import Request, jsonify

logger = logging.getLogger(__name__)

class InputSanitizer:
    """Middleware for sanitizing user input to prevent XSS and injection attacks."""
    
    # Patterns for potentially dangerous input (XSS)
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<\w+[^>]*\s+on\w+\s*=',
    ]
    
    # Prompt injection patterns for AI safety
    PROMPT_INJECTION_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'ignore\s+all\s+previous\s+rules',
        r'disregard\s+your\s+(system\s+)?instructions',
        r'forget\s+everything\s+(you|I)\s+(told|said)',
        r'you\s+are\s+now\s+(a|an)\s+\[.*?\]',
        r'pretend\s+to\s+be\s+(a|an)\s+\[',
        r'system:\s*',
        r'always\s+respond\s+as\s+if',
        r'new\s+system\s+prompt',
        r'override\s+(your\s+)?(safety|guidelines)',
        r'bypass\s+(your\s+)?restrictions',
        r'<\|system\|>',
        r'<\|user\|>',
        r'<\|assistant\|>',
    ]
    
    # Compile patterns for efficiency
    COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in DANGEROUS_PATTERNS]
    COMPILED_PROMPT_INJECTION_PATTERNS = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in PROMPT_INJECTION_PATTERNS]
    
    @staticmethod
    def sanitize_request(request: Request) -> Dict[str, Any]:
        """Sanitize all input data from request."""
        if not request.is_json:
            logger.warning("Non-JSON request received")
            return {}
        
        data = request.get_json()
        if not data:
            return {}
        
        sanitized = InputSanitizer.sanitize_dict(data)
        
        if sanitized != data:
            logger.info("Input data was sanitized")
        
        return sanitized
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary values."""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [InputSanitizer.sanitize_dict(item) if isinstance(item, dict) 
                                 else InputSanitizer.sanitize_string(item) if isinstance(item, str) 
                                 else item 
                                 for item in value]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize a string value by removing dangerous patterns and HTML escaping."""
        if not isinstance(value, str):
            return value
        
        # Remove dangerous patterns
        sanitized = value
        for pattern in InputSanitizer.COMPILED_PATTERNS:
            sanitized = pattern.sub('', sanitized)
        
        # Strip HTML tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # HTML escape remaining content
        sanitized = html.escape(sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    @staticmethod
    def contains_dangerous_content(data: Dict[str, Any]) -> bool:
        """Check if data contains dangerous content."""
        def check_value(value: Any) -> bool:
            if isinstance(value, str):
                for pattern in InputSanitizer.COMPILED_PATTERNS:
                    if pattern.search(value):
                        return True
            elif isinstance(value, dict):
                for v in value.values():
                    if check_value(v):
                        return True
            elif isinstance(value, list):
                for item in value:
                    if check_value(item):
                        return True
            return False
        
        return check_value(data)
    
    @staticmethod
    def contains_prompt_injection(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check if data contains prompt injection patterns."""
        def check_value(value: Any) -> Tuple[bool, Optional[str]]:
            if isinstance(value, str):
                for pattern in InputSanitizer.COMPILED_PROMPT_INJECTION_PATTERNS:
                    match = pattern.search(value)
                    if match:
                        return True, pattern.pattern
            elif isinstance(value, dict):
                for v in value.values():
                    result, matched = check_value(v)
                    if result:
                        return result, matched
            elif isinstance(value, list):
                for item in value:
                    result, matched = check_value(item)
                    if result:
                        return result, matched
            return False, None
        
        return check_value(data)


def sanitize_input_middleware(request: Request):
    """Flask middleware decorator for input sanitization."""
    try:
        data = request.get_json() if request.is_json else {}
        
        # Check for prompt injection first - return 400 if detected
        has_injection, matched = InputSanitizer.contains_prompt_injection(data)
        if has_injection:
            logger.warning(f"Prompt injection detected: {matched}")
            return jsonify({'error': 'Potential prompt injection detected'}), 400
        
        # Check for dangerous content - return 400 if detected
        if InputSanitizer.contains_dangerous_content(data):
            logger.warning("Dangerous content detected")
            return jsonify({'error': 'Dangerous content detected'}), 400
        
        # Sanitize the input
        sanitized = InputSanitizer.sanitize_request(request)
        request._sanitized_json = sanitized
    except Exception as e:
        logger.error(f"Sanitization error: {str(e)}")
        return jsonify({'error': 'Invalid input'}), 400
