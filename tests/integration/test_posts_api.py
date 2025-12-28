"""
Integration tests for Posts API endpoints.
These tests verify the existing API behavior before refactoring.
"""
import pytest
from tests.base import IntegrationTestCase


@pytest.mark.integration
class TestPostsAPI(IntegrationTestCase):
    """Test suite for Posts API endpoints."""
    
    def test_get_all_posts_empty(self, client, auth_headers):
        """Test getting posts when database is empty."""
        response = self.get(client, '/api/posts', headers=auth_headers)
        
        data = self.assert_success_response(response, 200)
        assert 'posts' in data
        assert isinstance(data['posts'], list)
        assert len(data['posts']) == 0
        self.assert_pagination(data)
    
    def test_get_all_posts_with_data(self, client, auth_headers, multiple_posts):
        """Test getting all posts with pagination."""
        response = self.get(client, '/api/posts', headers=auth_headers)
        
        data = self.assert_success_response(response, 200)
        assert 'posts' in data
        assert isinstance(data['posts'], list)
        assert len(data['posts']) == 5
        self.assert_pagination(data)
        
        # Verify post structure
        post = data['posts'][0]
        assert 'id' in post
        assert 'content' in post
        assert 'author_first_name' in post
        assert 'author_last_name' in post
        assert 'created_at' in post
    
    def test_get_posts_with_pagination(self, client, auth_headers, multiple_posts):
        """Test posts pagination parameters."""
        response = self.get(
            client, 
            '/api/posts',
            headers=auth_headers,
            query_string={'page': 1, 'per_page': 2}
        )
        
        data = self.assert_success_response(response, 200)
        assert len(data['posts']) == 2
        assert data['pagination']['per_page'] == 2
        assert data['pagination']['total'] == 5
        assert data['pagination']['pages'] == 3
    
    def test_get_posts_filter_by_user(self, client, auth_headers, sample_user, multiple_posts):
        """Test filtering posts by user_id."""
        response = self.get(
            client,
            '/api/posts',
            headers=auth_headers,
            query_string={'user_id': sample_user.id}
        )
        
        data = self.assert_success_response(response, 200)
        assert len(data['posts']) == 5
        
        # Verify all posts belong to the user
        for post in data['posts']:
            assert post['user_id'] == sample_user.id
    
    def test_get_posts_filter_by_type(self, client, auth_headers, multiple_posts):
        """Test filtering posts by type."""
        response = self.get(
            client,
            '/api/posts',
            headers=auth_headers,
            query_string={'type': 'professional'}
        )
        
        data = self.assert_success_response(response, 200)
        # Should have 3 professional posts (indices 0, 2, 4)
        assert len(data['posts']) == 3
    
    def test_get_posts_search(self, client, auth_headers, multiple_posts):
        """Test searching posts by content."""
        response = self.get(
            client,
            '/api/posts',
            headers=auth_headers,
            query_string={'search': 'number 2'}
        )
        
        data = self.assert_success_response(response, 200)
        assert len(data['posts']) == 1
        assert 'number 2' in data['posts'][0]['content']
    
    def test_get_single_post(self, client, auth_headers, sample_post):
        """Test getting a single post by ID."""
        response = self.get(
            client,
            f'/api/posts/{sample_post.id}',
            headers=auth_headers
        )
        
        data = self.assert_success_response(response, 200)
        assert 'post' in data
        assert data['post']['id'] == sample_post.id
        assert data['post']['content'] == sample_post.content
    
    def test_get_nonexistent_post(self, client, auth_headers):
        """Test getting a post that doesn't exist."""
        response = self.get(
            client,
            '/api/posts/99999',
            headers=auth_headers
        )
        
        self.assert_error_response(response, 404)
    
    def test_create_post(self, client, auth_headers, sample_user):
        """Test creating a new post."""
        post_data = {
            'user_id': sample_user.id,
            'author_id': sample_user.id,
            'author_first_name': sample_user.first_name,
            'author_last_name': sample_user.last_name,
            'content': 'This is a new test post',
            'type': 'professional',
            'tags': ['test', 'new']
        }
        
        response = self.post(
            client,
            '/api/posts',
            data=post_data,
            headers=auth_headers
        )
        
        data = self.assert_success_response(response, 201)
        assert 'post' in data
        assert data['post']['content'] == post_data['content']
        assert data['post']['type'] == post_data['type']
        assert data['post']['tags'] == post_data['tags']
    
    def test_create_post_missing_fields(self, client, auth_headers, sample_user):
        """Test creating post with missing required fields."""
        post_data = {
            'user_id': sample_user.id,
            # Missing required fields
        }
        
        response = self.post(
            client,
            '/api/posts',
            data=post_data,
            headers=auth_headers
        )
        
        self.assert_error_response(response, 400)
    
    def test_update_post(self, client, auth_headers, sample_post):
        """Test updating an existing post."""
        update_data = {
            'content': 'Updated content',
            'tags': ['updated', 'test']
        }
        
        response = self.put(
            client,
            f'/api/posts/{sample_post.id}',
            data=update_data,
            headers=auth_headers
        )
        
        data = self.assert_success_response(response, 200)
        assert data['post']['content'] == update_data['content']
        assert data['post']['tags'] == update_data['tags']
    
    def test_update_nonexistent_post(self, client, auth_headers):
        """Test updating a post that doesn't exist."""
        update_data = {'content': 'Updated content'}
        
        response = self.put(
            client,
            '/api/posts/99999',
            data=update_data,
            headers=auth_headers
        )
        
        self.assert_error_response(response, 404)
    
    def test_delete_post(self, client, auth_headers, sample_post):
        """Test deleting a post."""
        response = self.delete(
            client,
            f'/api/posts/{sample_post.id}',
            headers=auth_headers
        )
        
        self.assert_success_response(response, 200)
        
        # Verify post is deleted
        response = self.get(
            client,
            f'/api/posts/{sample_post.id}',
            headers=auth_headers
        )
        self.assert_error_response(response, 404)
