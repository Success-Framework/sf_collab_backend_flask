from datetime import datetime, timedelta
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
        auto_send: bool = True,
        send_email: bool = False,
        transaction=None,
        link_url: Optional[str] = None
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
            link_url: URL to navigate to when notification is clicked
        Returns:
            Created Notification object or None if failed
        """
        try:
            # Don't notify yourself
            # IMPORTANT: actor_id comes from JWT (string) while user_id may be int or string.
            # Always cast both to int before comparing to avoid "5" != 5 false-negative.
            if actor_id is not None and int(actor_id) == int(user_id):
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
                link_url=link_url,
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
    def create_simple_notification(
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "info",
        category: str = "system",
        priority: str = "medium",
        actor_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        link_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_send: bool = True
    ) -> Optional[Notification]:
        """
        Create a simple notification without a template
        
        Args:
            user_id: ID of the user to receive the notification
            title: Notification title
            message: Notification message
            notification_type: Type (success, info, warning, error)
            category: Category (account, social, task, etc.)
            priority: Priority level (low, medium, high, critical)
            actor_id: ID of the user who triggered this
            entity_type: Type of related entity
            entity_id: ID of related entity
            link_url: URL to navigate to
            metadata: Additional data
            auto_send: Whether to send via Socket.IO immediately
        """
        try:
            # Don't notify yourself
            # IMPORTANT: same int() cast as create_notification to handle JWT string vs DB int
            if actor_id is not None and int(actor_id) == int(user_id):
                return None
            
            notification = Notification(
                user_id=user_id,
                actor_id=actor_id,
                notification_type=notification_type,
                category=category,
                priority=priority,
                title=title,
                message=message,
                entity_type=entity_type,
                entity_id=entity_id,
                data=metadata or {},
                link_url=link_url,
                is_read=False
            )
            
            db.session.add(notification)
            db.session.commit()
            
            if auto_send:
                NotificationService.send_realtime_notification(notification)
            
            logger.info(f"Created simple notification {notification.id} for user {user_id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creating simple notification: {e}")
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
            from app.extensions import socketio
            
            # Emit to the user's room
            socketio.emit(
                'new_notification',
                {
                    'notification': notification.to_dict()
                },
                room=f'user_{notification.user_id}'
            )
            
            logger.info(f"Sent real-time notification {notification.id} to user {notification.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending real-time notification: {e}")
            return False

    @staticmethod
    def send_email_notification(notification: Notification, transaction=None) -> bool:
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
            
            # Mark email as sent (actual email sending would go here)
            notification.email_sent = True
            notification.email_sent_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Email notification sent for {notification.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════
    # READ/UNREAD METHODS
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """
        Mark a single notification as read
        
        Args:
            notification_id: ID of notification
            user_id: ID of user (for authorization check)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                return False
            
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Marked notification {notification_id} as read")
            return True
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def mark_as_unread(notification_id: int, user_id: int) -> bool:
        """
        Mark a single notification as unread
        
        Args:
            notification_id: ID of notification
            user_id: ID of user (for authorization check)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                return False
            
            notification.is_read = False
            notification.read_at = None
            db.session.commit()
            
            logger.info(f"Marked notification {notification_id} as unread")
            return True
            
        except Exception as e:
            logger.error(f"Error marking notification as unread: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def mark_all_as_read(user_id: int, category: Optional[str] = None) -> int:
        """
        Mark all notifications as read for a user
        
        Args:
            user_id: ID of user
            category: Optional category to filter by
            
        Returns:
            Number of notifications marked as read
        """
        try:
            query = Notification.query.filter_by(user_id=user_id, is_read=False)
            
            if category:
                query = query.filter_by(category=category)
            
            count = query.update({
                'is_read': True,
                'read_at': datetime.utcnow()
            })
            
            db.session.commit()
            
            # Emit real-time event so all open Bell/Page components sync instantly
            try:
                from app.extensions import socketio
                socketio.emit(
                    'notifications_marked_read',
                    {'unread_count': 0, 'category': category},
                    room=f'user_{user_id}'
                )
            except Exception as emit_err:
                logger.warning(f"Could not emit notifications_marked_read: {emit_err}")
            
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error marking all as read: {e}")
            db.session.rollback()
            return 0

    @staticmethod
    def bulk_mark_as_read(notification_ids: List[int], user_id: int) -> int:
        """
        Mark multiple notifications as read
        
        Args:
            notification_ids: List of notification IDs
            user_id: ID of user (for authorization check)
            
        Returns:
            Number of notifications marked as read
        """
        try:
            count = Notification.query.filter(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id
            ).update({
                'is_read': True,
                'read_at': datetime.utcnow()
            }, synchronize_session=False)
            
            db.session.commit()
            
            logger.info(f"Bulk marked {count} notifications as read")
            return count
            
        except Exception as e:
            logger.error(f"Error bulk marking as read: {e}")
            db.session.rollback()
            return 0

    # ═══════════════════════════════════════════════════════════════
    # DELETE METHODS
    # ═══════════════════════════════════════════════════════════════

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
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                logger.error(f"Notification {notification_id} not found for user {user_id}")
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
    def delete_all_read(user_id: int) -> int:
        """
        Delete all read notifications for a user
        
        Args:
            user_id: ID of user
            
        Returns:
            Number of notifications deleted
        """
        try:
            count = Notification.query.filter_by(
                user_id=user_id,
                is_read=True
            ).delete()
            
            db.session.commit()
            
            logger.info(f"Deleted {count} read notifications for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error deleting read notifications: {e}")
            db.session.rollback()
            return 0

    @staticmethod
    def clear_all(user_id: int) -> int:
        """
        Clear/delete ALL notifications for a user
        
        Args:
            user_id: ID of user
            
        Returns:
            Number of notifications deleted
        """
        try:
            count = Notification.query.filter_by(user_id=user_id).delete()
            
            db.session.commit()
            
            logger.info(f"Cleared {count} notifications for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing all notifications: {e}")
            db.session.rollback()
            return 0

    @staticmethod
    def bulk_delete(notification_ids: List[int], user_id: int) -> int:
        """
        Delete multiple notifications
        
        Args:
            notification_ids: List of notification IDs
            user_id: ID of user (for authorization check)
            
        Returns:
            Number of notifications deleted
        """
        try:
            count = Notification.query.filter(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id
            ).delete(synchronize_session=False)
            
            db.session.commit()
            
            logger.info(f"Bulk deleted {count} notifications")
            return count
            
        except Exception as e:
            logger.error(f"Error bulk deleting notifications: {e}")
            db.session.rollback()
            return 0

    # ═══════════════════════════════════════════════════════════════
    # QUERY METHODS
    # ═══════════════════════════════════════════════════════════════

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
            
            # Order by created_at (newest first)
            query = query.order_by(Notification.created_at.desc())
            
            # Paginate
            total = query.count()
            pages = (total + per_page - 1) // per_page
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'notifications': [n.to_dict() for n in items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': pages
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
            
    def get_announcements(self) -> List[Dict[str, Any]]:
        """
        Get global announcements (for dashboard)
        
        Returns:
            List of announcement dicts
        """
        try:
            # For simplicity, using notifications with category 'announcement'
            announcements = Notification.query.filter_by(
                category='announcement'
            ).order_by(Notification.created_at.desc()).all()
            
            return [a.to_dict() for a in announcements]
            
        except Exception as e:
            logger.error(f"Error getting announcements: {e}")
            return []
    @staticmethod
    def create_announcement(
        title: str,
        user_id: int,
        message: str,
        priority: str = 'medium',
        actor_id: Optional[int] = None,
        link_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Notification]:
        """
        Create a global announcement
        
        Args:
            title: Announcement title
            message: Announcement message
            link_url: Optional URL for more info
            
        Returns:
            Created Notification object or None if failed
        """
        try:
            # For simplicity, using user_id = None for global announcements
            announcement = Notification(
                user_id=user_id,
                notification_type="info",
                actor_id=actor_id,
                category="announcement",
                priority=priority,
                title=title,
                message=message,
                link_url=link_url,
                is_read=False,
                data=metadata
                # metadata=metadata or {}
            )
            
            db.session.add(announcement)
            db.session.commit()
            
            logger.info(f"Created announcement {announcement.id}")
            return announcement
            
        except Exception as e:
            logger.error(f"Error creating announcement: {e}")
            db.session.rollback()
            return None
    def get_newsletter(self) -> List[Dict[str, Any]]:
        """
        Get newsletter content (for dashboard)
        
        Returns:
            List of newsletter dicts
        """
        try:
            # For simplicity, using notifications with category 'newsletter'
            newsletters = Notification.query.filter_by(
                category='newsletter'
            ).order_by(Notification.created_at.desc()).all()
            
            return [n.to_dict() for n in newsletters]
            
        except Exception as e:
            logger.error(f"Error getting newsletters: {e}")
            return []
    def create_newsletter(
        self,
        title: str,
        user_id: int,
        content: str,
        actor_id: Optional[int] = None,
        link_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Notification]:
        """
        Create a newsletter entry
        
        Args:
            title: Newsletter title
            message: Newsletter message
            link_url: Optional URL for more info
            
        Returns:
            Created Notification object or None if failed
        """
        try:
            # For simplicity, using user_id = None for global newsletters
            newsletter = Notification(
                user_id=user_id,
                notification_type="info",
                category="newsletter",
                priority="medium",
                title=title,
                message=content,
                actor_id=actor_id,
                link_url=link_url,
                is_read=False,
                data=metadata
            )
            
            db.session.add(newsletter)
            db.session.commit()
            
            logger.info(f"Created newsletter {newsletter.id}")
            return newsletter
            
        except Exception as e:
            logger.error(f"Error creating newsletter: {e}")
            db.session.rollback()
            return None
    @staticmethod
    def update_announcement(
        announcement_id: int,
        title: Optional[str] = None,
        message: Optional[str] = None,
        priority: Optional[str] = None,
        link_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: Optional[int] = None
    ) -> Optional[Notification]:
        """Update an announcement"""
        try:
            announcement = Notification.query.filter_by(
                id=announcement_id,
                category='announcement'
            ).first()
            
            if not announcement:
                return None
            
            if title:
                announcement.title = title
            if message:
                announcement.message = message
            if priority:
                announcement.priority = priority
            if link_url:
                announcement.link_url = link_url
            if metadata:
                announcement.data = metadata
            
            db.session.commit()
            logger.info(f"Updated announcement {announcement_id}")
            return announcement
            
        except Exception as e:
            logger.error(f"Error updating announcement: {e}")
            db.session.rollback()
            return None
    @staticmethod
    def delete_announcement(announcement_id: int, user_id: int) -> bool:
        """Delete an announcement"""
        try:
            announcement = Notification.query.filter_by(
                id=announcement_id,
                category='announcement'
            ).first()
            
            if not announcement:
                return False
            
            db.session.delete(announcement)
            db.session.commit()
            logger.info(f"Deleted announcement {announcement_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting announcement: {e}")
            db.session.rollback()
            return False
    @staticmethod
    def clear_all_announcements(user_id: int) -> int:
        """Delete all announcements"""
        try:
            count = Notification.query.filter_by(category='announcement').delete()
            db.session.commit()
            logger.info(f"Cleared {count} announcements")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing announcements: {e}")
            db.session.rollback()
            return 0
    @staticmethod
    def update_newsletter(
        newsletter_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        link_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_id: Optional[int] = None
    ) -> Optional[Notification]:
        """Update a newsletter"""
        try:
            newsletter = Notification.query.filter_by(
                id=newsletter_id,
                category='newsletter'
            ).first()
            
            if not newsletter:
                return None
            
            if title:
                newsletter.title = title
            if content:
                newsletter.message = content
            if link_url:
                newsletter.link_url = link_url
            if metadata:
                newsletter.data = metadata
            
            db.session.commit()
            logger.info(f"Updated newsletter {newsletter_id}")
            return newsletter
            
        except Exception as e:
            logger.error(f"Error updating newsletter: {e}")
            db.session.rollback()
            return None
    @staticmethod
    def delete_newsletter(newsletter_id: int, user_id: int) -> bool:
        """Delete a newsletter"""
        try:
            newsletter = Notification.query.filter_by(
                id=newsletter_id,
                category='newsletter'
            ).first()
            
            if not newsletter:
                return False
            
            db.session.delete(newsletter)
            db.session.commit()
            logger.info(f"Deleted newsletter {newsletter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting newsletter: {e}")
            db.session.rollback()
            return False
    @staticmethod
    def clear_all_newsletters(user_id: int) -> int:
        """Delete all newsletters"""
        try:
            count = Notification.query.filter_by(category='newsletter').delete()
            db.session.commit()
            logger.info(f"Cleared {count} newsletters")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing newsletters: {e}")
            db.session.rollback()
            return 0
# Singleton instance
notification_service = NotificationService()