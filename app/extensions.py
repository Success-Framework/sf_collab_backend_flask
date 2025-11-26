from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth

oauth = OAuth()
jwt = JWTManager()
cors = CORS()
db = SQLAlchemy()
migrate = Migrate()
