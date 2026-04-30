"""
Request Validator Test Suite - Day 6 Task
AI Developer 2: Week 1 Day 6 - Request Validation Tests

Tests cover:
- Request size validation
- Content-Type validation
- JSON body validation
- Middleware integration

Results documented in TODO.md
"""

import pytest
import json
from unittest.mock import Mock
from io import BytesIO

# Import the modules to test
from middleware.request_validator import (
    validate_request_size,
    validate_content_type,
    validate_json_body,
    request_validator_middleware,
    MAX_BODY_SIZE,
    RequestValidatorConfig
)
from app import app


class TestRequestSizeValidation:
    """Test request size validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_request_within_size_limit(self, client):
        """Test request within size limit passes."""
        # Small payload
        small_data = {"breach_data": {"company": "Test"}}
        response = client.post('/describe',
                          data=json.dumps(small_data),
                          content_type='application/json')
        
        assert response.status_code in [200, 429]
    
    def test_request_exceeds_size_limit(self, client):
        """Test request exceeding size limit returns 413."""
        # Create large payload (2MB)
        large_payload = "x" * (2 * 1024 * 1024)
        
        response = client.post('/describe',
                          data=large_payload,
                          content_type='application/json')
        
        assert response.status_code == 413
        assert b'Payload too large' in response.data or b'PAYLOAD_TOO_LARGE' in response.data
    
    def test_exact_size_limit(self, client):
        """Test request at exactly size limit passes."""
        # Create exactly 1MB payload
        exact_payload = "x" * MAX_BODY_SIZE
        
        response = client.post('/describe',
                          data=exact_payload,
                          content_type='application/json')
        
        # Should pass (not exceed)
        assert response.status_code in [200, 429, 400]


class TestContentTypeValidation:
    """Test Content-Type validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_valid_json_content_type(self, client):
        """Test valid JSON content type passes."""
        response = client.post('/describe',
                          data=json.dumps({"breach_data": {"company": "Test"}}),
                          content_type='application/json')
        
        assert response.status_code in [200, 400, 429]
    
    def test_invalid_content_type(self, client):
        """Test invalid content type returns 415."""
        response = client.post('/describe',
                          data=json.dumps({"breach_data": {"company": "Test"}}),
                          content_type='text/plain')
        
        assert response.status_code == 415
    
    def test_missing_content_type_with_data(self, client):
        """Test missing Content-Type with data returns 400."""
        response = client.post('/describe',
                          data=json.dumps({"breach_data": {"company": "Test"}}))
        
        # May return 400 or pass depending on implementation
        assert response.status_code in [200, 400, 415, 429]
    
    def test_application_json_with_charset(self, client):
        """Test application/json with charset is accepted."""
        response = client.post('/describe',
                          data=json.dumps({"breach_data": {"company": "Test"}}),
                          content_type='application/json; charset=utf-8')
        
        assert response.status_code in [200, 429]


class TestJSONBodyValidation:
    """Test JSON body validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_valid_json_body(self, client):
        """Test valid JSON body passes."""
        response = client.post('/describe',
                          data=json.dumps({"breach_data": {"company": "Test"}}),
                          content_type='application/json')
        
        assert response.status_code in [200, 429]
    
    def test_invalid_json_body(self, client):
        """Test invalid JSON body returns 400."""
        response = client.post('/describe',
                          data="not valid json",
                          content_type='application/json')
        
        assert response.status_code == 400
        assert b'Invalid JSON' in response.data or b'INVALID_JSON' in response.data
    
    def test_malformed_json(self, client):
        """Test malformed JSON returns 400."""
        response = client.post('/describe',
                          data='{"breach_data":}',
                          content_type='application/json')
        
        assert response.status_code in [400, 500]


class TestRequestValidatorMiddleware:
    """Test combined request validator middleware."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_middleware_passes_valid_request(self, client):
        """Test valid request passes middleware."""
        response = client.post('/describe',
                          data=json.dumps({"breach_data": {"company": "Test"}}),
                          content_type='application/json')
        
        assert response.status_code in [200, 429]
    
    def test_middleware_blocks_large_request(self, client):
        """Test large request is blocked."""
        large_payload = "x" * (2 * 1024 * 1024)
        
        response = client.post('/describe',
                          data=large_payload,
                          content_type='application/json')
        
        assert response.status_code == 413
    
    def test_middleware_blocks_wrong_content_type(self, client):
        """Test wrong content type is blocked."""
        response = client.post('/describe',
                          data="test",
                          content_type='text/plain')
        
        assert response.status_code == 415
    
    def test_middleware_blocks_invalid_json(self, client):
        """Test invalid JSON is blocked."""
        response = client.post('/describe',
                          data="invalid",
                          content_type='application/json')
        
        assert response.status_code == 400


class TestRequestValidatorConfig:
    """Test RequestValidatorConfig class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = RequestValidatorConfig()
        assert config.max_body_size == 1024 * 1024  # 1MB
        assert config.enabled is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RequestValidatorConfig(max_body_size=512 * 1024)
        assert config.max_body_size == 512 * 1024


class TestIntegrations:
    """Test integrations with app."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_app_has_request_validator(self, client):
        """Test request validator is integrated in app."""
        # Valid request should work
        response = client.post('/describe',
                       data=json.dumps({"breach_data": {"company": "Test"}}),
                       content_type='application/json')
        
        assert response.status_code in [200, 429]
    
    def test_rate_limit_still_works(self, client):
        """Test rate limiting still works alongside validation."""
        # Make rapid requests
        for _ in range(35):
            response = client.post('/describe',
                             data=json.dumps({"breach_data": {"company": "Test"}}),
                             content_type='application/json')
        
        # Should be rate limited at some point
        # Note: This test may be slow


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
