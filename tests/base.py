"""
Base test classes with common utilities and helpers.
"""
import json
from typing import Dict, Any, Optional


class BaseTestCase:
    """
    Base test case with common utilities for all tests.
    """
    
    def assert_success_response(self, response, status_code: int = 200):
        """Assert that response is successful with expected structure."""
        assert response.status_code == status_code
        data = response.get_json()
        assert data is not None
        assert data.get('success') is True
        return data
    
    def assert_error_response(self, response, status_code: int = 400):
        """Assert that response is an error with expected structure."""
        assert response.status_code == status_code
        data = response.get_json()
        assert data is not None
        assert data.get('success') is False
        assert 'error' in data
        return data
    
    def get_json_response(self, response) -> Dict[str, Any]:
        """Get JSON data from response."""
        assert response.content_type == 'application/json'
        return response.get_json()


class APITestCase(BaseTestCase):
    """Base class for API integration tests."""
    
    def make_request(
        self,
        client,
        method: str,
        url: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        query_string: Optional[Dict] = None
    ):
        """Make an HTTP request with common setup."""
        kwargs = {}
        
        if headers:
            kwargs['headers'] = headers
        
        if data:
            kwargs['data'] = json.dumps(data)
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Content-Type'] = 'application/json'
        
        if query_string:
            kwargs['query_string'] = query_string
        
        return client.open(url, method=method, **kwargs)
    
    def get(self, client, url: str, headers: Optional[Dict] = None, query_string: Optional[Dict] = None):
        """Make GET request."""
        return self.make_request(client, 'GET', url, headers=headers, query_string=query_string)
    
    def post(self, client, url: str, data: Dict, headers: Optional[Dict] = None):
        """Make POST request."""
        return self.make_request(client, 'POST', url, data=data, headers=headers)
    
    def put(self, client, url: str, data: Dict, headers: Optional[Dict] = None):
        """Make PUT request."""
        return self.make_request(client, 'PUT', url, data=data, headers=headers)
    
    def delete(self, client, url: str, headers: Optional[Dict] = None):
        """Make DELETE request."""
        return self.make_request(client, 'DELETE', url, headers=headers)
    
    def assert_pagination(self, data: Dict, expected_per_page: int = 10):
        """Assert that response contains valid pagination metadata."""
        assert 'pagination' in data
        pagination = data['pagination']
        
        assert 'page' in pagination
        assert 'per_page' in pagination
        assert 'total' in pagination
        assert 'pages' in pagination
        
        assert pagination['page'] > 0
        assert pagination['per_page'] == expected_per_page
        assert pagination['total'] >= 0
        assert pagination['pages'] >= 0


class IntegrationTestCase(APITestCase):
    """Base class for integration tests."""
    pass
