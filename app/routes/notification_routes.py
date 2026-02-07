"""
Notification Routes

API endpoints for notification management.
FIXED VERSION - Correct method signatures to match service.py
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.helper import success_response, error_response
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

notification_bp = Blueprint('notifications', __name__)

# ============================================
# SAFE IMPORT - Won't break routes if service is missing
# ============================================
try:
    from app.notifications.service import NotificationService
    notification_service = NotificationService()
    HAS_NOTIFICATION_SERVICE = True
except Exception as e:
    logger.warning(f"Notification service not available: {e}")
    notification_service = None
    HAS_NOTIFICATION_SERVICE = False


# ─────────────────────────────────────────────────────────────
# GET ALL NOTIFICATIONS - FIXED
# ─────────────────────────────────────────────────────────────
@notification_bp.route('', methods=['GET'])
@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_notifications():
    """Get paginated notifications for current user (supports filters)"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        notification_type = request.args.get('type')
        priority = request.args.get('priority')
        is_read = request.args.get('is_read')

        # Convert is_read to boolean if provided
        if is_read is not None:
            is_read = str(is_read).lower() in ('true', '1', 'yes')

        # Build filters dict - THIS IS THE FIX
        filters = {}
        if category:
            filters['category'] = category
        if notification_type:
            filters['type'] = notification_type
        if priority:
            filters['priority'] = priority
        if is_read is not None:
            filters['is_read'] = is_read

        # Call service with correct signature
        result = notification_service.get_user_notifications(
            user_id=user_id,
            page=page,
            per_page=per_page,
            filters=filters if filters else None
        )

        return success_response(result)

    except Exception as e:
        logger.error(f"Error getting notifications: {e}", exc_info=True)
        return error_response(f"Failed to get notifications: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# GET SINGLE NOTIFICATION
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    """Get a single notification by ID for current user"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()

        # Use get_by_id if available
        if hasattr(notification_service, "get_by_id"):
            notif = notification_service.get_by_id(notification_id, user_id)
            if not notif:
                return error_response("Notification not found", 404)
            return success_response({"notification": notif})

        return error_response("get_by_id not implemented in NotificationService", 501)

    except Exception as e:
        logger.error(f"Error getting notification: {e}", exc_info=True)
        return error_response(f"Failed to get notification: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# CREATE NOTIFICATION
# ─────────────────────────────────────────────────────────────
@notification_bp.route('', methods=['POST'])
@jwt_required()
def create_notification():
    """Create a new notification (admin/service usage)"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        actor_id = int(get_jwt_identity())
        data = request.get_json() or {}

        required_fields = ['user_id', 'title', 'message']
        if not all(field in data for field in required_fields):
            return error_response("Missing required fields: user_id, title, message", 400)

        # Use create_simple_notification which exists in service
        created = notification_service.create_simple_notification(
            user_id=data['user_id'],
            title=data['title'],
            message=data['message'],
            notification_type=data.get('type', 'info'),
            category=data.get('category', 'system'),
            priority=data.get('priority', 'medium'),
            actor_id=actor_id,
            entity_type=data.get('entity_type'),
            entity_id=data.get('entity_id'),
            link_url=data.get('link_url'),
            metadata=data.get('data', {}),
        )
        
        if created:
            return success_response({"notification": created.to_dict()}, "Notification created successfully", 201)
        return error_response("Failed to create notification", 500)

    except Exception as e:
        logger.error(f"Error creating notification: {e}", exc_info=True)
        return error_response(f"Failed to create notification: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# GET UNREAD COUNT
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get unread notification count for current user"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        count = notification_service.get_unread_count(user_id)

        return success_response({
            'unread_count': count,
            'unreadCount': count
        })

    except Exception as e:
        logger.error(f"Error getting unread count: {e}", exc_info=True)
        return error_response(f"Failed to get unread count: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# GET HIGH PRIORITY
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/high-priority', methods=['GET'])
@jwt_required()
def get_high_priority():
    """Get high priority unread notifications"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 5, type=int)

        # Use get_user_notifications with priority filter
        result = notification_service.get_user_notifications(
            user_id=user_id,
            page=1,
            per_page=limit,
            filters={'priority': 'high', 'is_read': False}
        )
        return success_response({'notifications': result.get('notifications', [])})

    except Exception as e:
        logger.error(f"Error getting high priority notifications: {e}", exc_info=True)
        return error_response(f"Failed to get high priority notifications: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# GET STATS
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get notification statistics for current user"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        stats = notification_service.get_notification_stats(user_id)
        return success_response(stats)

    except Exception as e:
        logger.error(f"Error getting notification stats: {e}", exc_info=True)
        return error_response(f"Failed to get stats: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# MARK AS READ
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/<int:notification_id>/read', methods=['PUT', 'POST'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark a single notification as read"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        success = notification_service.mark_as_read(notification_id, user_id)

        if success:
            unread_count = notification_service.get_unread_count(user_id)
            return success_response({
                'message': 'Notification marked as read',
                'unread_count': unread_count,
                'unreadCount': unread_count
            })
        return error_response('Notification not found', 404)

    except Exception as e:
        logger.error(f"Error marking notification as read: {e}", exc_info=True)
        return error_response(f"Failed to mark as read: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# MARK AS UNREAD
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/<int:notification_id>/unread', methods=['PUT', 'POST'])
@jwt_required()
def mark_as_unread(notification_id):
    """Mark a single notification as unread"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        success = notification_service.mark_as_unread(notification_id, user_id)

        if success:
            unread_count = notification_service.get_unread_count(user_id)
            return success_response({
                'message': 'Notification marked as unread',
                'unread_count': unread_count,
                'unreadCount': unread_count
            })
        return error_response('Notification not found', 404)

    except Exception as e:
        logger.error(f"Error marking notification as unread: {e}", exc_info=True)
        return error_response(f"Failed to mark as unread: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# MARK ALL AS READ
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/mark-all-read', methods=['PUT', 'POST'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read for current user (optional category)"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()

        # Accept category from query param OR JSON body
        category = request.args.get('category')
        data = request.get_json(silent=True) or {}
        category = category or data.get('category')

        count = notification_service.mark_all_as_read(user_id, category)

        return success_response({
            'message': f'Marked {count} notifications as read',
            'count': count,
            'unread_count': 0,
            'unreadCount': 0
        })

    except Exception as e:
        logger.error(f"Error marking all as read: {e}", exc_info=True)
        return error_response(f"Failed to mark all as read: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# BATCH READ
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/batch/read', methods=['POST'])
@jwt_required()
def batch_mark_read():
    """Mark multiple notifications as read (batch)"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        notification_ids = data.get('notification_ids', data.get('notificationIds', []))

        if not notification_ids:
            return error_response('Notification IDs are required', 400)

        count = notification_service.bulk_mark_as_read(notification_ids, user_id)
        unread_count = notification_service.get_unread_count(user_id)

        return success_response({
            'message': f'{count} notifications marked as read',
            'count': count,
            'unread_count': unread_count,
            'unreadCount': unread_count
        })

    except Exception as e:
        logger.error(f"Error batch marking as read: {e}", exc_info=True)
        return error_response(f"Failed to mark notifications as read: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# BULK MARK AS READ
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/bulk/mark-read', methods=['PUT', 'POST'])
@jwt_required()
def bulk_mark_as_read():
    """Mark multiple notifications as read"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        notification_ids = data.get('notificationIds', data.get('notification_ids', []))

        if not notification_ids:
            return error_response('No notification IDs provided', 400)

        count = notification_service.bulk_mark_as_read(notification_ids, user_id)
        unread_count = notification_service.get_unread_count(user_id)

        return success_response({
            'message': f'Marked {count} notifications as read',
            'count': count,
            'unread_count': unread_count,
            'unreadCount': unread_count
        })

    except Exception as e:
        logger.error(f"Error bulk marking as read: {e}", exc_info=True)
        return error_response(f"Failed to bulk mark as read: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# DELETE NOTIFICATION
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a single notification"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        success = notification_service.delete_notification(notification_id, user_id)

        if success:
            unread_count = notification_service.get_unread_count(user_id)
            return success_response({
                'message': 'Notification deleted',
                'unread_count': unread_count,
                'unreadCount': unread_count
            })
        return error_response('Notification not found', 404)

    except Exception as e:
        logger.error(f"Error deleting notification: {e}", exc_info=True)
        return error_response(f"Failed to delete notification: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# DELETE ALL READ NOTIFICATIONS
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/read', methods=['DELETE'])
@notification_bp.route('/delete-all-read', methods=['DELETE'])
@jwt_required()
def delete_all_read():
    """Delete all read notifications for current user"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        count = notification_service.delete_all_read(user_id)

        return success_response({
            'message': f'Deleted {count} read notifications',
            'count': count
        })

    except Exception as e:
        logger.error(f"Error deleting read notifications: {e}", exc_info=True)
        return error_response(f"Failed to delete read notifications: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# CLEAR ALL NOTIFICATIONS
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/all', methods=['DELETE'])
@jwt_required()
def clear_all_notifications():
    """Clear/delete ALL notifications for current user"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        count = notification_service.clear_all(user_id)

        return success_response({
            'message': f'Cleared {count} notifications',
            'count': count,
            'unread_count': 0,
            'unreadCount': 0
        })

    except Exception as e:
        logger.error(f"Error clearing all notifications: {e}", exc_info=True)
        return error_response(f"Failed to clear notifications: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# BULK DELETE
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/bulk', methods=['DELETE'])
@notification_bp.route('/bulk/delete', methods=['POST'])
@jwt_required()
def bulk_delete():
    """Delete multiple notifications"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        notification_ids = data.get('notificationIds', data.get('notification_ids', []))

        if not notification_ids:
            return error_response('No notification IDs provided', 400)

        count = notification_service.bulk_delete(notification_ids, user_id)
        unread_count = notification_service.get_unread_count(user_id)

        return success_response({
            'message': f'Deleted {count} notifications',
            'count': count,
            'unread_count': unread_count,
            'unreadCount': unread_count
        })

    except Exception as e:
        logger.error(f"Error bulk deleting: {e}", exc_info=True)
        return error_response(f"Failed to bulk delete: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# GET PREFERENCES
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get notification preferences for current user"""
    try:
        preferences = {
            'emailEnabled': True,
            'pushEnabled': True,
            'inAppEnabled': True,
            'categories': {
                'account': True,
                'social': True,
                'task': True,
                'message': True,
                'idea': True,
                'startup': True,
                'reward': True,
                'event': True,
                'newsletter': True,
                'system': True,
            },
            'priorityThreshold': 'low',
            'digestFrequency': 'daily',
            'mutedUsers': [],
            'mutedStartups': [],
            'doNotDisturb': {
                'enabled': False,
                'startTime': '22:00',
                'endTime': '08:00'
            }
        }
        return success_response({'preferences': preferences})

    except Exception as e:
        logger.error(f"Error getting preferences: {e}", exc_info=True)
        return error_response(f"Failed to get preferences: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# UPDATE PREFERENCES
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/preferences', methods=['PUT', 'PATCH'])
@jwt_required()
def update_preferences():
    """Update notification preferences for current user"""
    try:
        data = request.get_json() or {}
        return success_response({
            'message': 'Preferences updated',
            'preferences': data
        })

    except Exception as e:
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        return error_response(f"Failed to update preferences: {str(e)}", 500)