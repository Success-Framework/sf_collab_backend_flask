from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return {
        'message': 'Flask API is running',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users',
            'knowledge': '/api/knowledge',
            'knowledge_comments': '/api/knowledge-comments',
            'resource_views': '/api/resource-views',
            'resource_likes': '/api/resource-likes',
            'resource_downloads': '/api/resource-downloads',
            'ideas': '/api/ideas',
            'idea_comments': '/api/idea-comments',
            'suggestions': '/api/suggestions',
            'startups': '/api/startups',
            'startup_members': '/api/startup-members',
            'join_requests': '/api/join-requests',
            'notifications': '/api/notifications',
            'stories': '/api/stories',
            'story_views': '/api/story-views',
            'posts': '/api/posts',
            'post_comments': '/api/post-comments',
            'post_likes': '/api/post-likes',
            'connections': '/api/connections',
            'idea_bookmarks': '/api/idea-bookmarks',
            'knowledge_bookmarks': '/api/knowledge-bookmarks',
            'startup_bookmarks': '/api/startup-bookmarks',
            'refresh_tokens': '/api/refresh-tokens'
        }
    }
