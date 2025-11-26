from flask import Blueprint, request, jsonify
from app.models.chatConversation import ChatConversation, conversation_participants
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

conversations_bp = Blueprint('conversations', __name__, url_prefix='/api/conversations')

@conversations_bp.route('', methods=['GET'])
def get_conversations():
    """Get all conversations for a user"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return error_response('User ID is required', 400)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Get user's conversations
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)
    
    query = ChatConversation.query\
        .join(conversation_participants)\
        .filter(conversation_participants.c.user_id == user_id)\
        .filter(ChatConversation.is_active == True)
    
    result = paginate(query.order_by(ChatConversation.updated_at.desc()), page, per_page)
    
    return success_response({
        'conversations': [conv.to_dict(for_user=user) for conv in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@conversations_bp.route('/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get single conversation"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return error_response('User ID is required', 400)
    
    user = User.query.get(user_id)
    conversation = ChatConversation.query.get(conversation_id)
    
    if not user or not conversation:
        return error_response('User or conversation not found', 404)
    
    if not conversation.is_user_participant(user_id):
        return error_response('Access denied', 403)
    
    return success_response({
        'conversation': conversation.to_dict(for_user=user)
    })

@conversations_bp.route('', methods=['POST'])
def create_conversation():
    """Create new conversation"""
    data = request.get_json()
    
    required_fields = ['created_by_id', 'participant_ids']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: created_by_id, participant_ids')
    
    creator = User.query.get(data['created_by_id'])
    if not creator:
        return error_response('Creator not found', 404)
    
    try:
        # Create conversation
        conversation = ChatConversation(
            name=data.get('name'),
            conversation_type=data.get('conversation_type', 'direct'),
            created_by_id=creator.id,
            description=data.get('description'),
            avatar_url=data.get('avatar_url')
        )
        
        db.session.add(conversation)
        db.session.flush()  # Get the ID without committing
        
        # Add participants
        participant_ids = data['participant_ids']
        participants = User.query.filter(User.id.in_(participant_ids)).all()
        
        # Add creator as participant
        conversation.add_participant(creator, 'admin')
        
        # Add other participants
        for participant in participants:
            if participant.id != creator.id:
                conversation.add_participant(participant, 'member')
        
        db.session.commit()
        
        return success_response({
            'conversation': conversation.to_dict(for_user=creator)
        }, 'Conversation created successfully', 201)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create conversation: {str(e)}', 500)

@conversations_bp.route('/<int:conversation_id>/participants', methods=['POST'])
def add_participant(conversation_id):
    """Add participant to conversation"""
    data = request.get_json()
    user_id = data.get('user_id')
    role = data.get('role', 'member')
    
    if not user_id:
        return error_response('User ID is required', 400)
    
    user = User.query.get(user_id)
    conversation = ChatConversation.query.get(conversation_id)
    
    if not user or not conversation:
        return error_response('User or conversation not found', 404)
    
    try:
        conversation.add_participant(user, role)
        return success_response(message='Participant added successfully')
    except Exception as e:
        return error_response(f'Failed to add participant: {str(e)}', 500)

@conversations_bp.route('/<int:conversation_id>/participants/<int:user_id>', methods=['DELETE'])
def remove_participant(conversation_id, user_id):
    """Remove participant from conversation"""
    user = User.query.get(user_id)
    conversation = ChatConversation.query.get(conversation_id)
    
    if not user or not conversation:
        return error_response('User or conversation not found', 404)
    
    try:
        conversation.remove_participant(user)
        return success_response(message='Participant removed successfully')
    except Exception as e:
        return error_response(f'Failed to remove participant: {str(e)}', 500)

@conversations_bp.route('/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete conversation (soft delete)"""
    conversation = ChatConversation.query.get(conversation_id)
    if not conversation:
        return error_response('Conversation not found', 404)
    
    try:
        conversation.is_active = False
        db.session.commit()
        return success_response(message='Conversation deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete conversation: {str(e)}', 500)