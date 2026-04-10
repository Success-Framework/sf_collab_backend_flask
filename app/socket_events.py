"""
WebSocket Events Handler for Real-Time Chat
"""

from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio, db
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
        to="/",
    )
    print(f"✅ User {user_id} connected (sid={sid})")
@socketio.on("disconnect")
def handle_disconnect(reason=None):
    sid = request.sid
    session = socket_sessions.pop(sid, None)
    if not session:
        return
    user_id = session["user_id"]
    connected_users[user_id].remove(sid)
    if not connected_users[user_id]:
        del connected_users[user_id]
        now_iso = datetime.utcnow().isoformat()
        # Persist last_seen timestamp in DB so other users see accurate "last seen" times
        try:
            from app.models.user import User
            user = User.query.get(user_id)
            if user and hasattr(user, 'last_seen'):
                user.last_seen = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            logging.warning(f"Could not update last_seen for user {user_id}: {e}")
        emit(
            "user_status",
            {
                "user_id": user_id,
                "status": "offline",
                "timestamp": now_iso,
                "last_seen": now_iso,
            },
            to="/",
        )
    # Clear away state on disconnect
    _last_activity.pop(str(user_id), None)
    _user_away_status.pop(str(user_id), None)
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
    message_type = str(data.get('message_type', 'text') or 'text').lower()
    reply_to_id = data.get('reply_to_id')

    has_file_url = bool(file_url)
    file_type_is_image = isinstance(file_type, str) and file_type.startswith('image/')
    derived_is_image = message_type == 'image' or file_type_is_image
    
    if not content and not has_file_url:
        emit('error', {'message': 'Message content or file URL is required'})
        return

    if message_type in ('image', 'file') and not has_file_url:
        emit('error', {'message': 'file_url is required for image/file messages'})
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
            metadata_data={'is_image': derived_is_image} if (has_file_url or message_type in ('image', 'file')) else {},
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

        # For each participant who had hidden this conversation, un-hide it
        # so the new message reappears in their list
        for participant in conversation.participants:
            if str(participant.id) != str(user_id):
                if conversation.is_hidden_for_user(participant.id):
                    conversation.unhide_for_user(participant.id)
        
        room = f"conversation_{conversation_id}"
        # Include conversation_type so the frontend can suppress general chat notifications
        conversation_meta = {
            'id': conversation_id,
            'conversation_type': conversation.conversation_type,
            'name': conversation.name,
        }
        
        # Broadcast to conversation room
        emit('new_message', {
            'message': message_data,
            'conversation_id': conversation_id,
            'conversation': conversation_meta,
        }, room=room)
        # 2️⃣ Emit to each participant's user room (GLOBAL updates)
        for participant in conversation.participants:
            emit('conversation_message', {
                'conversation_id': conversation_id,
                'message': message_data,
                'conversation': conversation_meta,
            }, room=f"user_{participant.id}")

        # 3️⃣ Emit "delivered" back to the SENDER if any recipient is currently online
        now_iso = datetime.utcnow().isoformat()
        any_recipient_online = any(
            str(p.id) != str(user_id) and str(p.id) in connected_users
            for p in conversation.participants
        )
        if any_recipient_online:
            socketio.emit('message_status_update', {
                'message_id': message.id,
                'conversation_id': conversation_id,
                'status': 'delivered',
                'delivered_at': now_iso
            }, room=f"user_{user_id}")
                
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
    """Mark conversation as read and notify senders their messages were read"""
    from app.models.chatConversation import ChatConversation
    from app.models.chatMessage import ChatMessage
    
    conversation_id = data.get('conversation_id')
    sid = request.sid
    
    if sid not in socket_sessions:
        return
    
    user_id = socket_sessions[sid]['user_id']
    
    try:
        conversation = ChatConversation.query.get(conversation_id)
        if not (conversation and conversation.is_user_participant(user_id)):
            return

        # Get unread messages BEFORE marking as read (sent by others, not this user)
        from app.models.chatConversation import conversation_user_reads
        from sqlalchemy import and_
        
        read_status = None
        try:
            read_status = db.session.execute(
                conversation_user_reads.select().where(
                    and_(
                        conversation_user_reads.c.conversation_id == conversation_id,
                        conversation_user_reads.c.user_id == user_id
                    )
                )
            ).first()
        except Exception:
            pass

        last_read_at = read_status.last_read_at if read_status else None

        # Fetch messages that this user hasn't read yet (sent by someone else)
        unread_messages_query = ChatMessage.query.filter(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.sender_id != user_id,
            ChatMessage.is_deleted == False
        )
        if last_read_at:
            unread_messages_query = unread_messages_query.filter(
                ChatMessage.created_at > last_read_at
            )
        unread_messages = unread_messages_query.all()

        # Mark as read in DB
        conversation.mark_as_read(user_id)

        # Emit unread_count_update to THIS user so ChatDock/ChatPage badge clears instantly
        try:
            remaining = conversation.get_unread_message_count(user_id)
        except Exception:
            remaining = 0
        socketio.emit('unread_count_update', {
            'conversation_id': conversation_id,
            'unread_count': remaining,
            'user_id': user_id,
        }, room=f"user_{user_id}")

        room = f"conversation_{conversation_id}"
        now_iso = datetime.utcnow().isoformat()

        # Notify room that this user read the conversation
        emit('messages_read', {
            'user_id': user_id,
            'conversation_id': conversation_id,
            'timestamp': now_iso
        }, room=room)

        # For each unread message, tell the SENDER their message was read
        notified_senders = set()
        for msg in unread_messages:
            sender_id = str(msg.sender_id)
            # Emit to the sender's personal room so they see the green ticks
            socketio.emit('message_status_update', {
                'message_id': msg.id,
                'conversation_id': conversation_id,
                'status': 'read',
                'read_at': now_iso,
                'read_by': user_id
            }, room=f"user_{sender_id}")
            notified_senders.add(sender_id)

        logging.info(
            f"User {user_id} read conversation {conversation_id}, "
            f"notified {len(notified_senders)} senders"
        )

    except Exception as e:
        logging.error(f"Error marking as read: {e}")
@socketio.on('join_notifications')
def handle_join_notifications(data):
    """User explicitly joins their notification room (called after connect)."""
    sid = request.sid
    if sid not in socket_sessions:
        return
    user_id = socket_sessions[sid]['user_id']
    # Security: only allow joining own room
    requested_user_id = str(data.get('user_id', '')) if data else ''
    if requested_user_id and requested_user_id != str(user_id):
        logging.warning(f"User {user_id} tried to join notifications room for user {requested_user_id}")
        return
    join_room(f'user_{user_id}')
    emit('notifications_room_joined', {'user_id': user_id})
    logging.info(f"User {user_id} joined notifications room")

# Track per-user last activity timestamp for away detection
# Key: user_id (str), Value: datetime of last ping
_last_activity = {}
# Track per-user whether they are currently marked as 'away'
_user_away_status = {}

@socketio.on('user_activity')
def handle_user_activity(data):
    """Track last-active timestamp for presence display.
    
    - Broadcasts the fresh timestamp to all clients so they can update idle timers.
    - If a user was previously marked 'away' (3+ min silence), sends an 'online'
      recovery event before updating the timestamp.
    """
    sid = request.sid
    if sid not in socket_sessions:
        return
    user_id = str(socket_sessions[sid]['user_id'])
    now = datetime.utcnow()
    ts_str = now.isoformat()

    # Check if user is recovering from 'away' state
    last = _last_activity.get(user_id)
    was_away = _user_away_status.get(user_id, False)
    AWAY_THRESHOLD_SECS = 3 * 60  # 3 minutes

    if last and was_away:
        # User is back — broadcast online recovery
        _user_away_status[user_id] = False
        emit('user_status', {
            'user_id': user_id,
            'status': 'online',
            'timestamp': ts_str,
        }, to="/", include_self=False)

    # Update last activity
    _last_activity[user_id] = now

    # Broadcast the fresh activity timestamp to all clients
    emit('user_activity', {
        'user_id': user_id,
        'ts': ts_str,
    }, to="/", include_self=False)


def _check_away_users():
    """Background thread: broadcast 'away' for users silent for 3+ minutes."""
    import time
    AWAY_THRESHOLD_SECS = 3 * 60
    CHECK_INTERVAL = 30  # check every 30s

    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            now = datetime.utcnow()
            for user_id, last in list(_last_activity.items()):
                # Only check users currently connected
                if user_id not in connected_users:
                    continue
                gap = (now - last).total_seconds()
                already_away = _user_away_status.get(user_id, False)
                if gap >= AWAY_THRESHOLD_SECS and not already_away:
                    _user_away_status[user_id] = True
                    socketio.emit('user_status', {
                        'user_id': user_id,
                        'status': 'away',
                        'timestamp': now.isoformat(),
                    }, to="/")
                    logging.info(f"User {user_id} marked away after {gap:.0f}s silence")
        except Exception as e:
            logging.warning(f"Away checker error: {e}")


# Start away-detection thread when module loads
import threading
_away_thread = threading.Thread(target=_check_away_users, daemon=True)
_away_thread.start()

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