import time
import json
import logging
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from flask import Request, Response
from functools import wraps
from collections import defaultdict

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logging for security compliance and incident response."""
    
    def __init__(self, log_file: str = 'audit.log', retention_days: int = 90):
        """
        Initialize audit logger.
        
        Args:
            log_file: Path to audit log file
            retention_days: Days to retain logs
        """
        self.log_file = log_file
        self.retention_days = retention_days
        
        # In-memory cache for recent logs (for fast lookup)
        self.recent_logs = defaultdict(list)
        self.max_cached = 1000
    
    def _generate_log_id(self, data: Dict[str, Any]) -> str:
        """Generate unique audit log ID."""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _get_client_info(self, request: Request) -> Dict[str, str]:
        """Extract client information from request."""
        return {
            'ip_address': request.remote_addr or 'unknown',
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'api_key': request.headers.get('Authorization', 'none')[:20] + '...' if request.headers.get('Authorization') else 'none'
        }
    
    def _serialize_request(self, request: Request) -> Dict[str, Any]:
        """Serialize request data for logging."""
        return {
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint,
            'args': dict(request.args) if request.args else {},
            'headers': {k: v for k, v in request.headers if k.lower() not in ['authorization', 'cookie']}
        }
    
    def log_request(self, request: Request, response: Optional[Response] = None, 
                 error: Optional[str] = None, duration_ms: Optional[float] = None):
        """
        Log an API request for audit trail.
        
        Args:
            request: Flask request object
            response: Flask response object (optional)
            error: Error message if request failed
            duration_ms: Request processing duration in milliseconds
        """
        timestamp = datetime.now().isoformat()
        
        client_info = self._get_client_info(request)
        
        audit_entry = {
            'timestamp': timestamp,
            'event_type': 'error' if error else 'api_request',
            'method': request.method,
            'path': request.path,
            'client_ip': client_info['ip_address'],
            'user_agent': client_info['user_agent'],
            'api_key_hash': hashlib.sha256(client_info['api_key'].encode()).hexdigest()[:8],
            'status_code': response.status_code if response else 500,
            'error': error,
            'duration_ms': duration_ms
        }
        
        # Add to recent logs cache
        log_id = self._generate_log_id(audit_entry)
        audit_entry['log_id'] = log_id
        
        self.recent_logs[client_info['ip_address']].append(audit_entry)
        
        # Trim cache if needed
        if len(self.recent_logs[client_info['ip_address']]) > self.max_cached:
            self.recent_logs[client_info['ip_address']] = self.recent_logs[client_info['ip_address']][-self.max_cached:]
        
        # Log to file
        log_line = json.dumps(audit_entry)
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_line + '\n')
            logger.info(f"Audit log written: {log_id}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {str(e)}")
        
        return audit_entry
    
    def get_client_logs(self, client_ip: str, limit: int = 100) -> list:
        """
        Get recent logs for a specific client.
        
        Args:
            client_ip: Client IP address
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log entries
        """
        return self.recent_logs.get(client_ip, [])[-limit:]
    
    def get_all_logs(self, limit: int = 100) -> list:
        """
        Get all recent logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of audit log entries
        """
        all_logs = []
        for logs in self.recent_logs.values():
            all_logs.extend(logs)
        
        all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_logs[:limit]


# Global audit logger instance
audit_logger = AuditLogger(log_file='audit.log', retention_days=90)


def audit_log_middleware(request: Request, response: Optional[Response] = None, 
                       error: Optional[str] = None):
    """
    Flask middleware for audit logging.
    
    Usage:
        @app.before_request
        def before_request():
            request._start_time = time.time()
        
        @app.after_request
        def after_request(response):
            duration = (time.time() - request._start_time) * 1000
            return audit_log_middleware(request, response, duration_ms=duration)
    """
    try:
        # Get duration if available
        duration_ms = getattr(request, '_start_time', None)
        if duration_ms:
            duration_ms = (time.time() - duration_ms) * 1000
        
        audit_logger.log_request(request, response, error, duration_ms)
        
    except Exception as e:
        logger.error(f"Audit logging error: {str(e)}")


def log_exception(request: Request, exception: Exception = None):
    """
    Log an exception.
    
    Args:
        request: Flask request object
        exception: The exception that occurred (optional)
    
    Usage:
        @app.errorhandler(Exception)
        def handle_error(e):
            log_exception(request, e)
            return jsonify({'error': str(e)}), 500
    """
    error_msg = str(exception) if exception else "Unknown error"
    audit_logger.log_request(request, error=error_msg)
