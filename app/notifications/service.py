"""
SF Collab Notification Service
Core service for creating and managing notifications
Enhanced with email and real-time support
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from app.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.notifications.templates import NOTIFICATION_TEMPLATES, PRIORITY_LEVELS
import logging
from app.models.transaction import Transaction
from app.utils.email_templates.email_templates import transaction_bill_email_template

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
        auto_send: bool = True,
        send_email: bool = False,
        transaction=None
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
            send_email: Whether to send email notification
            transaction: Transaction object related to the notification
        Returns:
            Created Notification object or None if failed
        """
        try:
            # Don't notify yourself
            if actor_id and actor_id == user_id:
                logger.debug(f"Skipping self-notification for user {user_id}")
                return None
            
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
                **(metadata or {})
            }
            
            # Create notification with all fields
            notification = Notification(
                user_id=user_id,
                actor_id=actor_id,
                notification_type=template.get("type", "info"),
                category=template.get("category", "system"),
                priority=template.get("priority", "medium"),
                title=title,
                message=message,
                entity_type=entity_type,
                entity_id=entity_id,
                data=full_metadata,
                is_read=False
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Send real-time notification if auto_send is True
            if auto_send:
                NotificationService.send_realtime_notification(notification)
            
            # Send email if requested and priority is high/critical
            if send_email or template.get("priority") in ["critical", "high"]:
                NotificationService.send_email_notification(notification, transaction=transaction)
            
            logger.info(f"Created notification {notification.id} for user {user_id} (template: {template_key})")
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
    def send_email_notification(notification: Notification, transaction: Transaction) -> bool:
        """
        Send notification via email
        
        Args:
            notification: Notification object to send
            transaction: Transaction object related to the notification
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Only send email for certain priorities
            if notification.priority not in ["critical", "high"]:
                return False
            
            user = User.query.get(notification.user_id)
            if not user or not user.email:
                return False
            
            # Check user preferences (TODO: implement preferences)
            # if not user.notification_preferences.email_enabled:
            #     return False
            
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            # Send email
            email_service.send_email(
                recipient=user.email,
                subject=notification.title,
                body=transaction_bill_email_template(transaction)
            )
            
            # Update notification
            notification.email_sent = True
            notification.email_sent_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Sent email notification {notification.id} to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False

    @staticmethod
    def bulk_create_notifications(
        user_ids: List[int],
        template_key: str,
        variables: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        exclude_actor: bool = True
    ) -> List[Notification]:
        """
        Create notifications for multiple users
        
        Args:
            user_ids: List of user IDs to receive notifications
            exclude_actor: If True, don't notify the actor
            Other args same as create_notification
            
        Returns:
            List of created Notification objects
        """
        notifications = []
        
        # Remove actor from recipients if requested
        if exclude_actor and actor_id and actor_id in user_ids:
            user_ids = [uid for uid in user_ids if uid != actor_id]
        
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
            now = datetime.utcnow()
            count = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).update({
                'is_read': True,
                'read_at': now
            })
            
            db.session.commit()
            
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            db.session.rollback()
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
                if 'category' in filters:
                    query = query.filter_by(category=filters['category'])
                if 'priority' in filters:
                    query = query.filter_by(priority=filters['priority'])
                if 'is_read' in filters:
                    query = query.filter_by(is_read=filters['is_read'])
            
            # Order by priority then created_at
            query = query.order_by(
                Notification.created_at.desc()
            )
            
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
    def get_unread_count_by_category(user_id: int) -> Dict[str, int]:
        """
        Get unread count grouped by category
        
        Args:
            user_id: ID of user
            
        Returns:
            Dict of category -> count
        """
        try:
            results = db.session.query(
                Notification.category,
                db.func.count(Notification.id)
            ).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).group_by(Notification.category).all()
            
            return {category: count for category, count in results}
            
        except Exception as e:
            logger.error(f"Error getting unread count by category: {e}")
            return {}

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
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            count = Notification.query.filter(
                Notification.is_read == True,
                Notification.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            logger.info(f"Deleted {count} old notifications")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {e}")
            db.session.rollback()
            return 0

    @staticmethod
    def get_notification_stats(user_id: int) -> Dict[str, Any]:
        """
        Get notification statistics for a user
        
        Args:
            user_id: ID of user
            
        Returns:
            Dict with various statistics
        """
        try:
            total = Notification.query.filter_by(user_id=user_id).count()
            unread = Notification.query.filter_by(user_id=user_id, is_read=False).count()
            
            # By type
            type_stats = db.session.query(
                Notification.notification_type,
                db.func.count(Notification.id)
            ).filter_by(user_id=user_id).group_by(Notification.notification_type).all()
            
            # By category
            category_stats = db.session.query(
                Notification.category,
                db.func.count(Notification.id)
            ).filter_by(user_id=user_id).group_by(Notification.category).all()
            
            # By priority
            priority_stats = db.session.query(
                Notification.priority,
                db.func.count(Notification.id)
            ).filter_by(user_id=user_id).group_by(Notification.priority).all()
            
            return {
                'total': total,
                'unread': unread,
                'read': total - unread,
                'typeBreakdown': {t: c for t, c in type_stats},
                'categoryBreakdown': {c: cnt for c, cnt in category_stats},
                'priorityBreakdown': {p: c for p, c in priority_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {
                'total': 0,
                'unread': 0,
                'read': 0,
                'typeBreakdown': {},
                'categoryBreakdown': {},
                'priorityBreakdown': {}
            }


# Singleton instance
notification_service = NotificationService()