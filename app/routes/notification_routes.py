from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.notification import Notification
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get all notifications with filtering"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    type_filter = request.args.get('type', type=str)
    is_read = request.args.get('is_read', type=bool)
    
    # Default to current user's notifications if no user_id specified
    if not user_id:
        user_id = current_user_id
    
    # Check if user is authorized to view other users' notifications
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response('Unauthorized to view other users notifications', 403)
    
    query = Notification.query.filter(Notification.user_id == user_id)
    
    if type_filter:
        query = query.filter(Notification.type == type_filter)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    result = paginate(query.order_by(Notification.created_at.desc()), page, per_page)
    
    return success_response({
        'notifications': [notification.to_dict() for notification in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@notifications_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    """Get single notification by ID"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.get(notification_id)
    if not notification:
        return error_response('Notification not found', 404)
    
    # Check if user is authorized to view this notification
    if notification.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view this notification', 403)
    
    return success_response({'notification': notification.to_dict()})

@notifications_bp.route('', methods=['POST'])
@jwt_required()
def create_notification():
    """Create new notification"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['user_id', 'title', 'message']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: user_id, title, message')
    
    # Check if user is authorized to create notifications for other users
    target_user_id = data['user_id']
    if target_user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to create notifications for other users', 403)
    
    try:
        notification = Notification(
            user_id=target_user_id,
            type=data.get('type', 'system'),
            title=data['title'],
            message=data['message'],
            data=data.get('data', {})
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return success_response({
            'notification': notification.to_dict()
        }, 'Notification created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create notification: {str(e)}', 500)

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.get(notification_id)
    if not notification:
        return error_response('Notification not found', 404)
    
    # Check if user is authorized to mark this notification as read
    if notification.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to mark this notification as read', 403)
    
    try:
        notification.mark_as_read()
        return success_response({
            'notification': notification.to_dict()
        }, 'Notification marked as read')
    except Exception as e:
        return error_response(f'Failed to mark notification as read: {str(e)}', 500)

@notifications_bp.route('/<int:notification_id>/unread', methods=['POST'])
@jwt_required()
def mark_notification_unread(notification_id):
    """Mark notification as unread"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.get(notification_id)
    if not notification:
        return error_response('Notification not found', 404)
    
    # Check if user is authorized to mark this notification as unread
    if notification.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to mark this notification as unread', 403)
    
    try:
        notification.mark_as_unread()
        return success_response({
            'notification': notification.to_dict()
        }, 'Notification marked as unread')
    except Exception as e:
        return error_response(f'Failed to mark notification as unread: {str(e)}', 500)

@notifications_bp.route('/batch/read', methods=['POST'])
@jwt_required()
def mark_notifications_read_batch():
    """Mark multiple notifications as read"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    notification_ids = data.get('notification_ids', [])
    
    if not notification_ids:
        return error_response('Notification IDs are required', 400)
    
    try:
        # Get notifications that belong to the current user
        notifications = Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user_id
        ).all()
        
        # If user is admin, allow marking any notifications as read
        if len(notifications) != len(notification_ids):
            current_user = User.query.get(current_user_id)
            if current_user and current_user.role == 'admin':
                notifications = Notification.query.filter(Notification.id.in_(notification_ids)).all()
            else:
                return error_response('Unauthorized to mark some notifications as read', 403)
        
        for notification in notifications:
            notification.mark_as_read()
        
        return success_response(message=f'{len(notifications)} notifications marked as read')
    except Exception as e:
        return error_response(f'Failed to mark notifications as read: {str(e)}', 500)

@notifications_bp.route('/user/<int:user_id>/unread-count', methods=['GET'])
@jwt_required()
def get_unread_notifications_count(user_id):
    """Get count of unread notifications for user"""
    current_user_id = get_jwt_identity()
    
    # Check if user is authorized to view other users' notification counts
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to view other users notification counts', 403)
    
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    return success_response({
        'user_id': user_id,
        'unread_count': count
    })

@notifications_bp.route('/my-unread-count', methods=['GET'])
@jwt_required()
def get_my_unread_notifications_count():
    """Get count of unread notifications for current user (convenience endpoint)"""
    current_user_id = get_jwt_identity()
    
    count = Notification.query.filter_by(user_id=current_user_id, is_read=False).count()
    
    return success_response({
        'user_id': current_user_id,
        'unread_count': count
    })

@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete notification"""
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.get(notification_id)
    if not notification:
        return error_response('Notification not found', 404)
    
    # Check if user is authorized to delete this notification
    if notification.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return error_response('Unauthorized to delete this notification', 403)
    
    try:
        db.session.delete(notification)
        db.session.commit()
        return success_response(message='Notification deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete notification: {str(e)}', 500)

@notifications_bp.route('/my-notifications', methods=['GET'])
@jwt_required()
def get_my_notifications():
    """Get current user's notifications (convenience endpoint)"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    type_filter = request.args.get('type', type=str)
    is_read = request.args.get('is_read', type=bool)
    
    query = Notification.query.filter(Notification.user_id == current_user_id)
    
    if type_filter:
        query = query.filter(Notification.type == type_filter)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    result = paginate(query.order_by(Notification.created_at.desc()), page, per_page)
    
    return success_response({
        'notifications': [notification.to_dict() for notification in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all current user's notifications as read"""
    current_user_id = get_jwt_identity()
    
    try:
        notifications = Notification.query.filter_by(
            user_id=current_user_id, 
            is_read=False
        ).all()
        
        for notification in notifications:
            notification.mark_as_read()
        
        return success_response(message=f'{len(notifications)} notifications marked as read')
    except Exception as e:
        return error_response(f'Failed to mark notifications as read: {str(e)}', 500)

@notifications_bp.route('/clear-read', methods=['DELETE'])
@jwt_required()
def clear_read_notifications():
    """Delete all read notifications for current user"""
    current_user_id = get_jwt_identity()
    
    try:
        deleted_count = Notification.query.filter_by(
            user_id=current_user_id, 
            is_read=True
        ).delete()
        
        db.session.commit()
        
        return success_response(message=f'{deleted_count} read notifications cleared')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to clear read notifications: {str(e)}', 500)