import os
from datetime import timedelta
from dotenv import load_dotenv
import stripe

# ======================================================
# ENV FILE LOADING PRIORITY
# .env.local > .env.development > .env
# ======================================================
dotenv_file = (
    ".env.local"
    if os.path.exists(".env.local")
    else ".env.development"
    if os.path.exists(".env.development")
    else ".env"
)

load_dotenv(dotenv_file)


# ======================================================
# BASE CONFIG
# ======================================================
class Config:
    """Base configuration (safe defaults)"""

    # ------------------------
    # Flask
    # ------------------------
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = True
    TESTING = False

    # ------------------------
    # Database
    # ------------------------
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_MAX_OVERFLOW = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_TIMEOUT = 30

    # ------------------------
    # OAuth
    # ------------------------
    BACKEND_URL = os.getenv("APP_DOMAIN", "http://localhost:5001")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    GOOGLE_REDIRECT_URI = f"{BACKEND_URL}/api/auth/google/callback"

    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    GITHUB_REDIRECT_URI = f"{BACKEND_URL}/api/auth/github/callback"

    # ------------------------
    # JSON
    # ------------------------
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # ------------------------
    # File uploads
    # ------------------------
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "chat_files")
    AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "chat_avatars")

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "pdf",
        "doc",
        "docx",
        "mp4",
        "mov",
        "avi",
    }

    # ------------------------
    # JWT
    # ------------------------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = "HS256"

    # ------------------------
    # CORS
    # ------------------------
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://sfclb.netlify.app",
        "https://sfmanagers-frontend.vercel.app",
        "https://sfcollab.com",
        "https://sfcollab.com/",
        "https://www.sfcollab.com/",
        "https://www.sfcollab.com",
        "https://api.sfcollab.com",
        "https://www.api.sfcollab.com",
        "d329ej3iwi83w9.cloudfront.net",
        "https://d329ej3iwi83w9.cloudfront.net",
    ]

    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
    ]

    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS

    # ------------------------
    # Sessions
    # ------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Security
    WTF_CSRF_ENABLED = False  # Disabled for API
    WTF_CSRF_TIME_LIMIT = None
    
    # Email (if needed in future)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Redis (if needed for caching/celery)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery (if needed for background tasks)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # API
    API_TITLE = 'Startup Platform API'
    API_VERSION = 'v1'
    API_PREFIX = '/api'
    
    # Timezone
    TIMEZONE = 'UTC'
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    @staticmethod
    def init_stripe():
        if not Config.STRIPE_SECRET_KEY:
            raise RuntimeError("STRIPE_SECRET_KEY is not set")
        stripe.api_key = Config.STRIPE_SECRET_KEY


# ======================================================
# DEVELOPMENT
# ======================================================
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging
    
    TESTING = False
    
    # Disable some security features for easier development
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False


# ======================================================
# TESTING
# ======================================================
class TestingConfig(Config):
    TESTING = True
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False


# ======================================================
# PRODUCTION
# ======================================================
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Ensure these are set in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    # Strict CORS in production - must be set via environment
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    # Enhanced security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_NAME = "sfcollab_session"

    # Production database with connection pooling
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_MAX_OVERFLOW = 40
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Logging
    LOG_LEVEL = 'WARNING'


# ======================================================
# STAGING
# ======================================================
class StagingConfig(ProductionConfig):
    DEBUG = False


# ======================================================
# CONFIG MAP
# ======================================================
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "staging": StagingConfig,
    "default": DevelopmentConfig,
}


def get_config(name=None):
    if name is None:
        name = os.getenv("FLASK_ENV", "development")
    return config.get(name, DevelopmentConfig)
