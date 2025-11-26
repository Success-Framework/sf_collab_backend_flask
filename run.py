import eventlet
eventlet.monkey_patch()     # MUST BE FIRST

from app import create_app
from app.utils.socketio import socketio

app = create_app()

# initialize socketio with the already-created app only at runtime
socketio.init_app(app, cors_allowed_origins=app.config.get('CORS_ORIGINS','*'))

if __name__ == "__main__":
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # eventlet does NOT work with reloader
    )
