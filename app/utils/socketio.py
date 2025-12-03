from flask_socketio import SocketIO
from flask import request
import logging

# Configure SocketIO with CORS support
socketio = SocketIO(async_mode="gevent")

__all__ = ['socketio']

# Store connected users: {user_id: socket_id}
connected_users = {}

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection"""
    user_id = request.args.get('user_id')
    if user_id:
        connected_users[str(user_id)] = request.sid
        logging.info(f'User {user_id} connected with SID {request.sid}')
        
        # Notify others about user coming online
        socketio.emit('user_online', {
            'user_id': user_id,
            'status': 'online'
        }, skip_sid=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    user_id = None
    for uid, sid in list(connected_users.items()):
        if sid == request.sid:
            user_id = uid
            break
    
    if user_id:
        del connected_users[user_id]
        logging.info(f'User {user_id} disconnected')
        
        # Notify others about user going offline
        socketio.emit('user_offline', {
            'user_id': user_id,
            'status': 'offline'
        })

@socketio.on('join_user_conversations')
def handle_join_user_conversations(data):
    """Join all user's conversation rooms"""
    user_id = data.get('user_id')
    
    if user_id:
        # Import here to avoid circular imports
        from app.models.chatConversation import ChatConversation, conversation_participants
        
        # Get all user's conversations
        conversations = ChatConversation.query\
            .join(conversation_participants)\
            .filter(conversation_participants.c.user_id == user_id)\
            .filter(ChatConversation.is_active == True)\
            .all()
        
        # Join each conversation room
        for conversation in conversations:
            room_name = f'conversation_{conversation.id}'
            socketio.server.enter_room(request.sid, room_name)
        
        logging.info(f'User {user_id} joined {len(conversations)} conversation rooms')

@socketio.on('join_conversation')
def handle_join_conversation(data):
    """Join a specific conversation room"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        room_name = f'conversation_{conversation_id}'
        socketio.server.enter_room(request.sid, room_name)
        logging.info(f'User {user_id} joined conversation room {conversation_id}')

@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """Leave a conversation room"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        room_name = f'conversation_{conversation_id}'
        socketio.server.leave_room(request.sid, room_name)
        logging.info(f'User {user_id} left conversation room {conversation_id}')

@socketio.on('start_typing')
def handle_start_typing(data):
    """Handle typing start event"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_user_typing(conversation_id, user_id, True)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Handle typing stop event"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_user_typing(conversation_id, user_id, False)

@socketio.on('mark_message_read')
def handle_mark_message_read(data):
    """Handle message read event"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    message_id = data.get('message_id')
    
    if conversation_id and user_id and message_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_message_read(conversation_id, user_id, message_id)

# Helper functions
def get_user_sid(user_id):
    """Get SocketIO SID for a user"""
    return connected_users.get(str(user_id))

def is_user_online(user_id):
    """Check if user is currently online"""
    return str(user_id) in connected_users

def get_online_users():
    """Get list of all online user IDs"""
    return list(connected_users.keys())

def get_online_count():
    """Get count of online users"""
    return len(connected_users)