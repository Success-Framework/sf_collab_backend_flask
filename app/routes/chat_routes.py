
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.chatConversation import ChatConversation, conversation_participants
from app.models.chatMessage import ChatMessage
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response
from app.utils.timezone_converter import TimezoneConverter, get_user_timezone
import logging
import re
from datetime import datetime
from werkzeug.utils import secure_filename
import os 
import json
from app.utils.chat_utils import (
    get_or_create_general_chat,
    add_user_to_general_chat,
    on_user_profile_created,
    on_founder_created,
    on_team_member_added,
    on_team_member_removed
)

# Import socket events for real-time updates
try:
    from app.socket_events import (
        emit_new_message, 
        emit_message_edited, 
        emit_message_deleted,
        emit_conversation_update,
        emit_to_user
    )
    SOCKET_ENABLED = True
except ImportError:
    SOCKET_ENABLED = False
    logging.warning("Socket events not available - real-time updates disabled")

chat_bp = Blueprint('chat', __name__)

# Upload configurations
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'chat_files')
AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'chat_avatars')

# Ensure upload directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}
ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_avatar(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS
    

def validate_file_size(file, max_size=MAX_FILE_SIZE):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= max_size


#! GET CONVERSATIONS
@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get user's conversations with timezone-converted previews"""
    try:
        current_user_id = get_jwt_identity()
        
        user = User.query.get(current_user_id)
        if not user:
            return error_response('User not found', 404)
        
        conversations = (
            ChatConversation.query
            .join(conversation_participants)
            .filter(conversation_participants.c.user_id == current_user_id)
            .order_by(ChatConversation.updated_at.desc())
            .all()
        )

        
        conversations_data = []
        for conv in conversations:
            try:
                conversations_data.append(conv.to_dict(for_user=user))
            except Exception as e:
                logging.error(f'Error converting conversation {conv.id}: {str(e)}')
                continue
        
        return success_response({
            'conversations': conversations_data
        })
    
    except Exception as e:
        logging.error(f'Error in get_conversations: {str(e)}')
        return error_response(f'Failed to load conversations: {str(e)}', 500)


#! GET GENERAL CHAT
@chat_bp.route('/general', methods=['GET'])
@jwt_required()
def get_general_chat():
    """Get the general chat conversation"""
    try:
        from app.utils.general_chat import get_or_create_general_chat
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        general_chat = get_or_create_general_chat()
        
        if not general_chat:
            return error_response('General chat not available', 404)
        
        return success_response({
            'conversation': general_chat.to_dict(for_user=user)
        })
    
    except Exception as e:
        logging.error(f'Error getting general chat: {str(e)}')
        return error_response(f'Failed to get general chat: {str(e)}', 500)


#! MARK CONVERSATION AS READ
@chat_bp.route('/conversations/<int:conversation_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_conversation_read(conversation_id):
    """Mark conversation as read for user"""
    try:
        current_user_id = get_jwt_identity()
        
        user = User.query.get(current_user_id)
        conversation = ChatConversation.query.get(conversation_id)
        
        if not user or not conversation:
            return error_response('User or conversation not found', 404)
        
        if not conversation.is_user_participant(current_user_id):
            return error_response('Access denied', 403)
        
        conversation.mark_as_read(current_user_id)
        
        return success_response({
            'message': 'Conversation marked as read'
        })
    
    except Exception as e:
        logging.error(f'Error marking conversation as read: {str(e)}')
        return error_response(f'Failed to mark conversation as read: {str(e)}', 500)


#! GET MESSAGES
@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    """Get messages for conversation with timezone conversion"""
    try:
        current_user_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        user = User.query.get(current_user_id)
        conversation = ChatConversation.query.get(conversation_id)
        
        if not user or not conversation:
            return error_response('User or conversation not found', 404)
        
        if not conversation.is_user_participant(current_user_id):
            return error_response('Access denied', 403)
        
        messages = conversation.get_messages_for_user(user, limit, offset)
        
        return success_response({
            'conversation': conversation.to_dict(for_user=user),
            'messages': messages
        })
    
    except Exception as e:
        logging.error(f'Error in get_messages: {str(e)}')
        return error_response(f'Failed to load messages: {str(e)}', 500)


#! SEND MESSAGE (with WebSocket emission)
@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """Send new message with timezone handling, file upload, and WebSocket emission"""
    current_user_id = get_jwt_identity()
    
    is_file_upload = 'file' in request.files
    
    if is_file_upload:
        if 'file' not in request.files:
            return error_response('No file provided')
        
        file = request.files['file']
        if file.filename == '':
            return error_response('No file selected')
        
        if not allowed_file(file.filename):
            return error_response(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}')
        
        if not validate_file_size(file):
            return error_response(f'File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024)}MB')
        
        content = request.form.get('content', 'Sent a file')
        message_type = request.form.get('message_type', 'file')
        reply_to_id = request.form.get('reply_to_id', type=int)
        
    else:
        data = request.get_json()
        content = data.get('content')
        message_type = data.get('message_type', 'text')
        reply_to_id = data.get('reply_to_id')
        file = None
    
    if not content:
        return error_response('Missing required field: content')
    
    user = User.query.get(current_user_id)
    conversation = ChatConversation.query.get(conversation_id)
    
    if not user or not conversation:
        return error_response('User or conversation not found', 404)
    
    if not conversation.is_user_participant(user.id):
        return error_response('Access denied', 403)
    
    try:
        sender_timezone = get_user_timezone(user)
        original_content = content
        metadata_data = {} if is_file_upload else data.get('metadata_data', {})
        
        time_pattern = r'\[(\d{1,2}:\d{2})\]'
        has_existing_placeholders = bool(re.search(time_pattern, original_content))
        
        if has_existing_placeholders:
            metadata_data['has_time_placeholders'] = True
            metadata_data['sender_timezone'] = sender_timezone
            metadata_data['sent_at_utc'] = datetime.utcnow().isoformat()
        
        file_url = None
        file_name = None
        file_size = None
        file_type = None
        
        if file:
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{current_user_id}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            file.save(file_path)
            
            file_name = filename
            file_size = os.path.getsize(file_path)
            file_type = file.content_type
            file_url = f"/api/chat/uploads/{unique_filename}"
            
            metadata_data['file_info'] = {
                'original_name': file_name,
                'size': file_size,
                'type': file_type,
                'uploaded_at': datetime.utcnow().isoformat()
            }
        
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=user.id,
            original_content=original_content,
            message_type=message_type,
            metadata_data=metadata_data,
            reply_to_id=reply_to_id,
            sender_timezone=sender_timezone,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type
        )
        
        db.session.add(message)
        conversation.updated_at = datetime.utcnow()
        conversation.increment_unread_count(user.id)
        db.session.commit()
        
        response_data = message.to_dict(for_user=user)
        
        # Add sender info for WebSocket broadcast
        response_data['sender'] = {
            'id': user.id,
            'firstName': user.first_name,
            'lastName': user.last_name,
            'profilePicture': user.profile_picture
        }
        
        # Emit WebSocket event for real-time updates
        if SOCKET_ENABLED:
            emit_new_message(conversation_id, response_data)
        
        return success_response({
            'message': response_data,
            'original_content': original_content,
            'has_time_placeholders': has_existing_placeholders,
            'file_uploaded': file is not None
        }, 'Message sent successfully', 201)
    
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to send message: {str(e)}')
        return error_response(f'Failed to send message: {str(e)}', 500)


#! EDIT MESSAGE (with WebSocket emission)
@chat_bp.route('/conversations/<int:conversation_id>/messages/<int:message_id>', methods=['PUT'])
@jwt_required()
def edit_message(conversation_id, message_id):
    """Edit an existing message"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('content'):
        return error_response('Content is required')
    
    try:
        message = ChatMessage.query.get(message_id)
        
        if not message:
            return error_response('Message not found', 404)
        
        if message.conversation_id != conversation_id:
            return error_response('Message does not belong to this conversation', 400)
        
        if message.sender_id != current_user_id:
            return error_response('You can only edit your own messages', 403)
        
        new_content = data.get('content')
        metadata_data = data.get('metadata_data', message.metadata_data or {})
        
        time_pattern = r'\[(\d{1,2}:\d{2})\]'
        has_existing_placeholders = bool(re.search(time_pattern, new_content))
        
        if has_existing_placeholders:
            metadata_data['has_time_placeholders'] = True
            metadata_data['edited_with_time_placeholders'] = True
        
        message.edit_message(new_content, metadata_data)
        
        user = User.query.get(current_user_id)
        response_data = message.to_dict(for_user=user)
        
        # Emit WebSocket event
        if SOCKET_ENABLED:
            emit_message_edited(conversation_id, response_data)
        
        return success_response({
            'message': response_data
        }, 'Message edited successfully')
    
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to edit message: {str(e)}')
        return error_response(f'Failed to edit message: {str(e)}', 500)


#! DELETE MESSAGE (with WebSocket emission)
@chat_bp.route('/conversations/<int:conversation_id>/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(conversation_id, message_id):
    """Delete a message"""
    current_user_id = get_jwt_identity()
    
    try:
        message = ChatMessage.query.get(message_id)
        conversation = ChatConversation.query.get(conversation_id)
        
        if not message:
            return error_response('Message not found', 404)
        
        if message.conversation_id != conversation_id:
            return error_response('Message does not belong to this conversation', 400)
        
        if message.sender_id != current_user_id and conversation.created_by_id != current_user_id:
            return error_response('You can only delete your own messages or you must be the conversation creator', 403)
        
        if message.file_url:
            try:
                file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(message.file_url))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.error(f'Failed to delete file: {str(e)}')
        
        db.session.delete(message)
        db.session.commit()
        
        # Emit WebSocket event
        if SOCKET_ENABLED:
            emit_message_deleted(conversation_id, message_id)
        
        return success_response({
            'message_id': message_id
        }, 'Message deleted successfully')
    
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to delete message: {str(e)}')
        return error_response(f'Failed to delete message: {str(e)}', 500)


#! CREATE CONVERSATION (with auto-join and WebSocket)
@chat_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """Create new conversation with WebSocket emission"""
    try:
        current_user_id = get_jwt_identity()
        
        has_avatar = 'avatar' in request.files
        
        if has_avatar:
            data = {
                'participant_ids': json.loads(request.form.get('participant_ids', '[]')),
                'name': request.form.get('name'),
                'conversation_type': request.form.get('conversation_type', 'direct'),
                'description': request.form.get('description')
            }
            avatar_file = request.files['avatar']
        else:
            data = request.get_json()
            avatar_file = None
        
        required_fields = ['participant_ids']
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields: participant_ids', 400)
        
        creator = User.query.get(current_user_id)
        if not creator:
            return error_response('Creator not found', 404)
        
        # Handle avatar upload
        avatar_url = None
        if avatar_file:
            if not allowed_avatar(avatar_file.filename):
                return error_response(f'Avatar file type not allowed')
            
            if not validate_file_size(avatar_file, MAX_AVATAR_SIZE):
                return error_response(f'Avatar size exceeds limit')
            
            filename = secure_filename(avatar_file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"avatar_{timestamp}_{current_user_id}_{filename}"
            file_path = os.path.join(AVATAR_UPLOAD_FOLDER, unique_filename)
            
            avatar_file.save(file_path)
            avatar_url = f"/uploads/chat_avatars/{unique_filename}"
        
        # Check for existing direct conversation
        participant_ids = data['participant_ids']
        if data.get('conversation_type', 'direct') == 'direct' and len(participant_ids) == 1:
            other_user_id = participant_ids[0]
            existing = ChatConversation.query\
                .join(conversation_participants)\
                .filter(conversation_participants.c.user_id == current_user_id)\
                .filter(ChatConversation.conversation_type == 'direct')\
                .filter(ChatConversation.is_active == True)\
                .all()
            
            for conv in existing:
                if conv.is_user_participant(other_user_id) and len(conv.participants) == 2:
                    return success_response({
                        'conversation': conv.to_dict(for_user=creator),
                        'existing': True
                    }, 'Existing conversation found')
        
        conversation = ChatConversation(
            name=data.get('name'),
            conversation_type=data.get('conversation_type', 'direct'),
            created_by_id=creator.id,
            description=data.get('description'),
            avatar_url=avatar_url
        )
        
        db.session.add(conversation)
        db.session.flush()
        
        participants = User.query.filter(User.id.in_(participant_ids)).all()
        
        conversation.add_participant(creator, 'admin')
        
        for participant in participants:
            if participant.id != creator.id:
                conversation.add_participant(participant, 'member')
        
        db.session.commit()
        
        conv_data = conversation.to_dict(for_user=creator)
        
        # Notify all participants via WebSocket
        if SOCKET_ENABLED:
            for participant in conversation.participants:
                emit_to_user(participant.id, 'new_conversation', {
                    'conversation': conv_data
                })
        
        return success_response({
            'conversation': conv_data
        }, 'Conversation created successfully', 201)
    
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to create conversation: {str(e)}')
        import traceback
        traceback.print_exc()
        return error_response(f'Failed to create conversation: {str(e)}', 500)


#! GET ONLINE STATUS
@chat_bp.route('/online-status', methods=['GET'])
@jwt_required()
def get_online_status():
    """Get online status of users"""
    try:
        if SOCKET_ENABLED:
            from app.socket_events import connected_users
            return success_response({
                'online_users': list(connected_users.keys())
            })
        else:
            return success_response({'online_users': []})
    except Exception as e:
        return error_response(f'Failed to get online status: {str(e)}', 500)


#! SERVE UPLOADED FILE
@chat_bp.route('/uploads/<path:filename>', methods=['GET'])
def serve_uploaded_file(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)
    except FileNotFoundError:
        return error_response('File not found', 404)


#! GET CONVERSATION FILES
@chat_bp.route('/conversations/<int:conversation_id>/files', methods=['GET'])
@jwt_required()
def get_conversation_files(conversation_id):
    """Get all files from a conversation"""
    try:
        current_user_id = get_jwt_identity()
        
        conversation = ChatConversation.query.get(conversation_id)
        
        if not conversation:
            return error_response('Conversation not found', 404)
        
        if not conversation.is_user_participant(current_user_id):
            return error_response('Access denied', 403)
        
        messages_with_files = ChatMessage.query.filter_by(
            conversation_id=conversation_id
        ).filter(
            ChatMessage.file_url.isnot(None)
        ).order_by(ChatMessage.created_at.desc()).all()
        
        files = []
        for msg in messages_with_files:
            file_url = msg.file_url
            if file_url and not file_url.startswith('http'):
                file_url = request.host_url.rstrip('/') + file_url
            
            files.append({
                'id': msg.id,
                'file_name': msg.file_name,
                'file_url': file_url,
                'file_size': msg.file_size,
                'file_type': msg.file_type,
                'uploaded_by': {
                    'id': msg.sender_id,
                    'firstName': msg.message_sender.first_name,
                    'lastName': msg.message_sender.last_name
                },
                'uploaded_at': msg.created_at.isoformat(),
                'is_image': msg.is_image(),
                'is_document': msg.is_document()
            })
        
        return success_response({
            'files': files,
            'total_count': len(files)
        }, 'Files retrieved successfully')
    
    except Exception as e:
        logging.error(f'Failed to get conversation files: {str(e)}')
        return error_response(f'Failed to get files: {str(e)}', 500)


#! ADD/REMOVE PARTICIPANT (with notifications)
@chat_bp.route('/conversations/<int:conversation_id>/participants', methods=['POST'])
@jwt_required()
def add_participant(conversation_id):
    """Add participant to conversation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        user_id = data.get('user_id')
        role = data.get('role', 'member')
        
        if not user_id:
            return error_response('User ID is required', 400)
        
        conversation = ChatConversation.query.get(conversation_id)
        
        if not conversation:
            return error_response('Conversation not found', 404)
        
        if conversation.created_by_id != current_user_id:
            return error_response('Only conversation creator can add participants', 403)
        
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', 404)
        
        if conversation.is_user_participant(user_id):
            return error_response('User is already a participant', 400)
        
        conversation.add_participant(user, role)
        
        creator = User.query.get(current_user_id)
        notif_content = f"👥 {creator.get_full_name()} added {user.get_full_name()} to the conversation"
        
        notif_message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=current_user_id,
            original_content=notif_content,
            message_type='system',
            metadata_data={'action': 'participant_added', 'user_id': user_id},
            sender_timezone='UTC'
        )
        
        db.session.add(notif_message)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit WebSocket events
        if SOCKET_ENABLED:
            emit_new_message(conversation_id, notif_message.to_dict())
            emit_to_user(user_id, 'added_to_conversation', {
                'conversation': conversation.to_dict(for_user=user)
            })
        
        return success_response({
            'message': 'Participant added successfully',
            'notification': notif_message.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to add participant: {str(e)}')
        return error_response(f'Failed to add participant: {str(e)}', 500)


@chat_bp.route('/conversations/<int:conversation_id>/participants/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_participant(conversation_id, user_id):
    """Remove participant from conversation"""
    try:
        current_user_id = get_jwt_identity()
        
        conversation = ChatConversation.query.get(conversation_id)
        
        if not conversation:
            return error_response('Conversation not found', 404)
        
        if conversation.created_by_id != current_user_id:
            return error_response('Only conversation creator can remove participants', 403)
        
        if user_id == conversation.created_by_id:
            return error_response('Cannot remove conversation creator', 400)
        
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', 404)
        
        if not conversation.is_user_participant(user_id):
            return error_response('User is not a participant', 400)
        
        stmt = conversation_participants.update().where(
            (conversation_participants.c.conversation_id == conversation_id) &
            (conversation_participants.c.user_id == user_id)
        ).values(left_at=datetime.utcnow())

        db.session.execute(stmt)
        db.session.commit()

        
        creator = User.query.get(current_user_id)
        notif_content = f"👋 {user.get_full_name()} was removed from the conversation"
        
        notif_message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=current_user_id,
            original_content=notif_content,
            message_type='system',
            metadata_data={'action': 'participant_removed', 'user_id': user_id},
            sender_timezone='UTC'
        )
        
        db.session.add(notif_message)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit WebSocket events
        if SOCKET_ENABLED:
            emit_new_message(conversation_id, notif_message.to_dict())
            emit_to_user(user_id, 'removed_from_conversation', {
                'conversation_id': conversation_id
            })
        
        return success_response({
            'message': 'Participant removed successfully',
            'notification': notif_message.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to remove participant: {str(e)}')
        return error_response(f'Failed to remove participant: {str(e)}', 500)


#! DELETE CONVERSATION
@chat_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """Delete conversation (soft delete)"""
    try:
        current_user_id = get_jwt_identity()
        
        conversation = ChatConversation.query.get(conversation_id)
        
        if not conversation:
            return error_response('Conversation not found', 404)
        
        if conversation.created_by_id != current_user_id:
            return error_response('Only conversation creator can delete conversation', 403)
        
        # Don't allow deleting general chat
        if conversation.conversation_type == 'general':
            return error_response('Cannot delete the general chat', 403)
        
        if conversation.avatar_url:
            try:
                file_path = os.path.join(AVATAR_UPLOAD_FOLDER, os.path.basename(conversation.avatar_url))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.error(f'Failed to delete avatar: {str(e)}')
        
        participant_ids = [p.id for p in conversation.participants]
        
        stmt = conversation_participants.update().where(
            (conversation_participants.c.conversation_id == conversation_id) &
            (conversation_participants.c.user_id == current_user_id)
        ).values(left_at=datetime.utcnow())

        db.session.execute(stmt)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Notify all participants
        if SOCKET_ENABLED:
            for user_id in participant_ids:
                emit_to_user(user_id, 'conversation_deleted', {
                    'conversation_id': conversation_id
                })
        
        return success_response({'message': 'Conversation deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to delete conversation: {str(e)}')
        return error_response(f'Failed to delete conversation: {str(e)}', 500)
    
#testing

@chat_bp.route('/setup-general-chat', methods=['POST'])
@jwt_required()
def setup_general_chat():
    """One-time setup to create general chat"""
    from app.utils.chat_utils import get_or_create_general_chat, sync_all_users_to_general_chat
    
    current_user_id = get_jwt_identity()
    
    # Create general chat
    general_chat = get_or_create_general_chat(admin_user_id=current_user_id)
    
    # Sync all users
    stats = sync_all_users_to_general_chat()
    
    return success_response({
        'general_chat_id': general_chat.id,
        'sync_stats': stats
    }, 'General chat setup complete!')