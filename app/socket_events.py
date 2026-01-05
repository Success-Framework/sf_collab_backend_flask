"""
Socket Events Module - Real-time Chat & Notifications
Handles WebSocket connections for live chat, messaging, and real-time updates
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask import request, session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize SocketIO
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='gevent',
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1e6
)

# Track connected users
connected_users = {}  # {user_id: {sid, username, status, timestamp}}
active_conversations = {}  # {conversation_id: [user_ids]}


# ===============================================
# CONNECTION & DISCONNECTION HANDLERS
# ===============================================

@socketio.on('connect')
def handle_connect():
    """Handle user connection"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        sid = request.sid
        
        if user_id:
            connected_users[user_id] = {
                'sid': sid,
                'username': username,
                'status': 'online',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Broadcast user online status
            emit('user_connected', {
                'user_id': user_id,
                'username': username,
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)
            
            logger.info(f"User {user_id} ({username}) connected via {sid}")
        else:
            logger.warning(f"Connection attempt without user_id: {sid}")
            
    except Exception as e:
        logger.error(f"Error in handle_connect: {str(e)}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle user disconnection"""
    try:
        user_id = None
        sid = request.sid
        
        # Find and remove user from connected_users
        for uid, data in list(connected_users.items()):
            if data['sid'] == sid:
                user_id = uid
                username = data.get('username', 'Unknown')
                del connected_users[uid]
                break
        
        if user_id:
            # Broadcast user offline status
            emit('user_disconnected', {
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)
            
            logger.info(f"User {user_id} disconnected")
        else:
            logger.warning(f"Disconnection from unknown user: {sid}")
            
    except Exception as e:
        logger.error(f"Error in handle_disconnect: {str(e)}")


# ===============================================
# CHAT MESSAGE EVENTS
# ===============================================

@socketio.on('join_conversation')
def handle_join_conversation(data):
    """User joins a specific conversation room"""
    try:
        conversation_id = data.get('conversation_id')
        user_id = session.get('user_id')
        
        if conversation_id and user_id:
            room = f"conversation_{conversation_id}"
            join_room(room)
            
            if conversation_id not in active_conversations:
                active_conversations[conversation_id] = []
            
            if user_id not in active_conversations[conversation_id]:
                active_conversations[conversation_id].append(user_id)
            
            # Notify others that user joined
            emit('user_joined_conversation', {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'username': session.get('username'),
                'timestamp': datetime.utcnow().isoformat()
            }, room=room, skip_sid=request.sid)
            
            logger.info(f"User {user_id} joined conversation {conversation_id}")
            
    except Exception as e:
        logger.error(f"Error in handle_join_conversation: {str(e)}")


@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """User leaves a specific conversation room"""
    try:
        conversation_id = data.get('conversation_id')
        user_id = session.get('user_id')
        
        if conversation_id and user_id:
            room = f"conversation_{conversation_id}"
            leave_room(room)
            
            if conversation_id in active_conversations:
                if user_id in active_conversations[conversation_id]:
                    active_conversations[conversation_id].remove(user_id)
                
                if not active_conversations[conversation_id]:
                    del active_conversations[conversation_id]
            
            # Notify others that user left
            emit('user_left_conversation', {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room)
            
            logger.info(f"User {user_id} left conversation {conversation_id}")
            
    except Exception as e:
        logger.error(f"Error in handle_leave_conversation: {str(e)}")


# ===============================================
# MESSAGE EMIT FUNCTIONS
# ===============================================

def emit_new_message(conversation_id, message_data):
    """
    Emit a new message to all users in a conversation
    
    Args:
        conversation_id: ID of the conversation
        message_data: Dictionary containing message details
            - id, content, sender_id, sender_name, timestamp, etc.
    """
    try:
        room = f"conversation_{conversation_id}"
        socketio.emit('new_message', {
            **message_data,
            'conversation_id': conversation_id,
            'timestamp': message_data.get('timestamp', datetime.utcnow().isoformat())
        }, room=room)
        
        logger.debug(f"Emitted new message in conversation {conversation_id}")
        
    except Exception as e:
        logger.error(f"Error in emit_new_message: {str(e)}")


def emit_message_edited(conversation_id, message_data):
    """
    Emit message edit notification to conversation
    
    Args:
        conversation_id: ID of the conversation
        message_data: Dictionary containing updated message details
    """
    try:
        room = f"conversation_{conversation_id}"
        socketio.emit('message_edited', {
            **message_data,
            'conversation_id': conversation_id,
            'edited_at': datetime.utcnow().isoformat()
        }, room=room)
        
        logger.debug(f"Emitted message edit in conversation {conversation_id}")
        
    except Exception as e:
        logger.error(f"Error in emit_message_edited: {str(e)}")


def emit_message_deleted(conversation_id, message_id):
    """
    Emit message deletion notification to conversation
    
    Args:
        conversation_id: ID of the conversation
        message_id: ID of the deleted message
    """
    try:
        room = f"conversation_{conversation_id}"
        socketio.emit('message_deleted', {
            'conversation_id': conversation_id,
            'message_id': message_id,
            'deleted_at': datetime.utcnow().isoformat()
        }, room=room)
        
        logger.debug(f"Emitted message deletion in conversation {conversation_id}")
        
    except Exception as e:
        logger.error(f"Error in emit_message_deleted: {str(e)}")


def emit_conversation_update(conversation_id, update_data):
    """
    Emit conversation state update to all users in conversation
    
    Args:
        conversation_id: ID of the conversation
        update_data: Dictionary containing conversation update details
            - name, description, settings, participants, etc.
    """
    try:
        room = f"conversation_{conversation_id}"
        socketio.emit('conversation_updated', {
            **update_data,
            'conversation_id': conversation_id,
            'updated_at': datetime.utcnow().isoformat()
        }, room=room)
        
        logger.debug(f"Emitted conversation update for {conversation_id}")
        
    except Exception as e:
        logger.error(f"Error in emit_conversation_update: {str(e)}")


def emit_to_user(user_id, event_name, data):
    """
    Emit an event to a specific user
    
    Args:
        user_id: ID of the target user
        event_name: Name of the event to emit
        data: Event data dictionary
    """
    try:
        if user_id in connected_users:
            user_sid = connected_users[user_id]['sid']
            socketio.emit(event_name, data, room=user_sid)
            logger.debug(f"Emitted {event_name} to user {user_id}")
        else:
            logger.warning(f"User {user_id} not connected for event {event_name}")
            
    except Exception as e:
        logger.error(f"Error in emit_to_user: {str(e)}")


# ===============================================
# TYPING INDICATOR
# ===============================================

@socketio.on('typing')
def handle_typing(data):
    """Handle user typing indicator"""
    try:
        conversation_id = data.get('conversation_id')
        user_id = session.get('user_id')
        username = session.get('username')
        
        if conversation_id and user_id:
            room = f"conversation_{conversation_id}"
            emit('user_typing', {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'username': username
            }, room=room, skip_sid=request.sid)
            
    except Exception as e:
        logger.error(f"Error in handle_typing: {str(e)}")


@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Handle user stop typing indicator"""
    try:
        conversation_id = data.get('conversation_id')
        user_id = session.get('user_id')
        
        if conversation_id and user_id:
            room = f"conversation_{conversation_id}"
            emit('user_stop_typing', {
                'conversation_id': conversation_id,
                'user_id': user_id
            }, room=room, skip_sid=request.sid)
            
    except Exception as e:
        logger.error(f"Error in handle_stop_typing: {str(e)}")


# ===============================================
# HEARTBEAT
# ===============================================

@socketio.on('heartbeat')
def handle_heartbeat():
    """Handle client heartbeat to keep connection alive"""
    try:
        user_id = session.get('user_id')
        if user_id and user_id in connected_users:
            connected_users[user_id]['timestamp'] = datetime.utcnow().isoformat()
            emit('heartbeat_ack', {'timestamp': datetime.utcnow().isoformat()})
            
    except Exception as e:
        logger.error(f"Error in handle_heartbeat: {str(e)}")


# ===============================================
# UTILITY FUNCTIONS
# ===============================================

def get_connected_users():
    """Get list of currently connected users"""
    return list(connected_users.keys())


def get_user_by_id(user_id):
    """Get user connection data by user_id"""
    return connected_users.get(user_id)


def is_user_connected(user_id):
    """Check if user is currently connected"""
    return user_id in connected_users


def get_conversation_users(conversation_id):
    """Get list of users currently in a conversation"""
    return active_conversations.get(conversation_id, [])
