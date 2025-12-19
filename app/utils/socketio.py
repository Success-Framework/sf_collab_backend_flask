from flask_socketio import SocketIO, emit
from flask import request
import logging
from app.models.user import User

# Configure SocketIO with CORS support
socketio = SocketIO(async_mode="gevent", cors_allowed_origins="*")

__all__ = ['socketio']

# Store connected users: {user_id: socket_id}
connected_users = {}
whiteboard_users = {}  # {conversation_id: [user_ids]}

# Add this helper function at the top of socketio.py, after the imports:

def safe_enter_room(sid, room_name, namespace='/'):
    """Safely enter a room with connection verification"""
    try:
        # Check if socket exists in manager
        if sid in socketio.server.manager.rooms.get(namespace, {}).get(None, {}):
            socketio.server.enter_room(sid, room_name, namespace=namespace)
            print(f'Socket {sid} entered room {room_name}')
            return True
        else:
            print(f'Socket {sid} not found in namespace {namespace}, cannot enter room {room_name}')
            return False
    except KeyError as e:
        logging.error(f'KeyError entering room {room_name}: {str(e)}')
        return False
    except Exception as e:
        logging.error(f'Error entering room {room_name}: {str(e)}')
        return False
        
        
@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connection"""
    try:
        user_id = request.args.get('user_id')
        if user_id:
            # IMPORTANT: Add the socket to the manager first
            socketio.server.manager.connect(request.sid, '/')
            
            # Then store the user mapping
            connected_users[str(user_id)] = request.sid
            
            print(f'User {user_id} connected with SID {request.sid}')
            
            # Notify others about user coming online
            socketio.emit('user_online', {
                'user_id': user_id,
                'status': 'online'
            }, skip_sid=request.sid)
            
            # Return success with socket info
            return {
                'status': 'connected', 
                'user_id': user_id,
                'socket_id': request.sid
            }
    except Exception as e:
        logging.error(f'Connection error: {str(e)}')
        return {'status': 'error', 'error': str(e)}

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
        print(f'User {user_id} disconnected')
        
        # Remove from all whiteboards
        for conversation_id in list(whiteboard_users.keys()):
            if user_id in whiteboard_users[conversation_id]:
                whiteboard_users[conversation_id].remove(user_id)
                
                # Notify others
                from app.services.realtime_service import RealtimeService
                RealtimeService.emit_user_left_whiteboard(conversation_id, user_id)
                
                # Update active users if any remain
                if whiteboard_users[conversation_id]:
                    RealtimeService.emit_active_whiteboard_users(
                        conversation_id, 
                        whiteboard_users[conversation_id]
                    )
        
        # Notify others about user going offline
        socketio.emit('user_offline', {
            'user_id': user_id,
            'status': 'offline'
        })

@socketio.on('join_user_conversations')
def handle_join_user_conversations(data):
    """Join all user's conversation rooms with safe room entry"""
    user_id = data.get('user_id')
    
    if not user_id:
        return {'status': 'error', 'message': 'No user_id provided'}
    
    # Verify socket exists using the safe method
    socket_id = request.sid
    if not socket_id in socketio.server.manager.rooms.get('/', {}).get(None, {}):
        print(f'Socket {socket_id} not ready for room operations')
        return {'status': 'error', 'message': 'Socket not ready'}
    
    try:
        # Import here to avoid circular imports
        from app.models.chatConversation import ChatConversation, conversation_participants
        
        # Get all user's conversations
        conversations = ChatConversation.query\
            .join(conversation_participants)\
            .filter(conversation_participants.c.user_id == user_id)\
            .filter(ChatConversation.is_active == True)\
            .all()
        
        # Join each conversation room safely
        joined_rooms = []
        for conversation in conversations:
            room_name = f'conversation_{conversation.id}'
            if safe_enter_room(socket_id, room_name):
                joined_rooms.append(room_name)
        
        print(f'User {user_id} joined {len(joined_rooms)} conversation rooms')
        
        return {
            'status': 'success', 
            'rooms_joined': len(joined_rooms),
            'joined_rooms': joined_rooms
        }
        
    except Exception as e:
        logging.error(f'Error joining conversations: {str(e)}')
        return {'status': 'error', 'message': str(e)}        

@socketio.on('join_conversation')
def handle_join_conversation(data):
    """Join a specific conversation room"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        room_name = f'conversation_{conversation_id}'
        if safe_enter_room(request.sid, room_name):
            print(f'User {user_id} joined conversation room {conversation_id}')
            return {'status': 'success', 'conversation_id': conversation_id}
        else:
            logging.error(f'Failed to join conversation room {conversation_id}')
            return {'status': 'error', 'message': 'Failed to join room'}

@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """Leave a conversation room"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        room_name = f'conversation_{conversation_id}'
        socketio.server.leave_room(request.sid, room_name)
        print(f'User {user_id} left conversation room {conversation_id}')
        
        return {'status': 'success', 'conversation_id': conversation_id}

@socketio.on('start_typing')
def handle_start_typing(data):
    """Handle typing start event"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_user_typing(conversation_id, user_id, True)
        
        return {'status': 'success'}

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Handle typing stop event"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_user_typing(conversation_id, user_id, False)
        
        return {'status': 'success'}

@socketio.on('mark_message_read')
def handle_mark_message_read(data):
    """Handle message read event"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    message_id = data.get('message_id')
    
    if conversation_id and user_id and message_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_message_read(conversation_id, user_id, message_id)
        
        return {'status': 'success'}

# NEW EVENT HANDLERS FOR MESSAGE OPERATIONS

@socketio.on('send_message')
def handle_send_message(data):
    """Handle sending a new message"""
    try:
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        content = data.get('content')
        message_type = data.get('message_type', 'text')
        metadata = data.get('metadata', {})
        reply_to_id = data.get('reply_to_id')
        
        if not all([conversation_id, user_id, content]):
            return {'error': 'Missing required fields'}
        
        # Import here to avoid circular imports
        from app.models.chatMessage import ChatMessage
        from app.extensions import db
        from datetime import datetime
        
        # Create new message
        new_message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=user_id,
            original_content=content,
            message_type=message_type,
            metadata_data=metadata,
            reply_to_id=reply_to_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        # Emit new message via RealtimeService
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_new_message(new_message.id, skip_sid=request.sid)
        
        print(f'User {user_id} sent message in conversation {conversation_id}')
        
        return {'status': 'success', 'message_id': new_message.id}
        
    except Exception as e:
        logging.error(f'Error sending message: {str(e)}')
        return {'error': str(e)}

@socketio.on('edit_message')
def handle_edit_message(data):
    """Handle editing an existing message"""
    try:
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        content = data.get('content')
        metadata = data.get('metadata', {})
        
        if not all([conversation_id, user_id, message_id, content]):
            return {'error': 'Missing required fields'}
        
        # Import here to avoid circular imports
        from app.models.chatMessage import ChatMessage
        from app.extensions import db
        
        # Find and update message
        message = ChatMessage.query.get(message_id)
        if not message:
            return {'error': 'Message not found'}
        
        # Check if user is the sender
        if message.sender_id != int(user_id):
            return {'error': 'Not authorized to edit this message'}
        
        # Update message
        message.edit_message(content, metadata)
        
        # Emit message edited via RealtimeService
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_message_edited(message_id)
        
        print(f'User {user_id} edited message {message_id}')
        
        return {'status': 'success', 'message_id': message_id}
        
    except Exception as e:
        logging.error(f'Error editing message: {str(e)}')
        return {'error': str(e)}

@socketio.on('delete_message')
def handle_delete_message(data):
    """Handle deleting a message"""
    try:
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        
        if not all([conversation_id, user_id, message_id]):
            return {'error': 'Missing required fields'}
        
        # Import here to avoid circular imports
        from app.models.chatMessage import ChatMessage
        from app.extensions import db
        
        # Find message
        message = ChatMessage.query.get(message_id)
        if not message:
            return {'error': 'Message not found'}
        
        # Check if user is the sender or has permission
        if message.sender_id != int(user_id):
            # TODO: Add admin/privilege check here if needed
            return {'error': 'Not authorized to delete this message'}
        
        # Store message ID before deletion
        stored_message_id = message.id
        stored_conversation_id = message.conversation_id
        
        # Delete message
        db.session.delete(message)
        db.session.commit()
        
        # Emit message deleted via RealtimeService
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_message_deleted(stored_message_id, stored_conversation_id)
        
        print(f'User {user_id} deleted message {message_id}')
        
        return {'status': 'success', 'message_id': stored_message_id}
        
    except Exception as e:
        logging.error(f'Error deleting message: {str(e)}')
        return {'error': str(e)}
        
        
#!========================== WHITEBOARD FUNCTIONS=========
@socketio.on('join_whiteboard')
def handle_join_whiteboard(data):
    """Join a whiteboard session for a conversation"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        # Join the whiteboard room safely
        room_name = f'whiteboard_{conversation_id}'
        if not safe_enter_room(request.sid, room_name):
            logging.error(f'Failed to join whiteboard room {room_name} for user {user_id}')
            return {'status': 'error', 'message': 'Failed to join whiteboard'}
        
        # Track user in whiteboard
        if conversation_id not in whiteboard_users:
            whiteboard_users[conversation_id] = []
        
        if user_id not in whiteboard_users[conversation_id]:
            whiteboard_users[conversation_id].append(user_id)
        
        # Notify others
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_user_joined_whiteboard(conversation_id, user_id)
        
        # Send current active users to the joining user
        RealtimeService.emit_active_whiteboard_users(
            conversation_id, 
            whiteboard_users[conversation_id]
        )
        
        print(f'User {user_id} joined whiteboard for conversation {conversation_id}')
        return {'status': 'success', 'conversation_id': conversation_id}

@socketio.on('leave_whiteboard')
def handle_leave_whiteboard(data):
    """Leave a whiteboard session"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        # Leave the whiteboard room
        room_name = f'whiteboard_{conversation_id}'
        try:
            socketio.server.leave_room(request.sid, room_name)
        except Exception as e:
            print(f'Error leaving whiteboard room: {str(e)}')
        
        # Remove user from tracking
        if conversation_id in whiteboard_users and user_id in whiteboard_users[conversation_id]:
            whiteboard_users[conversation_id].remove(user_id)
            
            # Notify others
            from app.services.realtime_service import RealtimeService
            RealtimeService.emit_user_left_whiteboard(conversation_id, user_id)
            
            # Update active users
            if whiteboard_users[conversation_id]:
                RealtimeService.emit_active_whiteboard_users(
                    conversation_id, 
                    whiteboard_users[conversation_id]
                )
        
        print(f'User {user_id} left whiteboard for conversation {conversation_id}')
        return {'status': 'success', 'conversation_id': conversation_id}
    
    return {'status': 'error', 'message': 'Missing conversation_id or user_id'}
    

@socketio.on('whiteboard_drawing')
def handle_whiteboard_drawing(data):
    """Handle whiteboard drawing data"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    image_data = data.get('image_data')
    
    user = User.query.get(user_id)
    user_name=user.get_full_name()
    
    if conversation_id and user_id and image_data:
        from app.services.realtime_service import RealtimeService
        
        # Check if this is a cursor movement
        if image_data.get('type') == 'cursor_move':
            RealtimeService.emit_user_cursor_move(
                conversation_id, 
                user_id, 
                image_data.get('x', 0), 
                image_data.get('y', 0),
                image_data.get('color'),
                user_name  
            )
        else:
            # Regular drawing data
            RealtimeService.emit_whiteboard_image(conversation_id, image_data, user_id)
        
        return {'status': 'success'}
        
@socketio.on('whiteboard_clear')
def handle_whiteboard_clear(data):
    """Handle whiteboard clear request"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_whiteboard_clear(conversation_id, user_id)
        
        return {'status': 'success'}

@socketio.on('whiteboard_undo')
def handle_whiteboard_undo(data):
    """Handle whiteboard undo request"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_whiteboard_undo(conversation_id, user_id)
        
        return {'status': 'success'}

@socketio.on('whiteboard_redo')
def handle_whiteboard_redo(data):
    """Handle whiteboard redo request"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if conversation_id and user_id:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_whiteboard_redo(conversation_id, user_id)
        
        return {'status': 'success'}

@socketio.on('get_whiteboard_users')
def handle_get_whiteboard_users(data):
    """Get active users in a whiteboard"""
    conversation_id = data.get('conversation_id')
    
    if conversation_id:
        users = whiteboard_users.get(conversation_id, [])
        
        return {
            'status': 'success',
            'conversation_id': conversation_id,
            'active_users': users,
            'count': len(users)
        }


@socketio.on('whiteboard_batch_drawings')
def handle_whiteboard_batch_drawings(data):
    """Handle batch whiteboard drawings"""
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    drawings = data.get('drawings', [])
    
    if conversation_id and user_id and drawings:
        from app.services.realtime_service import RealtimeService
        # Emit each drawing in the batch
        for drawing in drawings:
            RealtimeService.emit_whiteboard_image(
                conversation_id, 
                drawing.get('image_data'), 
                user_id
            )
        
        return {'status': 'success', 'count': len(drawings)}

@socketio.on('set_user_status')
def handle_set_user_status(data):
    """Handle user status change"""
    user_id = data.get('user_id')
    status = data.get('status')  # online, away, busy, offline
    
    if user_id and status:
        from app.services.realtime_service import RealtimeService
        RealtimeService.emit_user_status_change(user_id, status)
        
        return {'status': 'success', 'user_id': user_id, 'new_status': status}
        
#!========================== Helper functions=============
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