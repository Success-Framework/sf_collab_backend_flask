from flask import Flask, request, abort, request, g, send_from_directory, make_response
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
import time
import json
from app.services.email_service import EmailService
from flask_session import Session


WEBHOOK_SECRET = b'sFcollab_2025_secretKey!'

# Suppress warnings first
warnings.filterwarnings("ignore")
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'chat_avatars')

def get_email_service():
    return EmailService()

def create_app(config_name=None):
    """Create and configure Flask application"""

    app = Flask(__name__, instance_relative_config=True)
    
    # ✅ REMOVED BROKEN PREFLIGHT HANDLER - Flask-CORS handles this automatically
    
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    app.config.from_pyfile('config.py', silent=True)

    
    # JWT Configuration
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=6)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY") or app.config.get("SECRET_KEY")

    
    # Session configuration
    print(f"SESSION_TYPE from config: {app.config.get('SESSION_TYPE')}")

    
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    if os.getenv("FLASK_ENV") == "production":
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_SECURE"] = True
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = False

    
    # Ensure session keys have a prefix for Redis
    app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
    
    app.config.setdefault("GITHUB_CLIENT_ID", os.getenv("GITHUB_CLIENT_ID"))
    app.config.setdefault("GITHUB_CLIENT_SECRET", os.getenv("GITHUB_CLIENT_SECRET"))

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # AWS S3 Configuration
    app.config["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
    app.config["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
    app.config["AWS_REGION"] = os.getenv("AWS_REGION", "us-east-1")
    app.config["AWS_S3_BUCKET"] = os.getenv("AWS_S3_BUCKET")
    app.config["BACKEND_URL"] = Config.BACKEND_URL

    # Email service
    app.config['SMTP_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
    app.config['SMTP_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    app.config['SMTP_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['SMTP_USERNAME'] = os.getenv('MAIL_USERNAME', 'your_username')
    app.config['SMTP_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your_password')
    app.config['SMTP_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'your_default_sender')
    
    # AI services  
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
    app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY', '')
    app.config['HUGGINGFACE_API_KEY'] = os.getenv('HUGGINGFACE_API_KEY', '')


    # ✅ FIXED: Initialize CORS with proper configuration
    print("Initializing CORS with origins:", app.config.get('CORS_ORIGINS', []))
    
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get('CORS_ORIGINS', []),
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
                "supports_credentials": True,
                "expose_headers": ["Content-Type", "Authorization"],
                "max_age": 3600  # Cache preflight requests for 1 hour
            }
        },
        supports_credentials=True
    )


    @app.before_request
    def start_request_timer():
        g.start_time = time.time()
        
    @app.after_request
    def log_response(response):
        # Skip noise
        if request.path in ("/favicon.ico", "/health"):
            return response
            
        # ✅ FIXED: Ensure CORS headers are present for all responses
        if request.method == "OPTIONS":
            # Flask-CORS should handle this, but let's ensure headers are set
            response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
            
        if request.method == "OPTIONS" and not response.headers.get("Access-Control-Allow-Origin"):
            print("⚠️  CORS WARNING: Missing Access-Control-Allow-Origin header")
        
        start = getattr(g, "start_time", None)
        duration = round(time.time() - (start or time.time()), 4)

        # Request info
        method = request.method
        path = request.path
        status = response.status_code
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        origin = request.headers.get("Origin")
        user_agent = request.headers.get("User-Agent")

        # Auth presence (do NOT log tokens)
        has_auth = "Authorization" in request.headers
        has_cookie = bool(request.headers.get("Cookie"))

        # Request payload size (safe)
        content_length = request.content_length or 0

        # Response preview (safe)
        response_preview = ""
        if response.is_json:
            try:
                data = response.get_json()
                response_preview = json.dumps(data)[:300]
            except Exception:
                response_preview = "<invalid json>"
        else:
            response_preview = "<non-json response>"

        print(f"""
    ================= API REQUEST =================
    {method} {path}
    Status: {status}
    Duration: {duration}s

    Client IP: {ip}
    Origin: {origin}
    User-Agent: {user_agent}

    Auth Header Present: {has_auth}
    Cookie Present: {has_cookie}
    Request Size: {content_length} bytes

    Response Preview:
    {response_preview}
    =============================================""")
    
        return response
        
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    if app.config.get("SESSION_TYPE") == "filesystem":
        app.config["SESSION_FILE_DIR"] = os.path.join(BASE_DIR, "flask_session")
        os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

    sess = Session()
    if app.config.get("SESSION_TYPE") == "sqlalchemy":
        app.config["SESSION_SQLALCHEMY"] = db
        app.config["SESSION_SQLALCHEMY_TABLE"] = "sessions"

    sess.init_app(app)
   
    # Create sessions table if it doesn't exist
    with app.app_context():
        if app.config.get("SESSION_TYPE") == "sqlalchemy":
            try:
                db.create_all()
                print("✓ Sessions table ready")
            except Exception as e:
                print(f"Warning: Could not create sessions table: {e}")
        else:
            print("✓ Using filesystem sessions (no sessions table needed)")

    
    # Only init OAuth if env vars are present
    if app.config.get("GOOGLE_CLIENT_ID") and app.config.get("GOOGLE_CLIENT_SECRET"):
        auth_routes.init_oauth(app)
        print("✓ OAuth initialized")
    else:
        print("⚠  OAuth not initialized (missing GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET)")

    # Register all blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint["blueprint"], url_prefix=blueprint["url_prefix"])

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'database': 'connected'}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Resource not found'}, 404
    
    import traceback

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        print("🔥 500 ERROR:", error)
        traceback.print_exc()
        return {'success': False, 'error': str(error)}, 500

    
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
    
        print(event, payload)
        return '', 200

    return app