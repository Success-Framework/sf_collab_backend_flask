

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.friendRequest import FriendRequest
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from sqlalchemy import or_, and_
from datetime import datetime

connections_bp = Blueprint('connections', __name__)


# =============================================================================
# HELPER: Get user profile data
# =============================================================================

def get_user_profile_data(user):
    """Extract user profile data for API responses"""
    if not user:
        return None
    
    profile_data = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }
    
    # Try to get profile picture from different possible locations
    if hasattr(user, 'profile_picture') and user.profile_picture:
        profile_data['profile_picture'] = user.profile_picture
    elif hasattr(user, 'profile') and user.profile and hasattr(user.profile, 'picture'):
        profile_data['profile_picture'] = user.profile.picture
    else:
        profile_data['profile_picture'] = None
    
    # Try to get title
    if hasattr(user, 'title'):
        profile_data['title'] = user.title
    elif hasattr(user, 'profile') and user.profile and hasattr(user.profile, 'title'):
        profile_data['title'] = user.profile.title
    else:
        profile_data['title'] = None
    
    # Try to get company
    if hasattr(user, 'company'):
        profile_data['company'] = user.company
    elif hasattr(user, 'profile') and user.profile and hasattr(user.profile, 'company'):
        profile_data['company'] = user.profile.company
    else:
        profile_data['company'] = None
    
    # Try to get bio
    if hasattr(user, 'bio'):
        profile_data['bio'] = user.bio
    elif hasattr(user, 'profile') and user.profile and hasattr(user.profile, 'bio'):
        profile_data['bio'] = user.profile.bio
    else:
        profile_data['bio'] = None
    
    return profile_data


# =============================================================================
# SEND CONNECTION REQUEST
# =============================================================================

@connections_bp.route('/request', methods=['POST'])
@jwt_required()
def send_connection_request():
    """
    Send a connection request to another user.
    
    Request Body:
        { "receiver_id": 123 }
    
    Behavior:
        - Prevents self-requests
        - Prevents duplicate pending requests
        - If already connected, returns error
        - If previously declined, allows re-request
        - If they already sent us a request, returns error (user should accept instead)
    
    Returns:
        201: Request sent successfully
        400: Invalid request
        404: User not found
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'receiver_id' not in data:
        return error_response('Missing receiver_id', 400)
    
    receiver_id = data['receiver_id']
    
    # RULE: Prevent self-request
    if current_user_id == receiver_id:
        return error_response('Cannot send connection request to yourself', 400)
    
    # Check receiver exists
    receiver = User.query.get(receiver_id)
    if not receiver:
        return error_response('User not found', 404)
    
    # Check for existing request in EITHER direction
    existing = FriendRequest.query.filter(
        or_(
            and_(
                FriendRequest.sender_id == current_user_id,
                FriendRequest.receiver_id == receiver_id
            ),
            and_(
                FriendRequest.sender_id == receiver_id,
                FriendRequest.receiver_id == current_user_id
            )
        )
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            # RULE: Already connected
            return error_response('Already connected with this user', 400)
        
        elif existing.status == 'pending':
            if existing.sender_id == current_user_id:
                # RULE: Prevent duplicate - already sent
                return error_response('Connection request already sent', 400)
            else:
                # They sent us a request - tell user to accept instead
                return error_response('This user has already sent you a connection request. Check your incoming requests.', 400)
        
        elif existing.status == 'rejected':
            # RULE: Allow re-request after decline
            # Reset the request with current user as sender
            existing.sender_id = current_user_id
            existing.receiver_id = receiver_id
            existing.status = 'pending'
            existing.created_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
            db.session.commit()
            
            return success_response({
                'request': {
                    'id': existing.id,
                    'receiver': get_user_profile_data(receiver),
                    'status': 'pending',
                    'created_at': existing.created_at.isoformat()
                }
            }, 'Connection request sent', 201)
    
    # Create new request
    try:
        new_request = FriendRequest(
            sender_id=current_user_id,
            receiver_id=receiver_id,
            status='pending'
        )
        db.session.add(new_request)
        db.session.commit()
        
        return success_response({
            'request': {
                'id': new_request.id,
                'receiver': get_user_profile_data(receiver),
                'status': 'pending',
                'created_at': new_request.created_at.isoformat()
            }
        }, 'Connection request sent', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to send request: {str(e)}', 500)


# =============================================================================
# ACCEPT CONNECTION REQUEST
# =============================================================================

@connections_bp.route('/request/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_connection_request(request_id):
    current_user_id = int(get_jwt_identity())

    conn_request = FriendRequest.query.get(request_id)
    if not conn_request:
        return error_response('Connection request not found', 404)

    print("ACCEPT DEBUG:", {
        "jwt_identity": get_jwt_identity(),
        "jwt_type": str(type(get_jwt_identity())),
        "current_user_id": current_user_id,
        "receiver_id": conn_request.receiver_id,
        "receiver_type": str(type(conn_request.receiver_id)),
        "sender_id": conn_request.sender_id,
        "status": conn_request.status
    })

    if conn_request.receiver_id != current_user_id:
        return error_response('You can only accept requests sent to you', 403)

    if conn_request.status != 'pending':
        return error_response(f'Request is already {conn_request.status}', 400)


    
    try:
        conn_request.status = 'accepted'
        conn_request.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Get the sender info for response
        sender = User.query.get(conn_request.sender_id)
        
        return success_response({
            'connection': {
                'id': conn_request.id,
                'connected_user': get_user_profile_data(sender),
                'connected_at': conn_request.updated_at.isoformat()
            }
        }, 'Connection request accepted! You are now connected.')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to accept request: {str(e)}', 500)
    


# =============================================================================
# DECLINE CONNECTION REQUEST
# =============================================================================

@connections_bp.route('/request/<int:request_id>/decline', methods=['POST'])
@jwt_required()
def decline_connection_request(request_id):
    """
    Decline an incoming connection request.
    
    Behavior:
        - Only the receiver can decline
        - Request is marked as 'rejected' (allows re-request later)
        - No connection is created
    
    Returns:
        200: Request declined
        403: Not the receiver
        404: Request not found
    """
    current_user_id = int(get_jwt_identity())
    
    conn_request = FriendRequest.query.get(request_id)
    if not conn_request:
        return error_response('Connection request not found', 404)
    
    # Only receiver can decline
    if conn_request.receiver_id != current_user_id:
        return error_response('You can only decline requests sent to you', 403)
    
    if conn_request.status != 'pending':
        return error_response(f'Request is already {conn_request.status}', 400)
    
    try:
        # Mark as rejected - this allows sender to re-request later
        conn_request.status = 'rejected'
        conn_request.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(message='Connection request declined')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to decline request: {str(e)}', 500)


# =============================================================================
# CANCEL SENT REQUEST
# =============================================================================

@connections_bp.route('/request/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_connection_request(request_id):
    """
    Cancel a connection request you sent.
    
    Behavior:
        - Only the sender can cancel
        - Request is deleted
    
    Returns:
        200: Request cancelled
        403: Not the sender
        404: Request not found
    """
    current_user_id = int(get_jwt_identity())
    
    conn_request = FriendRequest.query.get(request_id)
    if not conn_request:
        return error_response('Connection request not found', 404)
    
    # Only sender can cancel
    if conn_request.sender_id != current_user_id:
        return error_response('You can only cancel requests you sent', 403)
    
    if conn_request.status != 'pending':
        return error_response(f'Request is already {conn_request.status}', 400)
    
    try:
        db.session.delete(conn_request)
        db.session.commit()
        
        return success_response(message='Connection request cancelled')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to cancel request: {str(e)}', 500)


# =============================================================================
# REMOVE CONNECTION
# =============================================================================

@connections_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_connection(user_id):
    """
    Remove a connection with another user.
    
    Behavior:
        - Either user can remove the connection
        - Deletes the relationship for BOTH users
    
    Returns:
        200: Connection removed
        404: Connection not found
    """
    current_user_id = int(get_jwt_identity())
    
    if current_user_id == user_id:
        return error_response('Invalid request', 400)
    
    # Find the accepted connection (in either direction)
    connection = FriendRequest.query.filter(
        FriendRequest.status == 'accepted',
        or_(
            and_(
                FriendRequest.sender_id == current_user_id,
                FriendRequest.receiver_id == user_id
            ),
            and_(
                FriendRequest.sender_id == user_id,
                FriendRequest.receiver_id == current_user_id
            )
        )
    ).first()
    
    if not connection:
        return error_response('Connection not found', 404)
    
    try:
        db.session.delete(connection)
        db.session.commit()
        
        return success_response(message='Connection removed')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to remove connection: {str(e)}', 500)


# =============================================================================
# LIST ALL CONNECTIONS
# =============================================================================

@connections_bp.route('', methods=['GET'])
@jwt_required()
def get_connections():
    """
    Get all accepted connections for current user.
    
    Shows:
        - Name
        - Basic profile info
        - Connected date
    
    Query Params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - search: Search by name
    
    Returns:
        List of connections with user info
    """
    current_user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str).strip().lower()
    
    # Get all accepted connections
    query = FriendRequest.query.filter(
        FriendRequest.status == 'accepted',
        or_(
            FriendRequest.sender_id == current_user_id,
            FriendRequest.receiver_id == current_user_id
        )
    ).order_by(FriendRequest.updated_at.desc())
    
    # Get all results then filter (for search)
    all_connections = query.all()
    
    connections = []
    for conn in all_connections:
        # Get the OTHER user
        if conn.sender_id == current_user_id:
            connected_user = User.query.get(conn.receiver_id)
        else:
            connected_user = User.query.get(conn.sender_id)
        
        if not connected_user:
            continue
        
        # Apply search filter
        if search:
            full_name = f"{connected_user.first_name or ''} {connected_user.last_name or ''}".lower()
            email = (connected_user.email or '').lower()
            if search not in full_name and search not in email:
                continue
        
        connections.append({
            'id': conn.id,
            'connected_user': get_user_profile_data(connected_user),
            'connected_at': (conn.updated_at or conn.created_at).isoformat()
        })
    
    # Manual pagination
    total = len(connections)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = connections[start:end]
    
    return success_response({
        'connections': paginated,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page if total > 0 else 1
        }
    })


# =============================================================================
# LIST INCOMING REQUESTS
# =============================================================================

@connections_bp.route('/requests/incoming', methods=['GET'])
@jwt_required()
def get_incoming_requests():
    """
    Get pending connection requests sent TO current user.
    
    These are requests the user can Accept or Decline.
    
    Query Params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
    
    Returns:
        List of incoming pending requests with sender info
    """
    current_user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = FriendRequest.query.filter(
        FriendRequest.receiver_id == current_user_id,
        FriendRequest.status == 'pending'
    ).order_by(FriendRequest.created_at.desc())
    
    result = paginate(query, page, per_page)
    
    requests = []
    for req in result['items']:
        sender = User.query.get(req.sender_id)
        if sender:
            requests.append({
                'id': req.id,
                'sender': get_user_profile_data(sender),
                'created_at': req.created_at.isoformat()
            })
    
    return success_response({
        'requests': requests,
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


# =============================================================================
# LIST OUTGOING REQUESTS
# =============================================================================

@connections_bp.route('/requests/outgoing', methods=['GET'])
@jwt_required()
def get_outgoing_requests():
    """
    Get pending connection requests sent BY current user.
    
    These are requests waiting for the other user to Accept/Decline.
    User can cancel these.
    
    Query Params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
    
    Returns:
        List of outgoing pending requests with receiver info
    """
    current_user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = FriendRequest.query.filter(
        FriendRequest.sender_id == current_user_id,
        FriendRequest.status == 'pending'
    ).order_by(FriendRequest.created_at.desc())
    
    result = paginate(query, page, per_page)
    
    requests = []
    for req in result['items']:
        receiver = User.query.get(req.receiver_id)
        if receiver:
            requests.append({
                'id': req.id,
                'receiver': get_user_profile_data(receiver),
                'created_at': req.created_at.isoformat()
            })
    
    return success_response({
        'requests': requests,
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


# =============================================================================
# GET CONNECTION STATUS
# =============================================================================

@connections_bp.route('/status/<int:user_id>', methods=['GET'])
@jwt_required()
def get_connection_status(user_id):
    """
    Get the connection status between current user and another user.
    
    Used by frontend to determine button state:
        - 'none' → Show "Connect" button
        - 'request_sent' → Show "Request Sent" (disabled)
        - 'request_received' → Show "Accept" / "Decline"
        - 'connected' → Show "Connected" / "Remove Connection"
    
    Returns:
        status: 'none' | 'request_sent' | 'request_received' | 'connected'
        request_id: ID of the request/connection (if exists)
    """
    current_user_id = int(get_jwt_identity())
    
    # Self check
    if current_user_id == user_id:
        return success_response({
            'status': 'self',
            'request_id': None
        })
    
    # Find any non-rejected request between users
    connection = FriendRequest.query.filter(
        or_(
            and_(
                FriendRequest.sender_id == current_user_id,
                FriendRequest.receiver_id == user_id
            ),
            and_(
                FriendRequest.sender_id == user_id,
                FriendRequest.receiver_id == current_user_id
            )
        ),
        FriendRequest.status.in_(['pending', 'accepted'])
    ).first()
    
    if not connection:
        # No connection → "Connect"
        return success_response({
            'status': 'none',
            'request_id': None
        })
    
    if connection.status == 'accepted':
        # Connected → "Connected" / "Remove Connection"
        return success_response({
            'status': 'connected',
            'request_id': connection.id
        })
    
    # Pending request
    if connection.sender_id == current_user_id:
        # I sent the request → "Request Sent" (disabled)
        return success_response({
            'status': 'request_sent',
            'request_id': connection.id
        })
    else:
        # They sent me a request → "Accept" / "Decline"
        return success_response({
            'status': 'request_received',
            'request_id': connection.id
        })


# =============================================================================
# GET COUNTS (for notification badges)
# =============================================================================

@connections_bp.route('/counts', methods=['GET'])
@jwt_required()
def get_connection_counts():
    """
    Get counts for badges/notifications.
    
    Returns:
        connections: Total accepted connections
        incoming: Pending incoming requests (needs action)
        outgoing: Pending outgoing requests
    """
    current_user_id = int(get_jwt_identity())
    
    connections = FriendRequest.query.filter(
        FriendRequest.status == 'accepted',
        or_(
            FriendRequest.sender_id == current_user_id,
            FriendRequest.receiver_id == current_user_id
        )
    ).count()
    
    incoming = FriendRequest.query.filter(
        FriendRequest.receiver_id == current_user_id,
        FriendRequest.status == 'pending'
    ).count()
    
    outgoing = FriendRequest.query.filter(
        FriendRequest.sender_id == current_user_id,
        FriendRequest.status == 'pending'
    ).count()
    
    return success_response({
        'connections': connections,
        'incoming': incoming,
        'outgoing': outgoing
    })
