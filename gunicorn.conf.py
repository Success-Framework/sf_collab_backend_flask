import os

# Get port from environment variable
port = int(os.environ.get('PORT', 10000))

bind = f"0.0.0.0:{port}"
workers = 1
worker_class = 'gevent'
timeout = 120
keepalive = 2
loglevel = 'debug'  # Changed to debug for more info
accesslog = '-'
errorlog = '-'
preload_app = True

# Add hooks to see what's happening
def on_starting(server):
    print(f"=== GUNICORN STARTING ===")
    print(f"Binding to: {bind}")
    print(f"PORT env var: {os.environ.get('PORT')}")
    print(f"Working dir: {os.getcwd()}")

def when_ready(server):
    print(f"=== GUNICORN READY ===")
    print(f"Listening on {bind}")
    print(f"PID: {os.getpid()}")

def worker_int(worker):
    print(f"=== WORKER INTERRUPTED ===")

def worker_abort(worker):
    print(f"=== WORKER ABORTED ===")