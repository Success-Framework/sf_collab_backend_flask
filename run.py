from gevent import monkey
monkey.patch_all()

import os
import warnings
import time
import json
from flask import request, g
from werkzeug.middleware.proxy_fix import ProxyFix
# very top of create_app or run.py
from dotenv import load_dotenv
load_dotenv()


from app import create_app
from app.config import Config
from app.socket_events import socketio

warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

print("=" * 60)
print("=== RUN.PY STARTING ===")
print(f"PORT: {os.environ.get('PORT', 'NOT SET')}")
print("=" * 60)

app = create_app()

env = os.environ.get("FLASK_ENV", "development")
if env == "production":
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_proto=1,
        x_host=1,
        x_for=1
    )


# ================= REQUEST LOGGING =================
@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_response(response):
    if request.path == "/favicon.ico":
        return response

    duration = round(time.time() - g.start_time, 4)

    try:
        data = response.get_json() if response.is_json else response.data.decode()[:400]
    except Exception:
        data = "Unable to read response"

    print(f"""
-------------------------
{request.method} {request.path}
STATUS: {response.status_code}
TIME: {duration}s
DATA: {data}
-------------------------
""")
    return response
# ===================================================

# ===== SOCKET.IO SETUP =====
socketio.init_app(
    app,
    cors_allowed_origins=Config.CORS_ORIGINS,
    async_mode="gevent",
    allow_credentials=True,
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)



# ===== START SERVER =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = env != "production"

    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=debug,
        use_reloader=False
    )
