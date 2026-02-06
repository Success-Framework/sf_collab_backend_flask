"""
Notification Routes

API endpoints for notification management.
MERGED VERSION:
- Keeps your existing NotificationService usage
- Adds missing routes + safer behavior from the other file:
  ✅ GET single notification
  ✅ CREATE notification
  ✅ Batch read endpoint (/batch/read)
  ✅ Bulk delete POST endpoint (/bulk/delete) + keep DELETE /bulk
  ✅ mark-all-read supports BOTH query param (?category=) and JSON body {category}
  ✅ GET notifications supports priority filter too
  ✅ Preferences endpoint supports PUT + PATCH
  ✅ Safe import fallback so app doesn't crash if service missing
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
# GET ALL NOTIFICATIONS
# ─────────────────────────────────────────────────────────────
@notification_bp.route('', methods=['GET'])
@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
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

        # If your NotificationService supports priority, pass it.
        # If it doesn't, the except block will fall back without it.
        try:
            result = notification_service.get_notifications(
                user_id=user_id,
                page=page,
                per_page=per_page,
                category=category,
                notification_type=notification_type,
                priority=priority,
                is_read=is_read
            )
        except TypeError:
            result = notification_service.get_notifications(
                user_id=user_id,
                page=page,
                per_page=per_page,
                category=category,
                notification_type=notification_type,
                is_read=is_read
            )

        return success_response(result)

    except Exception as e:
        logger.error(f"Error getting notifications: {e}", exc_info=True)
        return error_response(f"Failed to get notifications: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# GET SINGLE NOTIFICATION (added)
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    """Get a single notification by ID for current user"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()

        # Prefer service method if it exists
        if hasattr(notification_service, "get_by_id"):
            notif = notification_service.get_by_id(notification_id, user_id)
            if not notif:
                return error_response("Notification not found", 404)
            return success_response({"notification": notif})

        # Fallback: if service doesn't have get_by_id, reuse list query (best effort)
        result = notification_service.get_notifications(
            user_id=user_id,
            page=1,
            per_page=1,
        )
        # Can't reliably find by ID without model access. Return not implemented.
        return error_response("get_by_id not implemented in NotificationService", 501)

    except Exception as e:
        logger.error(f"Error getting notification: {e}", exc_info=True)
        return error_response(f"Failed to get notification: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# CREATE NOTIFICATION (added)
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

        # Normalize safe JSON payload
        safe_data = data.get('data', {})
        if not isinstance(safe_data, (dict, list)):
            safe_data = {}

        # Prefer service method if it exists
        if hasattr(notification_service, "create"):
            created = notification_service.create(
                actor_id=actor_id,
                user_id=data['user_id'],
                title=data['title'],
                message=data['message'],
                notification_type=data.get('type', 'info'),
                category=data.get('category', 'system'),
                priority=data.get('priority', 'medium'),
                entity_type=data.get('entity_type'),
                entity_id=data.get('entity_id'),
                link_url=data.get('link_url'),
                data=json.loads(json.dumps(safe_data)),
            )
            return success_response({"notification": created}, "Notification created successfully", 201)

        return error_response("create not implemented in NotificationService", 501)

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
# GET UNREAD COUNT FOR USER (added)
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/user/<int:user_id>/unread-count', methods=['GET'])
@jwt_required()
def get_user_unread_count(user_id):
    """Get unread count for a specific user (admin-only unless same user)"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        current_user_id = int(get_jwt_identity())

        # If your service supports auth checks, use it; otherwise keep strict
        if user_id != current_user_id:
            # If you have a method to check admin, use it. Otherwise block.
            if hasattr(notification_service, "is_admin") and notification_service.is_admin(current_user_id):
                pass
            else:
                return error_response("Unauthorized to view other users notification counts", 403)

        count = notification_service.get_unread_count(user_id)
        return success_response({
            'user_id': user_id,
            'unread_count': count,
            'unreadCount': count
        })

    except Exception as e:
        logger.error(f"Error getting user unread count: {e}", exc_info=True)
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

        notifications = notification_service.get_high_priority(user_id, limit)
        return success_response({'notifications': notifications})

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

        stats = notification_service.get_notification_stats(user_id) \
            if hasattr(notification_service, "get_notification_stats") \
            else notification_service.get_notification_stats(user_id)

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
# MARK ALL AS READ (enhanced: supports body OR query param)
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
# BATCH READ (added)  POST /batch/read  { notification_ids: [] }
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
        notification_ids = data.get('notification_ids', [])

        if not notification_ids:
            return error_response('Notification IDs are required', 400)

        # Prefer a dedicated service method if it exists; else reuse bulk
        if hasattr(notification_service, "mark_notifications_read_batch"):
            count = notification_service.mark_notifications_read_batch(notification_ids, user_id)
        else:
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
# BULK MARK AS READ (enhanced: accepts camelCase too)
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

        # Accept both camelCase and snake_case
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
# DELETE ALL READ NOTIFICATIONS (support both routes)
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

        # Prefer service method
        count = notification_service.delete_all_read(user_id) \
            if hasattr(notification_service, "delete_all_read") \
            else notification_service.delete_all_read(user_id)

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
# BULK DELETE (keep DELETE /bulk) - enhanced camelCase
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/bulk', methods=['DELETE'])
@jwt_required()
def bulk_delete():
    """Delete multiple notifications (DELETE endpoint)"""
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
# BULK DELETE (added) POST /bulk/delete  { notificationIds: [] }
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/bulk/delete', methods=['POST'])
@jwt_required()
def bulk_delete_post():
    """Delete multiple notifications (POST endpoint for frontend convenience)"""
    if not HAS_NOTIFICATION_SERVICE:
        return error_response("Notification service not available", 500)

    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        notification_ids = data.get('notificationIds', data.get('notification_ids', []))

        if not notification_ids:
            return error_response('No notification IDs provided', 400)

        # Prefer service bulk_delete
        count = notification_service.bulk_delete(notification_ids, user_id)
        unread_count = notification_service.get_unread_count(user_id)

        return success_response({
            'message': f'Deleted {count} notifications',
            'count': count,
            'unread_count': unread_count,
            'unreadCount': unread_count
        })

    except Exception as e:
        logger.error(f"Error in bulk delete POST: {e}", exc_info=True)
        return error_response("Failed to delete notifications", 500)


# ─────────────────────────────────────────────────────────────
# GET PREFERENCES
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get notification preferences for current user"""
    try:
        # Default preferences (same spirit as your other file)
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
# UPDATE PREFERENCES (PUT + PATCH)
# ─────────────────────────────────────────────────────────────
@notification_bp.route('/preferences', methods=['PUT', 'PATCH'])
@jwt_required()
def update_preferences():
    """Update notification preferences for current user"""
    try:
        data = request.get_json() or {}

        # TODO: Save preferences to database
        return success_response({
            'message': 'Preferences updated',
            'preferences': data
        })

    except Exception as e:
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        return error_response(f"Failed to update preferences: {str(e)}", 500)
