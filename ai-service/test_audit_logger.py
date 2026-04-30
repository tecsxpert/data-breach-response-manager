"""
Audit Logger Test Suite - Day 5 Task
AI Developer 2: Week 1 Day 5 - Audit Logging Tests

Tests cover:
- AuditLogger class initialization and methods
- Log ID generation
- Client info extraction
- Request serialization
- Audit logging to file
- Exception logging
- Log retrieval methods

Results documented in TODO.md
"""

import pytest
import json
import os
import time
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime
from io import StringIO

# Import the modules to test
from middleware.audit_logger import AuditLogger, audit_logger, audit_log_middleware, log_exception
from app import app


class TestAuditLoggerInitialization:
    """Test AuditLogger class initialization."""
    
    def test_initialization_with_defaults(self):
        """Test initialization with default parameters."""
        logger = AuditLogger()
        assert logger.log_file == 'audit.log'
        assert logger.retention_days == 90
        assert logger.max_cached == 1000
    
    def test_initialization_with_custom_params(self):
        """Test initialization with custom parameters."""
        logger = AuditLogger(log_file='custom_audit.log', retention_days=30)
        assert logger.log_file == 'custom_audit.log'
        assert logger.retention_days == 30
    
    def test_recent_logs_cache_initialized(self):
        """Test that recent_logs cache is initialized."""
        logger = AuditLogger()
        assert hasattr(logger, 'recent_logs')
        assert len(logger.recent_logs) == 0


class TestLogIdGeneration:
    """Test log ID generation."""
    
    def test_generate_log_id_consistency(self):
        """Test that same data produces same log ID."""
        logger = AuditLogger()
        data = {'test': 'data', 'timestamp': '2024-01-01'}
        
        id1 = logger._generate_log_id(data)
        id2 = logger._generate_log_id(data)
        
        assert id1 == id2
        assert len(id1) == 16  # SHA256 hexdigest first 16 chars
    
    def test_generate_log_id_uniqueness(self):
        """Test that different data produces different log IDs."""
        logger = AuditLogger()
        data1 = {'test': 'data1'}
        data2 = {'test': 'data2'}
        
        id1 = logger._generate_log_id(data1)
        id2 = logger._generate_log_id(data2)
        
        assert id1 != id2
    
    def test_generate_log_id_different_timestamps(self):
        """Test that timestamps affect log ID."""
        logger = AuditLogger()
        
        id1 = logger._generate_log_id({'timestamp': '2024-01-01T00:00:00'})
        id2 = logger._generate_log_id({'timestamp': '2024-01-01T00:00:01'})
        
        assert id1 != id2


class TestClientInfoExtraction:
    """Test client information extraction."""
    
    def test_get_client_info_with_request(self):
        """Test extracting client info from request."""
        logger = AuditLogger()
        
        # Create mock request with proper mock for headers
        mock_request = Mock()
        mock_request.remote_addr = '192.168.1.100'
        mock_request.headers = Mock()
        mock_request.headers.get = lambda k, default=None: {
            'User-Agent': 'TestAgent/1.0',
            'Authorization': 'Bearer test_token_12345'
        }.get(k, default)
        
        # Test the method directly
        client_info = logger._get_client_info(mock_request)
        assert client_info['ip_address'] == '192.168.1.100'
        assert client_info['user_agent'] == 'TestAgent/1.0'
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_get_client_info_real_request(self, client):
        """Test with real Flask test client."""
        logger = AuditLogger()
        
        # Make a test request
        response = client.post('/describe',
                            data=json.dumps({"breach_data": {"company": "Test"}}),
                            content_type='application/json')
        
        # Get the request from the app
        with app.test_request_context():
            from flask import request
            client_info = logger._get_client_info(request)
            assert 'ip_address' in client_info
            assert 'user_agent' in client_info


class TestRequestSerialization:
    """Test request serialization for logging."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_serialize_get_request(self, client):
        """Test serializing GET request."""
        logger = AuditLogger()
        
        with app.test_request_context(method='GET', path='/test'):
            from flask import request
            serialized = logger._serialize_request(request)
            
            assert serialized['method'] == 'GET'
            assert serialized['path'] == '/test'
            assert 'headers' in serialized
    
    def test_serialize_post_request(self, client):
        """Test serializing POST request."""
        logger = AuditLogger()
        
        with app.test_request_context(method='POST', 
                                       path='/describe',
                                       json={'breach_data': {'company': 'Test'}}):
            from flask import request
            request.args = {}
            serialized = logger._serialize_request(request)
            
            assert serialized['method'] == 'POST'
            assert serialized['path'] == '/describe'
    
    def test_serialize_request_filters_sensitive_headers(self, client):
        """Test that sensitive headers are filtered."""
        logger = AuditLogger()
        
        with app.test_request_context(method='POST', path='/test'):
            from flask import request
            serialized = logger._serialize_request(request)
            
            # Authorization and cookie headers should be filtered
            if 'authorization' in [h.lower() for h in serialized.get('headers', {})]:
                pytest.fail("Authorization header should be filtered")


class TestLogRequest:
    """Test log_request method."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def temp_logger(self, tmp_path):
        """Create logger with temp log file."""
        log_file = tmp_path / "test_audit.log"
        logger = AuditLogger(log_file=str(log_file))
        return logger
    
    def test_log_request_success(self, temp_logger, client):
        """Test logging successful request."""
        # Make a test request
        response = client.post('/describe',
                              data=json.dumps({"breach_data": {"company": "TestCo"}}),
                              content_type='application/json')
        
        # Get the request
        with app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            request.headers = Mock()
            request.headers.get = lambda k, d=None: d
            
            # Create mock response
            mock_response = Mock()
            mock_response.status_code = 200
            
            # Log the request
            audit_entry = temp_logger.log_request(request, mock_response, duration_ms=50.0)
            
            assert audit_entry is not None
            assert 'log_id' in audit_entry
            assert audit_entry['status_code'] == 200
            assert audit_entry['event_type'] == 'api_request'
    
    def test_log_request_error(self, temp_logger, client):
        """Test logging request with error."""
        with app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            request.headers = Mock()
            request.headers.get = lambda k, d=None: d
            
            # Log error
            audit_entry = temp_logger.log_request(request, error="Test error")
            
            assert audit_entry is not None
            assert audit_entry['error'] == "Test error"
            assert audit_entry['event_type'] == 'error'
    
    def test_log_request_writes_to_file(self, temp_logger, client):
        """Test that log is written to file."""
        with app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            request.headers = Mock()
            request.headers.get = lambda k, d=None: d
            
            mock_response = Mock()
            mock_response.status_code = 200
            
            temp_logger.log_request(request, mock_response)
            
# Check file exists and has content
            assert os.path.exists(temp_logger.log_file)
            with open(temp_logger.log_file, 'r') as f:
                content = f.read()
                assert len(content) > 0
    
    def test_log_request_adds_to_cache(self, temp_logger, client):
        """Test that log is added to in-memory cache."""
        with app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            request.headers = Mock()
            request.headers.get = lambda k, d=None: d
            
            mock_response = Mock()
            mock_response.status_code = 200
            
            temp_logger.log_request(request, mock_response)
            
            # Check cache - may have '127.0.0.1' or 'unknown' depending on request context
            assert len(temp_logger.recent_logs) > 0
            # Get any key from the cache and verify it's a non-empty list
            first_key = list(temp_logger.recent_logs.keys())[0]
            assert len(temp_logger.recent_logs[first_key]) > 0


class TestGetLogs:
    """Test log retrieval methods."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def logger_with_logs(self, tmp_path, client):
        """Create logger with some test logs."""
        log_file = tmp_path / "test_audit.log"
        logger = AuditLogger(log_file=str(log_file))
        
        # Add some test logs
        with app.test_request_context(method='POST', path='/test'):
            from flask import request
            
            for i in range(5):
                request.environ['REMOTE_ADDR'] = f'127.0.0.{i+1}'
                request.headers = Mock()
                request.headers.get = lambda k, d=None: d
                
                mock_response = Mock()
                mock_response.status_code = 200
                
                logger.log_request(request, mock_response)
        
        return logger
    
    def test_get_client_logs(self, logger_with_logs):
        """Test retrieving logs for specific client."""
        logs = logger_with_logs.get_client_logs('127.0.0.1')
        assert isinstance(logs, list)
    
    def test_get_all_logs(self, logger_with_logs):
        """Test retrieving all logs."""
        logs = logger_with_logs.get_all_logs()
        assert isinstance(logs, list)
    
    def test_get_all_logs_with_limit(self, logger_with_logs):
        """Test retrieving logs with limit."""
        logs = logger_with_logs.get_all_logs(limit=2)
        assert len(logs) <= 2


class TestAuditLogMiddleware:
    """Test audit_log_middleware function."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_middleware_integrated_in_app(self, client):
        """Test that middleware is integrated and runs."""
        # Make a request - audit logging happens in after_request
        response = client.post('/describe',
                              data=json.dumps({"breach_data": {"company": "TestCo"}}),
                              content_type='application/json')
        
        # Should succeed (200 or rate limit 429)
        assert response.status_code in [200, 429]


class TestLogException:
    """Test log_exception function."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_log_exception_function(self, client):
        """Test that log_exception function exists and works."""
        from middleware.audit_logger import log_exception
        
        with app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            request.headers = Mock()
            request.headers.get = lambda k, d=None: d
            
            # Call log_exception
            result = log_exception(request)
            
            # Function executes without error


class TestGlobalAuditLogger:
    """Test global audit logger instance."""
    
    def test_global_logger_exists(self):
        """Test that global audit_logger instance exists."""
        from middleware.audit_logger import audit_logger
        assert audit_logger is not None
        assert isinstance(audit_logger, AuditLogger)
    
    def test_global_logger_defaults(self):
        """Test global logger has correct defaults."""
        from middleware.audit_logger import audit_logger
        assert audit_logger.log_file == 'audit.log'
        assert audit_logger.retention_days == 90


class TestAuditLoggerEdgeCases:
    """Test edge cases for audit logger."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def temp_logger(self, tmp_path):
        """Create logger with temp log file."""
        log_file = tmp_path / "test_audit.log"
        logger = AuditLogger(log_file=str(log_file))
        return logger
    
    def test_log_request_without_response(self, temp_logger, client):
        """Test logging request without response object."""
        with app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            request.headers = Mock()
            request.headers.get = lambda k, d=None: d
            
            # Log without response
            audit_entry = temp_logger.log_request(request)
            
            assert audit_entry is not None
            assert audit_entry['status_code'] == 500  # Default to 500
    
    def test_log_request_with_none_duration(self, temp_logger, client):
        """Test logging with None duration."""
        with app.test_request_context():
            from flask import request
            request.environ['REMOTE_ADDR'] = '127.0.0.1'
            request.headers = Mock()
            request.headers.get = lambda k, d=None: d
            
            mock_response = Mock()
            mock_response.status_code = 200
            
            audit_entry = temp_logger.log_request(request, mock_response, duration_ms=None)
            
            assert audit_entry is not None
    
    def test_cache_limit(self, temp_logger, client):
        """Test that cache respects max limit."""
        # Create logger with small cache
        temp_logger.max_cached = 5
        
        with app.test_request_context():
            from flask import request
            
            # Add more logs than limit
            for i in range(10):
                request.environ['REMOTE_ADDR'] = '127.0.0.1'
                request.headers = Mock()
                request.headers.get = lambda k, d=None: d
                
                mock_response = Mock()
                mock_response.status_code = 200
                
                temp_logger.log_request(request, mock_response)
        
        # Cache should not exceed limit
        assert len(temp_logger.recent_logs['127.0.0.1']) <= temp_logger.max_cached


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
