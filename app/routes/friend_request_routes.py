from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.friendRequest import FriendRequest
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from datetime import datetime, timedelta

friend_requests_bp = Blueprint('friend_requests', __name__, url_prefix='/api/friend-requests')

@friend_requests_bp.route('', methods=['GET'])
@jwt_required()
def get_friend_requests():
    """Get all friend requests with filtering"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    direction = request.args.get('direction', 'all')  # sent, received, all
    status = request.args.get('status', type=str)
    
    query = FriendRequest.query
    
    if direction == 'sent':
        query = query.filter_by(sender_id=current_user_id)
    elif direction == 'received':
        query = query.filter_by(receiver_id=current_user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    result = paginate(query.order_by(FriendRequest.created_at.desc()), page, per_page)
    
    return success_response({
        'friend_requests': [fr.to_dict(include_user_info=True) for fr in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@friend_requests_bp.route('/<int:request_id>', methods=['GET'])
@jwt_required()
def get_friend_request(request_id):
    """Get single friend request by ID"""
    friend_request = FriendRequest.query.get(request_id)
    if not friend_request:
        return error_response('Friend request not found', 404)
    
    current_user_id = get_jwt_identity()
    
    # Check if user is involved in this request
    if friend_request.sender_id != current_user_id and friend_request.receiver_id != current_user_id:
        return error_response('Access denied', 403)
    
    return success_response({
        'friend_request': friend_request.to_dict(include_user_info=True)
    })

#! THIS 
@friend_requests_bp.route('', methods=['POST'])
@jwt_required()
def create_friend_request():
    """Send friend request"""
    current_user_id = get_jwt_identity()
    
    data = request.get_json()
    
    required_fields = ['receiver_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required field: receiver_id')
    
    receiver_id = data['receiver_id']
    
    # Check if receiver exists
    receiver = User.query.get(receiver_id)
    if not receiver:
        return error_response('Receiver not found', 404)
    
    # Cannot send request to yourself
    if current_user_id == receiver_id:
        return error_response('Cannot send friend request to yourself', 400)
    
    # Check if request already exists
    existing_request = FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user_id) & (FriendRequest.receiver_id == receiver_id)) |
        ((FriendRequest.sender_id == receiver_id) & (FriendRequest.receiver_id == current_user_id))
    ).first()
    
    if existing_request:
        if existing_request.status == 'pending':
            return error_response('Friend request already pending', 400)
        elif existing_request.status == 'accepted':
            return error_response('Already friends with this user', 400)
    
    try:
        friend_request = FriendRequest(
            sender_id=current_user_id,
            receiver_id=receiver_id
        )
        
        db.session.add(friend_request)
        db.session.commit()
        
        return success_response({
            'friend_request': friend_request.to_dict(include_user_info=True)
        }, 'Friend request sent successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to send friend request: {str(e)}', 500)

#! and this
@friend_requests_bp.route('/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_friend_request(request_id):
    """Accept friend request"""
    current_user_id = get_jwt_identity()
    
    friend_request = FriendRequest.query.get(request_id)
    if not friend_request:
        return error_response('Friend request not found', 404)
    
    # Check if current user is the receiver
    if friend_request.receiver_id != current_user_id:
        return error_response('You can only accept requests sent to you', 403)
    
    if friend_request.status != 'pending':
        return error_response(f'Friend request is already {friend_request.status}', 400)
    
    try:
        friend_request.status = 'accepted'
        friend_request.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response({
            'friend_request': friend_request.to_dict(include_user_info=True)
        }, 'Friend request accepted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to accept friend request: {str(e)}', 500)

#! and this
@friend_requests_bp.route('/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_friend_request(request_id):
    """Reject friend request"""
    current_user_id = get_jwt_identity()
    
    friend_request = FriendRequest.query.get(request_id)
    if not friend_request:
        return error_response('Friend request not found', 404)
    
    # Check if current user is the receiver
    if friend_request.receiver_id != current_user_id:
        return error_response('You can only reject requests sent to you', 403)
    
    if friend_request.status != 'pending':
        return error_response(f'Friend request is already {friend_request.status}', 400)
    
    try:
        friend_request.status = 'rejected'
        friend_request.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response({
            'friend_request': friend_request.to_dict(include_user_info=True)
        }, 'Friend request rejected successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to reject friend request: {str(e)}', 500)

#!and this sender
@friend_requests_bp.route('/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_friend_request(request_id):
    """Cancel sent friend request"""
    current_user_id = get_jwt_identity()
    
    friend_request = FriendRequest.query.get(request_id)
    if not friend_request:
        return error_response('Friend request not found', 404)
    
    # Check if current user is the sender
    if friend_request.sender_id != current_user_id:
        return error_response('You can only cancel requests sent by you', 403)
    
    if friend_request.status != 'pending':
        return error_response(f'Friend request is already {friend_request.status}', 400)
    
    try:
        db.session.delete(friend_request)
        db.session.commit()
        
        return success_response(message='Friend request cancelled successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to cancel friend request: {str(e)}', 500)

#! and this
@friend_requests_bp.route('/<int:request_id>', methods=['DELETE'])
@jwt_required()
def delete_friend_request(request_id):
    """Delete friend request (for cleanup)"""
    current_user_id = get_jwt_identity()
    
    friend_request = FriendRequest.query.get(request_id)
    if not friend_request:
        return error_response('Friend request not found', 404)
    
    # Check if current user is involved in this request
    if friend_request.sender_id != current_user_id and friend_request.receiver_id != current_user_id:
        return error_response('Access denied', 403)
    
    try:
        db.session.delete(friend_request)
        db.session.commit()
        return success_response(message='Friend request deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete friend request: {str(e)}', 500)

#! this in both
@friend_requests_bp.route('/check', methods=['GET'])
@jwt_required()
def check_friend_status():
    """Check friendship status between users"""
    current_user_id = get_jwt_identity()
    other_user_id = request.args.get('other_user_id', type=int)
    
    if not other_user_id:
        return error_response('Missing other_user_id parameter', 400)
    
    # Check if other user exists
    other_user = User.query.get(other_user_id)
    if not other_user:
        return error_response('User not found', 404)
    
    # Find any existing friend request
    friend_request = FriendRequest.query.filter(
        ((FriendRequest.sender_id == current_user_id) & (FriendRequest.receiver_id == other_user_id)) |
        ((FriendRequest.sender_id == other_user_id) & (FriendRequest.receiver_id == current_user_id))
    ).first()
    
    status = 'none'
    if friend_request:
        status = friend_request.status
        if status == 'accepted':
            status = 'friends'
    
    return success_response({
        'status': status,
        'friend_request': friend_request.to_dict(include_user_info=True) if friend_request else None,
        'users': {
            'current_user_id': current_user_id,
            'other_user_id': other_user_id
        }
    })