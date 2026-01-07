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
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv("SECRET_KEY")

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
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5001")
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
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "chat_files")
    AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "chat_avatars")

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
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
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
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
        "https://www.sfcollab.com",
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

    # ------------------------
    # Security
    # ------------------------
    WTF_CSRF_ENABLED = False  # API only

    # ------------------------
    # Rate limiting
    # ------------------------
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    REDIS_URL = os.getenv("REDIS_URL")

    # ------------------------
    # Stripe
    # ------------------------
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

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

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"

    RATELIMIT_ENABLED = False


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

    if not os.getenv("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be set in production")

    if not os.getenv("JWT_SECRET_KEY"):
        raise RuntimeError("JWT_SECRET_KEY must be set in production")

    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_MAX_OVERFLOW = 40
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


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
