"""
WebSocket Events Handler for Real-Time Chat
"""

from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio
from flask_jwt_extended import decode_token
from flask import request
from datetime import datetime
from app.config import Config
import logging


connected_users = {}
socket_sessions = {}
print("✅ socket_events.py loaded")
def get_user_from_token(token):
    try:
        decoded = decode_token(token)
        return decoded.get("sub")
    except Exception as e:
        logging.error(f"JWT decode error: {e}")
        return None
@socketio.on("connect")
def handle_connect(auth):
    print("🔌 SOCKET CONNECT")
    print("Auth payload:", auth)
    token = auth.get("token") if auth else None
    if not token:
        print("❌ No token provided")
        return False  # causes 400 if missing
    user_id = get_user_from_token(token)
    if not user_id:
        print("❌ Invalid token")
        return False
    sid = request.sid
    socket_sessions[sid] = {"user_id": user_id}
    connected_users.setdefault(user_id, []).append(sid)
    join_room(f"user_{user_id}")
    emit(
        "user_status",
        {
            "user_id": user_id,
            "status": "online",
            "timestamp": datetime.utcnow().isoformat(),
        },
        broadcast=True,
    )
    print(f"✅ User {user_id} connected (sid={sid})")
@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    session = socket_sessions.pop(sid, None)
    if not session:
        return
    user_id = session["user_id"]
    connected_users[user_id].remove(sid)
    if not connected_users[user_id]:
        del connected_users[user_id]
        emit(
            "user_status",
            {
                "user_id": user_id,
                "status": "offline",
                "timestamp": datetime.utcnow().isoformat(),
            },
            broadcast=True,
        )
    print(f"🔌 User {user_id} disconnected")
@socketio.on('join_conversation')
def handle_join_conversation(data):
    """User joins a conversation room"""
    conversation_id = data.get('conversation_id')
    sid = request.sid
    
    if sid not in socket_sessions:
        return
    
    user_id = socket_sessions[sid]['user_id']
    room = f"conversation_{conversation_id}"
    
    join_room(room)
    
    # Notify others in the conversation
    emit('user_joined_conversation', {
        'user_id': user_id,
        'conversation_id': conversation_id,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room, include_self=False)
    
    logging.info(f"User {user_id} joined conversation {conversation_id}")
@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """User leaves a conversation room"""
    conversation_id = data.get('conversation_id')
    sid = request.sid
    
    if sid not in socket_sessions:
        return
    
    user_id = socket_sessions[sid]['user_id']
    room = f"conversation_{conversation_id}"
    
    leave_room(room)
    
    emit('user_left_conversation', {
        'user_id': user_id,
        'conversation_id': conversation_id,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room, include_self=False)
@socketio.on('send_message')
def handle_send_message(data):
    """Handle new message from client"""
    from app.models.chatConversation import ChatConversation
    from app.models.chatMessage import ChatMessage
    from app.models.user import User
    from app.extensions import db
    
    sid = request.sid
    
    if sid not in socket_sessions:
        emit('error', {'message': 'Not authenticated'})
        return
    
    user_id = socket_sessions[sid]['user_id']
    conversation_id = data.get('conversation_id')
    content = data.get('content', '').strip()
    file_url = data.get('file_url')
    file_name = data.get('file_name')
    file_type = data.get('file_type')
    is_image = data.get('is_image', False)
    message_type = data.get('message_type', 'text')
    reply_to_id = data.get('reply_to_id')
    
    if not content and not file_url:
        emit('error', {'message': 'Message content or file URL is required'})
        return
        
    
    try:
        user = User.query.get(user_id)
        conversation = ChatConversation.query.get(conversation_id)
        
        if not user or not conversation:
            emit('error', {'message': 'User or conversation not found'})
            return
        
        if not conversation.is_user_participant(user_id):
            emit('error', {'message': 'Not a participant'})
            return
        
        # Create message - Now including file fields
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=user_id,
            original_content=content,
            message_type=message_type,
            reply_to_id=reply_to_id,
            file_url=file_url,
            file_name=file_name,
            file_type=file_type,
            is_image=is_image,
            sender_timezone=user.get_timezone() if hasattr(user, 'get_timezone') else 'UTC'
        )
        
        db.session.add(message)
        conversation.updated_at = datetime.utcnow()
        conversation.increment_unread_count(user_id)
        db.session.commit()
        
        # Prepare message data
        message_data = message.to_dict(for_user=user)
        message_data['sender'] = {
            'id': user.id,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'profilePicture': user.profile_picture
        }
        
        room = f"conversation_{conversation_id}"
        
        # Broadcast to conversation room
        emit('new_message', {
            'message': message_data,
            'conversation_id': conversation_id
        }, room=room)
        # 2️⃣ Emit to each participant's user room (GLOBAL updates)
        for participant in conversation.participants:
            emit('conversation_message', {
                'conversation_id': conversation_id,
                'message': message_data
            }, room=f"user_{participant.id}")
                
        logging.info(f"Message sent by user {user_id} in conversation {conversation_id}")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error sending message: {e}")
        emit('error', {'message': f'Failed to send message: {str(e)}'})
@socketio.on('typing_start')
def handle_typing_start(data):
    """User started typing"""
    conversation_id = data.get('conversation_id')
    sid = request.sid
    
    if sid not in socket_sessions:
        return
    
    user_id = socket_sessions[sid]['user_id']
    room = f"conversation_{conversation_id}"
    
    emit('user_typing', {
        'user_id': user_id,
        'conversation_id': conversation_id,
        'is_typing': True
    }, room=room, include_self=False)
@socketio.on('typing_stop')
def handle_typing_stop(data):
    """User stopped typing"""
    conversation_id = data.get('conversation_id')
    sid = request.sid
    
    if sid not in socket_sessions:
        return
    
    user_id = socket_sessions[sid]['user_id']
    room = f"conversation_{conversation_id}"
    
    emit('user_typing', {
        'user_id': user_id,
        'conversation_id': conversation_id,
        'is_typing': False
    }, room=room, include_self=False)
@socketio.on('mark_read')
def handle_mark_read(data):
    """Mark conversation as read"""
    from app.models.chatConversation import ChatConversation
    
    conversation_id = data.get('conversation_id')
    sid = request.sid
    
    if sid not in socket_sessions:
        return
    
    user_id = socket_sessions[sid]['user_id']
    
    try:
        conversation = ChatConversation.query.get(conversation_id)
        if conversation and conversation.is_user_participant(user_id):
            conversation.mark_as_read(user_id)
            
            room = f"conversation_{conversation_id}"
            emit('messages_read', {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room)
            
    except Exception as e:
        logging.error(f"Error marking as read: {e}")
@socketio.on('get_online_users')
def handle_get_online_users():
    """Get list of currently online users"""
    online_user_ids = list(connected_users.keys())
    emit('online_users', {'user_ids': online_user_ids})
# Helper functions to emit from routes
def emit_new_message(conversation_id, message_data):
    """Emit new message to conversation room (call from routes)"""
    room = f"conversation_{conversation_id}"
    socketio.emit('new_message', {
        'message': message_data,
        'conversation_id': conversation_id
    }, room=room)
def emit_message_edited(conversation_id, message_data):
    """Emit edited message to conversation room"""
    room = f"conversation_{conversation_id}"
    socketio.emit('message_edited', {
        'message': message_data,
        'conversation_id': conversation_id
    }, room=room)
def emit_message_deleted(conversation_id, message_id):
    """Emit deleted message notification"""
    room = f"conversation_{conversation_id}"
    socketio.emit('message_deleted', {
        'message_id': message_id,
        'conversation_id': conversation_id
    }, room=room)
def emit_conversation_update(conversation_id, conversation_data):
    """Emit conversation update to participants"""
    room = f"conversation_{conversation_id}"
    socketio.emit('conversation_updated', {
        'conversation': conversation_data
    }, room=room)
def emit_to_user(user_id, event, data):
    """Emit event to specific user"""
    socketio.emit(event, data, room=f"user_{user_id}")
def is_user_online(user_id):
    """Check if user is currently online"""
    return user_id in connected_users

def emit_notification(user_id, notification_data):
    """Emit notification to user in real-time"""
    try:
        socketio.emit('new_notification', {
            'notification': notification_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"user_{user_id}")
        
        logging.info(f"Notification emitted to user {user_id}")
    except Exception as e:
        logging.error(f"Error emitting notification: {e}")

def emit_user_status_update(user_id, status):
    """Emit user status update"""
    try:
        socketio.emit('user_status', {
            'user_id': user_id,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"user_{user_id}")
    except Exception as e:
        logging.error(f"Error emitting status: {e}")
        
def emit_user_left_conversation(conversation_id, user_id, user_name):
    """Emit when a user leaves a conversation."""
    socketio.emit(
        "user_left_conversation",
        {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user_name": user_name,
        },
        room=f"conversation_{conversation_id}",
    )
