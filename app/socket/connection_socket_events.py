from flask_socketio import emit
from app.extensions import socketio

# If you're using a different socket setup, adjust accordingly


def emit_new_connection_request(receiver_id, sender_data):
    """
    Emit event when a new connection request is sent.
    Called after successfully creating a connection request.
    
    Args:
        receiver_id: ID of the user receiving the request
        sender_data: Dict with sender info (id, first_name, last_name, etc.)
    """
    event_data = {
        'type': 'new_request',
        'sender_id': sender_data.get('id'),
        'sender_name': f"{sender_data.get('first_name', '')} {sender_data.get('last_name', '')}".strip(),
        'sender': sender_data,
        'message': f"{sender_data.get('first_name', 'Someone')} wants to connect with you"
    }
    
    # Emit to the receiver's room (assuming room = user_id)
    try:
        socketio.emit('connection_request', event_data, room=str(receiver_id))
        socketio.emit('connection_request_received', event_data, room=str(receiver_id))
    except Exception as e:
        print(f"Failed to emit connection_request event: {e}")


def emit_connection_accepted(sender_id, accepter_data):
    """
    Emit event when a connection request is accepted.
    Called after successfully accepting a connection request.
    
    Args:
        sender_id: ID of the user who sent the original request
        accepter_data: Dict with accepter info (id, first_name, last_name, etc.)
    """
    event_data = {
        'type': 'accepted',
        'accepter_id': accepter_data.get('id'),
        'accepter_name': f"{accepter_data.get('first_name', '')} {accepter_data.get('last_name', '')}".strip(),
        'accepter': accepter_data,
        'message': f"{accepter_data.get('first_name', 'Someone')} accepted your connection request"
    }
    
    # Emit to the original sender's room
    try:
        socketio.emit('connection_accepted', event_data, room=str(sender_id))
        socketio.emit('connection_request_accepted', event_data, room=str(sender_id))
    except Exception as e:
        print(f"Failed to emit connection_accepted event: {e}")


def emit_connection_declined(sender_id, decliner_data):
    """
    Emit event when a connection request is declined.
    Optional - you may not want to notify users of declines.
    
    Args:
        sender_id: ID of the user who sent the original request
        decliner_data: Dict with decliner info
    """
    event_data = {
        'type': 'declined',
        'decliner_id': decliner_data.get('id'),
        'decliner_name': f"{decliner_data.get('first_name', '')} {decliner_data.get('last_name', '')}".strip(),
    }
    
    try:
        socketio.emit('connection_declined', event_data, room=str(sender_id))
    except Exception as e:
        print(f"Failed to emit connection_declined event: {e}")


def emit_connection_removed(other_user_id, remover_data):
    """
    Emit event when a connection is removed.
    Optional - you may not want to notify users of removals.
    
    Args:
        other_user_id: ID of the other user in the connection
        remover_data: Dict with remover info
    """
    event_data = {
        'type': 'removed',
        'remover_id': remover_data.get('id'),
        'remover_name': f"{remover_data.get('first_name', '')} {remover_data.get('last_name', '')}".strip(),
    }
    
    try:
        socketio.emit('connection_removed', event_data, room=str(other_user_id))
    except Exception as e:
        print(f"Failed to emit connection_removed event: {e}")


# =============================================================================
# INTEGRATION EXAMPLE
# =============================================================================
# 
# In your connection_routes.py, after successful actions:
#
# from app.socket.connection_events import (
#     emit_new_connection_request,
#     emit_connection_accepted
# )
#
# @connections_bp.route('/request', methods=['POST'])
# @jwt_required()
# def send_connection_request():
#     # ... existing code ...
#     
#     # After creating the request successfully:
#     current_user = User.query.get(current_user_id)
#     emit_new_connection_request(
#         receiver_id=receiver_id,
#         sender_data={
#             'id': current_user.id,
#             'first_name': current_user.first_name,
#             'last_name': current_user.last_name,
#             'email': current_user.email,
#         }
#     )
#     
#     return success_response(...)
#
#
# @connections_bp.route('/request/<int:request_id>/accept', methods=['POST'])
# @jwt_required()
# def accept_connection_request(request_id):
#     # ... existing code ...
#     
#     # After accepting the request:
#     current_user = User.query.get(current_user_id)
#     emit_connection_accepted(
#         sender_id=conn_request.sender_id,
#         accepter_data={
#             'id': current_user.id,
#             'first_name': current_user.first_name,
#             'last_name': current_user.last_name,
#         }
#     )
#     
#     return success_response(...)
