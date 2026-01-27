from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from flask_session import Session
from app.config import Config
from flask_socketio import SocketIO
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