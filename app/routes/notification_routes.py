from flask import Blueprint, request, jsonify
from app.models.notification import Notification
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('', methods=['GET'])
def get_notifications():
    """Get all notifications with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    type_filter = request.args.get('type', type=str)
    is_read = request.args.get('is_read', type=bool)
    
    query = Notification.query
    
    if user_id:
        query = query.filter(Notification.user_id == user_id)
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
def get_notification(notification_id):
    """Get single notification by ID"""
    notification = Notification.query.get(notification_id)
    if not notification:
        return error_response('Notification not found', 404)
    
    return success_response({'notification': notification.to_dict()})

@notifications_bp.route('', methods=['POST'])
def create_notification():
    """Create new notification"""
    data = request.get_json()
    
    required_fields = ['user_id', 'title', 'message']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: user_id, title, message')
    
    try:
        notification = Notification(
            user_id=data['user_id'],
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
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get(notification_id)
    if not notification:
        return error_response('Notification not found', 404)
    
    try:
        notification.mark_as_read()
        return success_response({
            'notification': notification.to_dict()
        }, 'Notification marked as read')
    except Exception as e:
        return error_response(f'Failed to mark notification as read: {str(e)}', 500)

@notifications_bp.route('/<int:notification_id>/unread', methods=['POST'])
def mark_notification_unread(notification_id):
    """Mark notification as unread"""
    notification = Notification.query.get(notification_id)
    if not notification:
        return error_response('Notification not found', 404)
    
    try:
        notification.mark_as_unread()
        return success_response({
            'notification': notification.to_dict()
        }, 'Notification marked as unread')
    except Exception as e:
        return error_response(f'Failed to mark notification as unread: {str(e)}', 500)

@notifications_bp.route('/batch/read', methods=['POST'])
def mark_notifications_read_batch():
    """Mark multiple notifications as read"""
    data = request.get_json()
    notification_ids = data.get('notification_ids', [])
    
    if not notification_ids:
        return error_response('Notification IDs are required', 400)
    
    try:
        notifications = Notification.query.filter(Notification.id.in_(notification_ids)).all()
        for notification in notifications:
            notification.mark_as_read()
        
        return success_response(message=f'{len(notifications)} notifications marked as read')
    except Exception as e:
        return error_response(f'Failed to mark notifications as read: {str(e)}', 500)

@notifications_bp.route('/user/<int:user_id>/unread-count', methods=['GET'])
def get_unread_notifications_count(user_id):
    """Get count of unread notifications for user"""
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    return success_response({
        'user_id': user_id,
        'unread_count': count
    })

@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete notification"""
    notification = Notification.query.get(notification_id)
    if not notification:
        return error_response('Notification not found', 404)
    
    try:
        db.session.delete(notification)
        db.session.commit()
        return success_response(message='Notification deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete notification: {str(e)}', 500)