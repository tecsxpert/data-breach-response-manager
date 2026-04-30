import time
import logging
from typing import Dict, Tuple
from collections import defaultdict
from functools import wraps
from flask import Request, jsonify
from threading import Lock

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiting implementation."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
            requests_per_hour: Maximum requests allowed per hour
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Track requests: {client_id: [(timestamp, count)]}
        self.clients: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
        
        # Cleanup old entries every 5 minutes
        self.last_cleanup = time.time()
        self.cleanup_interval = 300
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier from request."""
        # Use IP address + API key if available
        ip = request.remote_addr or 'unknown'
        api_key = request.headers.get('Authorization', '')
        return f"{ip}:{api_key}"
    
    def _cleanup_old_entries(self):
        """Remove entries older than 1 hour."""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        with self.lock:
            cutoff = current_time - 3600  # 1 hour ago
            for client_id in list(self.clients.keys()):
                self.clients[client_id] = [
                    entry for entry in self.clients[client_id]
                    if entry[0] > cutoff
                ]
                if not self.clients[client_id]:
                    del self.clients[client_id]
        
        self.last_cleanup = current_time
        logger.info("Rate limiter cleanup completed")
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, dict]:
        """
        Check if request is within rate limits.
        
        Args:
            request: Flask request object
            
        Returns:
            Tuple of (is_allowed, limit_info)
        """
        self._cleanup_old_entries()
        
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        with self.lock:
            # Get recent requests
            recent = self.clients[client_id]
            minute_cutoff = current_time - 60
            hour_cutoff = current_time - 3600
            
            # Count requests in last minute and hour
            requests_last_minute = sum(1 for t, _ in recent if t > minute_cutoff)
            requests_last_hour = sum(1 for t, _ in recent if t > hour_cutoff)
            
            # Check limits
            if requests_last_minute >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded (per minute) for {client_id}")
                return False, {
                    'limit': self.requests_per_minute,
                    'remaining': 0,
                    'reset': int(min(recent[-1][0] if recent else current_time, current_time) + 60)
                }
            
            if requests_last_hour >= self.requests_per_hour:
                logger.warning(f"Rate limit exceeded (per hour) for {client_id}")
                return False, {
                    'limit': self.requests_per_hour,
                    'remaining': 0,
                    'reset': int(min(recent[-1][0] if recent else current_time, current_time) + 3600)
                }
            
            # Record this request
            self.clients[client_id].append((current_time, 1))
            
            return True, {
                'limit': self.requests_per_minute,
                'remaining': self.requests_per_minute - requests_last_minute - 1,
                'reset': int(current_time + 60)
            }
    
    def get_rate_limit_headers(self, limit_info: dict) -> Dict[str, str]:
        """
        Get rate limit headers for response.
        
        Args:
            limit_info: Limit information from check_rate_limit
            
        Returns:
            Dictionary of headers
        """
        return {
            'X-RateLimit-Limit': str(limit_info['limit']),
            'X-RateLimit-Remaining': str(limit_info['remaining']),
            'X-RateLimit-Reset': str(limit_info['reset'])
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)


def rate_limit_middleware(request: Request):
    """
    Flask middleware for rate limiting.
    
    Usage:
        @app.before_request
        def rate_limit():
            return rate_limit_middleware(request)
    """
    try:
        is_allowed, limit_info = rate_limiter.check_rate_limit(request)
        
        if not is_allowed:
            response = jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': limit_info['reset'] - int(time.time())
            })
            response.status_code = 429
            for header, value in rate_limiter.get_rate_limit_headers(limit_info).items():
                response.headers[header] = value
            response.headers['Retry-After'] = str(limit_info['reset'] - int(time.time()))
            return response
        
        # Store limit info for response headers
        request._rate_limit_info = limit_info
        
    except Exception as e:
        logger.error(f"Rate limit error: {str(e)}")
        # Allow request on error


def add_rate_limit_headers(response):
    """
    Add rate limit headers to response.
    
    Usage:
        @app.after_request
        def add_headers(response):
            return add_rate_limit_headers(response)
    """
    from flask import request
    limit_info = getattr(request, '_rate_limit_info', None)
    if limit_info:
        for header, value in rate_limiter.get_rate_limit_headers(limit_info).items():
            response.headers[header] = value
    return response
