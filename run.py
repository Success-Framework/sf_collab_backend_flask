from gevent import monkey
monkey.patch_all()

import os
import warnings
import logging
import time
import json

from app import create_app
from app.utils.socketio import socketio
from flask import request, g

app = create_app()

# ===== Custom Request Logging =====
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

    try:
        if response.is_json:
            data_str = json.dumps(response.get_json())[:500]
        else:
            data_str = (response.data.decode("utf-8") if response.data else "No data")[:500]
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

# init WITHOUT specifying async_mode
socketio.init_app(
    app,
    cors_allowed_origins="*"
)


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     socketio.run(
#         app,
#         host="0.0.0.0",
#         port=port,
#         debug=True,
#         use_reloader=False
#     )
