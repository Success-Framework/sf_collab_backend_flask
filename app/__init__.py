from flask import Flask, request, abort
from flask_cors import CORS
from .extensions import db, migrate, jwt, sess
from app.config import Config
from app.routes import auth_routes
from .config import get_config
import os
from datetime import timedelta
import logging
import warnings
import hmac
import hashlib
from app.blueprints import blueprints
from app.socket_events import socketio


WEBHOOK_SECRET = b'sFcollab_2025_secretKey!'

# Suppress warnings first
warnings.filterwarnings("ignore")
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'chat_files')
AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'chat_avatars')

# Set model cache location
# os.environ['HF_HOME'] = os.path.join(BASE_DIR, 'model_cache')
# os.environ['TRANSFORMERS_CACHE'] = os.path.join(BASE_DIR, 'model_cache')
# os.environ['TORCH_HOME'] = os.path.join(BASE_DIR, 'model_cache')

def create_app(config_name=None):
    """Create and configure Flask application"""

    app = Flask(__name__, instance_relative_config=True)
    
    CORS(
        app,
        resources={r"/*": {"origins": list(Config.CORS_ORIGINS)}},
        supports_credentials=True,
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Access-Control-Allow-Origin"
        ],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    # @app.after_request
    # def after_request(response):
    #     origin = request.headers.get('Origin')
    #     if origin in app.config['CORS_ORIGINS']:
    #         response.headers.add('Access-Control-Allow-Origin', origin)
    #         response.headers.add('Access-Control-Allow-Credentials', 'true')
    #         response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept,Origin')
    #         response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
    #     return response
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=6)
    app.secret_key = os.getenv('SECRET_KEY')
    
    # Session configuration for OAuth - Use SQLAlchemy (database-backed sessions)
    # This works across multiple workers and doesn't require Redis
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
    # Note: SESSION_SQLALCHEMY will be set after db.init_app()
    print("Using SQLAlchemy (database) session storage for OAuth")
    
    app.config['SESSION_PERMANENT'] = True  # Changed to True to persist session
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_COOKIE_NAME'] = 'session'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # Fix for OAuth CSRF state issues - use None (not Lax/Strict) for OAuth redirects
    app.config['SESSION_COOKIE_SAMESITE'] = None  # Changed from 'Lax' to None for OAuth
    app.config['SESSION_COOKIE_SECURE'] = True if os.getenv('FLASK_ENV') == 'production' else False
    
    # Don't set SESSION_COOKIE_DOMAIN - let it default to the request domain
    # if os.getenv('FLASK_ENV') == 'production':
    #     app.config['SESSION_COOKIE_DOMAIN'] = '.sfcollab.com'
    
    # Ensure session keys have a prefix for Redis
    app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
    
    app.config['GITHUB_CLIENT_ID'] = Config.GITHUB_CLIENT_ID
    app.config['GITHUB_CLIENT_SECRET'] = Config.GITHUB_CLIENT_SECRET

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    app.config.from_pyfile('config.py', silent=True)

    
    # Allowed origins for CORS (extended list)
    app.config['CORS_ORIGINS'] = Config.CORS_ORIGINS



    # Email service
    app.config['SMTP_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
    app.config['SMTP_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    app.config['SMTP_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['SMTP_USERNAME'] = os.getenv('MAIL_USERNAME', 'your_username')
    app.config['SMTP_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your_password')
    app.config['SMTP_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'your_default_sender')
    
    # AI services}  
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
    app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY', '')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    Config.init_stripe()
   
    # Set SESSION_SQLALCHEMY to use the same db instance
    
    with app.app_context():
        sess.init_app(app)
    
    # Create sessions table if it doesn't exist
    with app.app_context():
        try:
            # Try to create the sessions table
            db.create_all()
            print("✓ Sessions table ready")
        except Exception as e:
            print(f"Warning: Could not create sessions table: {e}")
    
    auth_routes.init_oauth(app)
    # Register all blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint["blueprint"], url_prefix=blueprint["url_prefix"])


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
    


    @app.route('/api/webhook/github', methods=['POST'])
    def github_webhook():
        signature = request.headers.get('X-Hub-Signature-256')
        if signature is None:
            abort(400, "No signature provided")
    
        sha_name, signature = signature.split('=')
        mac = hmac.new(os.getenv('WEBHOOK'), msg=request.data, digestmod=hashlib.sha256)
    
        if not hmac.compare_digest(mac.hexdigest(), signature):
            abort(403, "Invalid signature")
        
        event = request.headers.get('X-GitHub-Event')
        payload = request.json
    
        # Process your GitHub event here
        print(event, payload)
        return '', 200

    return app