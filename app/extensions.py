from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from flask_session import Session
from app.config import Config
from flask_socketio import SocketIO
from flask_limiter import Limiter
import os
oauth = OAuth()
jwt = JWTManager()
cors = CORS()
db = SQLAlchemy()
migrate = Migrate()
sess = Session()

socketio = SocketIO(
    async_mode="gevent",
    cors_allowed_origins=Config.CORS_ORIGINS,
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=True,
)

from flask_jwt_extended import get_jwt_identity
from flask import request

def user_or_ip():
    try:
        user = get_jwt_identity()
        if user:
            return f"user:{user}"
    except:
        pass
    return request.remote_addr

limiter = Limiter(
    key_func=user_or_ip,
    default_limits=["1000 per day"],
    storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379"),
)
