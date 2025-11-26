from flask import Flask, request
from flask_cors import CORS
from .extensions import db, migrate, jwt
# from .utils.socketio import socketio
from .routes import (
    auth_routes,
    user_routes,
    idea_routes,
    knowledge_routes,
    main_routes,
    startup_routes,
    api_routes,
    project_goal_routes,
    startup_bookmark_routes,
    startup_member_routes,
    team_member_routes,
    team_performance_routes,
    achievement_routes,
    calendar_event_routes,
    chat_routes,
    conversation_routes,
    goal_milestone_routes,
    idea_bookmark_routes,
    idea_comment_routes,
    join_request_routes,
    knowledge_bookmark_routes,
    knowledge_comment_routes,
    notification_routes,
    post_routes,
    post_comment_routes,
    post_like_routes,
    post_media_routes,
    resource_download_routes,
    resource_like_routes,
    resource_view_routes,
    story_routes,
    story_view_routes,
    suggestion_routes,
    task_routes,
    user_achievement_routes
)
from .config import get_config
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'chat_files')
AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'chat_avatars')

def create_app(config_name=None):
    """Create and configure Flask application"""
    app = Flask(__name__,instance_relative_config=True)
    
    # JWT Configuration - MAKE SURE THIS IS SET
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY","ksjxhcjkzcze5c4z53c1z531c5z1dczdchzecuzed51535e151qsqdcqcdze55@_")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=6)
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    app.config.from_pyfile('config.py', silent=True)
    
    # Configure CORS - FIXED: More permissive for development
    CORS(app, 
        resources={
            r"/*": {  # Allow all routes, not just /api/*
                "origins": app.config.get('CORS_ORIGINS', [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:5173",
                    "http://127.0.0.1:5173"
                ]),
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type", 
                    "Authorization", 
                    "X-Requested-With",
                    "Accept",
                    "Origin"
                ],
                "supports_credentials": True,
                "expose_headers": ["Content-Type", "Authorization"],
                "max_age": 3600
            }
        },
        supports_credentials=True
    )
    
    # Add after_request handler for additional CORS headers
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in app.config.get('CORS_ORIGINS', []):
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept,Origin')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
        return response
        
    
    # Initialize extensions
    db.init_app(app)
    # socketio.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    auth_routes.init_oauth(app)
    

    
    # Register all blueprints
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(user_routes.users_bp)
    app.register_blueprint(idea_routes.ideas_bp)
    app.register_blueprint(knowledge_routes.knowledge_bp)
    app.register_blueprint(main_routes.main_bp)
    app.register_blueprint(startup_routes.startups_bp)
    app.register_blueprint(api_routes.api_bp)
    app.register_blueprint(project_goal_routes.project_goals_bp)
    app.register_blueprint(startup_bookmark_routes.bookmarks_bp)
    app.register_blueprint(startup_member_routes.startup_members_bp)
    app.register_blueprint(team_member_routes.team_members_bp)
    app.register_blueprint(team_performance_routes.team_performance_bp)
    app.register_blueprint(achievement_routes.achievements_bp)
    app.register_blueprint(calendar_event_routes.calendar_events_bp)
    app.register_blueprint(chat_routes.chat_bp)
    app.register_blueprint(conversation_routes.conversations_bp)
    app.register_blueprint(goal_milestone_routes.milestones_bp)
    app.register_blueprint(idea_bookmark_routes.idea_bookmarks_bp)
    app.register_blueprint(idea_comment_routes.idea_comments_bp)
    app.register_blueprint(join_request_routes.join_requests_bp)
    app.register_blueprint(knowledge_bookmark_routes.knowledge_bookmarks_bp)
    app.register_blueprint(knowledge_comment_routes.knowledge_comments_bp)
    app.register_blueprint(notification_routes.notifications_bp)
    app.register_blueprint(post_routes.posts_bp)
    app.register_blueprint(post_comment_routes.post_comments_bp)
    app.register_blueprint(post_like_routes.post_likes_bp)
    app.register_blueprint(post_media_routes.post_media_bp)
    app.register_blueprint(resource_download_routes.resource_downloads_bp)
    app.register_blueprint(resource_like_routes.resource_likes_bp)
    app.register_blueprint(resource_view_routes.resource_views_bp)
    app.register_blueprint(story_routes.stories_bp)
    app.register_blueprint(story_view_routes.story_views_bp)
    app.register_blueprint(suggestion_routes.suggestions_bp)
    app.register_blueprint(task_routes.tasks_bp)
    app.register_blueprint(user_achievement_routes.user_achievements_bp)
    
    # Create tables
    # with app.app_context():
    #     db.create_all()
    
    # Root endpoint
    @app.route('/')
    def index():
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
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'database': 'connected'}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'success': False, 'error': 'Internal server error'}, 500
    
    return app