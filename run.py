from gevent import monkey
monkey.patch_all()

import warnings
import os
import logging

# # ===== SUPPRESS WARNINGS FIRST =====
# # Configure logging to ignore specific warnings - DO THIS FIRST
# warnings.filterwarnings("ignore", category=FutureWarning, module=".*torch.*")
# warnings.filterwarnings("ignore", category=UserWarning, module=".*gevent.*")

# # Set environment variables for better compatibility
# os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# ===== NOW IMPORT YOUR APP =====
from app import create_app
from app.utils.socketio import socketio
from flask import request, g
import time
import json

app = create_app()

# ===== Custom Request Logging (status + data) =====
@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_response(response):
    if request.path == "/favicon.ico":
        return response

    now = time.time()
    duration = round(now - g.start_time, 4)

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    method = request.method
    path = request.path
    status = response.status_code

    # Log response data safely
    try:
        # For JSON responses
        if response.is_json:
            data = response.get_json()
            data_str = json.dumps(data)[:500]
        else:
            # For other responses
            data_str = response.data.decode("utf-8")[:500] if response.data else "No data"
    except Exception as e:
        data_str = f"Error reading response: {str(e)}"

    print(f"""
-------------------------
[REQUEST] {method} {path}
[IP]      {ip}
[STATUS]  {status}
[TIME]    {duration}s
[DATA]    {data_str}
-------------------------
""")

    return response
# ===================================================

socketio.init_app(
    app,
    cors_allowed_origins=app.config.get("CORS_ORIGINS", "*"),
    async_mode="gevent"
)


# ADD THIS FOR DEBUGGING
print(f"=== GUNICORN DEBUG INFO ===")
print(f"PORT env var: {os.environ.get('PORT')}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")
print(f"App object created: {app}")


# For Gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"=== Starting on port {port} ===")
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,  # Change to False for production
        use_reloader=False,
    )