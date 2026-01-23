"""
SF Collab Notification Service
Core service for creating and managing notifications
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from app.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.notifications.templates import NOTIFICATION_TEMPLATES, PRIORITY_LEVELS
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service class for handling notification operations"""

    @staticmethod
    def create_notification(
        user_id: int,
        template_key: str,
        variables: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        auto_send: bool = True
    ) -> Optional[Notification]:
        """
        Create a notification from a template
        
        Args:
            user_id: ID of the user to receive the notification
            template_key: Key from NOTIFICATION_TEMPLATES
            variables: Variables to format the template message
            metadata: Additional metadata to store with notification
            actor_id: ID of the user who triggered this notification
            entity_type: Type of entity (idea, task, startup, etc.)
            entity_id: ID of the related entity
            auto_send: Whether to send via Socket.IO immediately
            
        Returns:
            Created Notification object or None if failed
        """
        try:
            # Get template
            template = NOTIFICATION_TEMPLATES.get(template_key)
            if not template:
                logger.error(f"Invalid notification template: {template_key}")
                return None
            
            # Prepare variables
            variables = variables or {}
            
            # Format title and message with variables
            try:
                title = template["title"].format(**variables)
                message = template["message"].format(**variables)
            except KeyError as e:
                logger.error(f"Missing variable in template {template_key}: {e}")
                return None
            
            # Prepare metadata
            full_metadata = {
                "template_key": template_key,
                "category": template.get("category"),
                "priority": template.get("priority"),
                **(metadata or {})
            }
            
            # Add actor info if provided
            if actor_id:
                full_metadata["actor_id"] = actor_id
            
            # Add entity info if provided
            if entity_type:
                full_metadata["entity_type"] = entity_type
            if entity_id:
                full_metadata["entity_id"] = entity_id
            
            # Create notification
            notification = Notification(
                user_id=user_id,
                notification_type=template.get("type", "info"),
                title=title,
                message=message,
                data=full_metadata,
                is_read=False
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Send real-time notification if auto_send is True
            if auto_send:
                NotificationService.send_realtime_notification(notification)
            
            logger.info(f"Created notification {notification.id} for user {user_id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def send_realtime_notification(notification: Notification) -> bool:
        """
        Send notification via Socket.IO
        
        Args:
            notification: Notification object to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            from app.socket_events import emit_to_user
            
            emit_to_user(
                user_id=notification.user_id,
                event='new_notification',
                data={
                    'notification': notification.to_dict()
                }
            )
            
            logger.info(f"Sent real-time notification {notification.id} to user {notification.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending real-time notification: {e}")
            return False

    @staticmethod
    def bulk_create_notifications(
        user_ids: List[int],
        template_key: str,
        variables: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None
    ) -> List[Notification]:
        """
        Create notifications for multiple users
        
        Args:
            user_ids: List of user IDs to receive notifications
            Other args same as create_notification
            
        Returns:
            List of created Notification objects
        """
        notifications = []
        
        for user_id in user_ids:
            notification = NotificationService.create_notification(
                user_id=user_id,
                template_key=template_key,
                variables=variables,
                metadata=metadata,
                actor_id=actor_id,
                entity_type=entity_type,
                entity_id=entity_id
            )
            if notification:
                notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} bulk notifications")
        return notifications

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """
        Mark a notification as read
        
        Args:
            notification_id: ID of notification
            user_id: ID of user (for authorization check)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.query.get(notification_id)
            
            if not notification:
                logger.error(f"Notification {notification_id} not found")
                return False
            
            # Check authorization
            if notification.user_id != user_id:
                logger.error(f"User {user_id} not authorized to mark notification {notification_id}")
                return False
            
            notification.mark_as_read()
            logger.info(f"Marked notification {notification_id} as read")
            return True
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """
        Mark all notifications for a user as read
        
        Args:
            user_id: ID of user
            
        Returns:
            Number of notifications marked as read
        """
        try:
            unread_notifications = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).all()
            
            count = 0
            for notification in unread_notifications:
                notification.mark_as_read()
                count += 1
            
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            return 0

    @staticmethod
    def delete_notification(notification_id: int, user_id: int) -> bool:
        """
        Delete a notification
        
        Args:
            notification_id: ID of notification
            user_id: ID of user (for authorization check)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.query.get(notification_id)
            
            if not notification:
                logger.error(f"Notification {notification_id} not found")
                return False
            
            # Check authorization
            if notification.user_id != user_id:
                logger.error(f"User {user_id} not authorized to delete notification {notification_id}")
                return False
            
            db.session.delete(notification)
            db.session.commit()
            
            logger.info(f"Deleted notification {notification_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def get_user_notifications(
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get notifications for a user with pagination and filters
        
        Args:
            user_id: ID of user
            page: Page number
            per_page: Items per page
            filters: Optional filters (type, category, priority, is_read)
            
        Returns:
            Dict with notifications and pagination info
        """
        try:
            query = Notification.query.filter_by(user_id=user_id)
            
            # Apply filters
            if filters:
                if 'type' in filters:
                    query = query.filter_by(notification_type=filters['type'])
                if 'is_read' in filters:
                    query = query.filter_by(is_read=filters['is_read'])
                # Add category/priority filters via JSON if needed
            
            # Order by created_at desc (newest first)
            query = query.order_by(Notification.created_at.desc())
            
            # Paginate
            from app.utils.helper import paginate
            result = paginate(query, page, per_page)
            
            return {
                'notifications': [n.to_dict() for n in result['items']],
                'pagination': {
                    'page': result['page'],
                    'per_page': result['per_page'],
                    'total': result['total'],
                    'pages': result['pages']
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return {
                'notifications': [],
                'pagination': {'page': 1, 'per_page': per_page, 'total': 0, 'pages': 0}
            }

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get count of unread notifications for a user
        
        Args:
            user_id: ID of user
            
        Returns:
            Count of unread notifications
        """
        try:
            count = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).count()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0

    @staticmethod
    def cleanup_old_notifications(days: int = 90) -> int:
        """
        Delete old read notifications
        
        Args:
            days: Delete notifications older than this many days
            
        Returns:
            Number of notifications deleted
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            old_notifications = Notification.query.filter(
                Notification.is_read == True,
                Notification.created_at < cutoff_date
            ).all()
            
            count = len(old_notifications)
            for notification in old_notifications:
                db.session.delete(notification)
            
            db.session.commit()
            
            logger.info(f"Deleted {count} old notifications")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {e}")
            db.session.rollback()
            return 0


# Singleton instance
notification_service = NotificationService()