"""
SF Collab Notification Routes - MERGED VERSION
Combines your existing routes + new functionality
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.notification import Notification
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from app.notifications.service import notification_service
import logging
import json

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)


# ============================================
# EXISTING ROUTES (KEPT AS-IS)
# ============================================

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
        query = query.filter(Notification.notification_type == type_filter)
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
    
    target_user_id = data['user_id']
    safe_data = data.get('data', {})

    if not isinstance(safe_data, (dict, list)):
        safe_data = {}
    
    try:
        notification = Notification(
            user_id=target_user_id,
            notification_type=data.get('type', 'system'),
            title=data['title'],
            message=data['message'],
            data=json.loads(json.dumps(safe_data)),
            is_read=data.get('isRead', False)
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # NEW: Send real-time notification via Socket.IO
        try:
            notification_service.send_realtime_notification(notification)
        except Exception as e:
            logger.error(f"Failed to send real-time notification: {e}")
        
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
            notifications = Notification.query.filter(Notification.id.in_(notification_ids)).all()

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


# ============================================
# NEW ROUTES (ADDED FUNCTIONALITY)
# ============================================

@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_current_user_unread_count():
    """
    NEW: Get unread count for current user (simpler endpoint)
    Frontend friendly - no need to pass user_id
    """
    current_user_id = get_jwt_identity()
    
    try:
        count = notification_service.get_unread_count(current_user_id)
        return success_response({
            'unreadCount': count
        })
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return error_response("Failed to get unread count", 500)


@notifications_bp.route('/mark-all-read', methods=['PUT', 'PATCH', 'POST'])
@jwt_required()
def mark_all_read():
    """
    NEW: Mark all notifications as read for the current user
    """
    current_user_id = get_jwt_identity()
    
    try:
        count = notification_service.mark_all_as_read(current_user_id)
        return success_response({
            'message': f'Marked {count} notifications as read',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        return error_response("Failed to mark all notifications as read", 500)


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """
    NEW: Delete a notification
    """
    current_user_id = get_jwt_identity()
    
    try:
        success = notification_service.delete_notification(notification_id, current_user_id)
        
        if not success:
            return error_response('Failed to delete notification', 400)
        
        return success_response({
            'message': 'Notification deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        return error_response("Failed to delete notification", 500)


@notifications_bp.route('/delete-all-read', methods=['DELETE'])
@jwt_required()
def delete_all_read():
    """
    NEW: Delete all read notifications for the current user
    """
    current_user_id = get_jwt_identity()
    
    try:
        read_notifications = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=True
        ).all()
        
        count = len(read_notifications)
        for notification in read_notifications:
            db.session.delete(notification)
        
        db.session.commit()
        
        return success_response({
            'message': f'Deleted {count} read notifications',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error deleting read notifications: {e}")
        db.session.rollback()
        return error_response("Failed to delete read notifications", 500)


@notifications_bp.route('/bulk/mark-read', methods=['POST'])
@jwt_required()
def bulk_mark_read():
    """
    NEW: Alternative bulk mark as read endpoint (frontend friendly naming)
    This complements your existing /batch/read endpoint
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        notification_ids = data.get('notificationIds', [])
        
        if not notification_ids:
            return error_response('No notification IDs provided', 400)
        
        # Get notifications
        notifications = Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user_id
        ).all()
        
        # Mark as read
        count = 0
        for notification in notifications:
            notification.mark_as_read()
            count += 1
        
        return success_response({
            'message': f'Marked {count} notifications as read',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error in bulk mark read: {e}")
        return error_response("Failed to mark notifications as read", 500)


@notifications_bp.route('/bulk/delete', methods=['POST'])
@jwt_required()
def bulk_delete():
    """
    NEW: Delete multiple notifications
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        notification_ids = data.get('notificationIds', [])
        
        if not notification_ids:
            return error_response('No notification IDs provided', 400)
        
        # Get and delete notifications
        notifications = Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user_id
        ).all()
        
        count = len(notifications)
        for notification in notifications:
            db.session.delete(notification)
        
        db.session.commit()
        
        return success_response({
            'message': f'Deleted {count} notifications',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        db.session.rollback()
        return error_response("Failed to delete notifications", 500)


@notifications_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    NEW: Get notification statistics for current user
    """
    current_user_id = get_jwt_identity()
    
    try:
        total = Notification.query.filter_by(user_id=current_user_id).count()
        unread = Notification.query.filter_by(user_id=current_user_id, is_read=False).count()
        read = total - unread
        
        # Stats by type
        type_stats = db.session.query(
            Notification.notification_type,
            db.func.count(Notification.id)
        ).filter_by(user_id=current_user_id).group_by(Notification.notification_type).all()
        
        type_breakdown = {type_name: count for type_name, count in type_stats}
        
        return success_response({
            'stats': {
                'total': total,
                'unread': unread,
                'read': read,
                'typeBreakdown': type_breakdown
            }
        })
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        return error_response("Failed to get notification stats", 500)


@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """
    NEW: Get notification preferences for current user
    TODO: Implement actual user preferences storage
    """
    current_user_id = get_jwt_identity()
    
    # Default preferences (TODO: get from database)
    default_preferences = {
        'email_enabled': True,
        'push_enabled': True,
        'in_app_enabled': True,
        'categories': {
            'account': True,
            'social': True,
            'task': True,
            'message': True,
            'idea': True,
            'startup': True,
            'reward': True,
            'event': True
        },
        'priority_threshold': 'low',
        'digest_frequency': 'daily',
        'muted_users': [],
        'muted_startups': [],
        'do_not_disturb': {
            'enabled': False,
            'start_time': '22:00',
            'end_time': '08:00'
        }
    }
    
    return success_response({
        'preferences': default_preferences
    })


@notifications_bp.route('/preferences', methods=['PUT', 'PATCH'])
@jwt_required()
def update_preferences():
    """
    NEW: Update notification preferences
    TODO: Implement actual preferences storage
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # TODO: Save preferences to database
    
    return success_response({
        'message': 'Preferences updated successfully',
        'preferences': data
    })