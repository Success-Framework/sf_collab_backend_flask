# run.py
from gevent import monkey
monkey.patch_all()

import os
import warnings

from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app
from app.socket_events import socketio
from app.subscription_plans import insert_default_plans

# =====================================================
# ENV SETUP
# =====================================================
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

ENV = os.getenv("FLASK_ENV", "development")
PORT = int(os.getenv("PORT", 5000))
DEBUG = ENV != "production"

print("=" * 60)
print("🚀 SF COLLAB API STARTING")
print(f"ENV: {ENV}")
print(f"PORT: {PORT}")
print("=" * 60)

# =====================================================
# CREATE APP
# =====================================================
app = create_app(ENV)

# =====================================================
# PROXY FIX (PRODUCTION ONLY)
# =====================================================
if ENV == "production":
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_proto=1,
        x_host=1,
        x_for=1
    )

# =====================================================
# SOCKET.IO
# =====================================================
socketio.init_app(
    app,
    cors_allowed_origins=app.config.get('SOCKETIO_CORS_ALLOWED_ORIGINS', app.config['CORS_ORIGINS']),
    async_mode="gevent",
    allow_credentials=True,
    logger=DEBUG,
    engineio_logger=DEBUG,
    ping_timeout=60,
    ping_interval=25
)

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    with app.app_context():
        insert_default_plans()

    socketio.run(
        app,
        host="0.0.0.0",
        port=PORT,
        debug=DEBUG,
        use_reloader=False
    )
