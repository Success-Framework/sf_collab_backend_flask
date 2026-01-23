"""
SF Collab Notification Helpers
Convenient helper functions for common notification scenarios
"""

from typing import Optional, Dict, Any, List
from app.notifications.service import notification_service
import logging

logger = logging.getLogger(__name__)


# ===========================================
# ACCOUNT & SYSTEM NOTIFICATIONS
# ===========================================

def notify_account_created(user_id: int):
    """Notify user their account was created"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="ACCOUNT_CREATED"
    )


def notify_email_verified(user_id: int):
    """Notify user their email was verified"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="EMAIL_VERIFIED"
    )


def notify_password_changed(user_id: int):
    """Notify user their password was changed"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PASSWORD_CHANGED"
    )


def notify_new_device_login(user_id: int, location: str):
    """Notify user of login from new device"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="NEW_DEVICE_LOGIN",
        variables={"location": location}
    )


# ===========================================
# SOCIAL NOTIFICATIONS
# ===========================================

def notify_user_followed(user_id: int, follower_id: int, follower_name: str):
    """Notify user they have a new follower"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="USER_FOLLOWED",
        variables={"actor_name": follower_name},
        actor_id=follower_id
    )


def notify_user_mentioned(user_id: int, actor_id: int, actor_name: str, entity_type: str, entity_id: int):
    """Notify user they were mentioned"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="USER_MENTIONED",
        variables={"actor_name": actor_name, "entity_type": entity_type},
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id
    )


def notify_comment_reply(user_id: int, replier_id: int, replier_name: str, comment_id: int):
    """Notify user of a reply to their comment"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="COMMENT_REPLY",
        variables={"actor_name": replier_name},
        actor_id=replier_id,
        entity_type="comment",
        entity_id=comment_id
    )


def notify_post_liked(user_id: int, liker_id: int, liker_name: str, post_id: int):
    """Notify user their post was liked"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="POST_LIKED",
        variables={"actor_name": liker_name},
        actor_id=liker_id,
        entity_type="post",
        entity_id=post_id
    )


def notify_new_comment(user_id: int, commenter_id: int, commenter_name: str, entity_type: str, entity_id: int):
    """Notify user of a new comment on their content"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="NEW_COMMENT",
        variables={"actor_name": commenter_name, "entity_type": entity_type},
        actor_id=commenter_id,
        entity_type=entity_type,
        entity_id=entity_id
    )


# ===========================================
# IDEA NOTIFICATIONS
# ===========================================

def notify_idea_submitted(user_id: int, idea_title: str, idea_id: int):
    """Notify user their idea was submitted"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_SUBMITTED",
        variables={"title": idea_title},
        entity_type="idea",
        entity_id=idea_id
    )


def notify_idea_feedback(user_id: int, feedback_giver_id: int, feedback_giver_name: str, idea_title: str, idea_id: int):
    """Notify user they received feedback on their idea"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_FEEDBACK_RECEIVED",
        variables={"actor_name": feedback_giver_name, "title": idea_title},
        actor_id=feedback_giver_id,
        entity_type="idea",
        entity_id=idea_id
    )


def notify_idea_approved(user_id: int, idea_title: str, idea_id: int):
    """Notify user their idea was approved"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_APPROVED",
        variables={"title": idea_title},
        entity_type="idea",
        entity_id=idea_id
    )


def notify_idea_rejected(user_id: int, idea_title: str, idea_id: int, reason: str):
    """Notify user their idea was rejected"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_REJECTED",
        variables={"title": idea_title, "reason": reason},
        entity_type="idea",
        entity_id=idea_id
    )


def notify_idea_to_startup(user_id: int, idea_title: str, idea_id: int, startup_id: int):
    """Notify user their idea became a startup"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_TO_STARTUP",
        variables={"title": idea_title},
        entity_type="idea",
        entity_id=idea_id,
        metadata={"startup_id": startup_id}
    )


# ===========================================
# STARTUP & PROJECT NOTIFICATIONS
# ===========================================

def notify_startup_created(user_id: int, startup_name: str, startup_id: int):
    """Notify user their startup was created"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="STARTUP_CREATED",
        variables={"name": startup_name},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_added_to_startup(user_id: int, startup_name: str, startup_id: int, role: str):
    """Notify user they were added to a startup"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="ADDED_TO_STARTUP",
        variables={"startup_name": startup_name, "role": role},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_removed_from_startup(user_id: int, startup_name: str, startup_id: int):
    """Notify user they were removed from a startup"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="REMOVED_FROM_STARTUP",
        variables={"startup_name": startup_name},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_startup_milestone(user_ids: List[int], startup_name: str, startup_id: int, milestone: str):
    """Notify startup members of a milestone achievement"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="STARTUP_MILESTONE_ACHIEVED",
        variables={"startup_name": startup_name, "milestone": milestone},
        entity_type="startup",
        entity_id=startup_id
    )


# ===========================================
# TASK NOTIFICATIONS
# ===========================================

def notify_task_assigned(user_id: int, assigner_id: int, assigner_name: str, task_title: str, task_id: int):
    """Notify user they were assigned a task"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="TASK_ASSIGNED",
        variables={"actor_name": assigner_name, "title": task_title},
        actor_id=assigner_id,
        entity_type="task",
        entity_id=task_id
    )


def notify_task_completed(user_id: int, completer_id: int, completer_name: str, task_title: str, task_id: int):
    """Notify task owner that task was completed"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="TASK_COMPLETED",
        variables={"actor_name": completer_name, "title": task_title},
        actor_id=completer_id,
        entity_type="task",
        entity_id=task_id
    )


def notify_task_overdue(user_id: int, task_title: str, task_id: int, due_date: str):
    """Notify user their task is overdue"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="TASK_OVERDUE",
        variables={"title": task_title, "due_date": due_date},
        entity_type="task",
        entity_id=task_id
    )


def notify_task_deadline_approaching(user_id: int, task_title: str, task_id: int, time_until: str):
    """Notify user task deadline is approaching"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="TASK_DEADLINE_APPROACHING",
        variables={"title": task_title, "time_until": time_until},
        entity_type="task",
        entity_id=task_id
    )


# ===========================================
# MESSAGING NOTIFICATIONS
# ===========================================

def notify_new_message(user_id: int, sender_id: int, sender_name: str, message_id: int):
    """Notify user of a new direct message"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="NEW_DIRECT_MESSAGE",
        variables={"actor_name": sender_name},
        actor_id=sender_id,
        entity_type="message",
        entity_id=message_id
    )


def notify_group_message(user_id: int, sender_id: int, sender_name: str, group_name: str, message_id: int):
    """Notify user of a new group message"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="NEW_GROUP_MESSAGE",
        variables={"actor_name": sender_name, "group_name": group_name},
        actor_id=sender_id,
        entity_type="message",
        entity_id=message_id
    )


# ===========================================
# REWARDS & POINTS NOTIFICATIONS
# ===========================================

def notify_points_earned(user_id: int, points: int, reason: str):
    """Notify user they earned points"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="POINTS_EARNED",
        variables={"points": points, "reason": reason}
    )


def notify_points_deducted(user_id: int, points: int, reason: str):
    """Notify user points were deducted"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="POINTS_DEDUCTED",
        variables={"points": points, "reason": reason}
    )


def notify_level_up(user_id: int, level: int):
    """Notify user they leveled up"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="LEVEL_UP",
        variables={"level": level}
    )


def notify_payment_received(user_id: int, amount: str, sender_name: str):
    """Notify user they received a payment"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PAYMENT_RECEIVED",
        variables={"amount": amount, "sender": sender_name}
    )


# ===========================================
# INVESTOR & FUNDING NOTIFICATIONS
# ===========================================

def notify_investor_interest(user_id: int, investor_name: str, startup_id: int):
    """Notify startup owner of investor interest"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="INVESTOR_INTEREST",
        variables={"investor_name": investor_name},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_investment_received(user_id: int, amount: str, investor_name: str, startup_id: int):
    """Notify startup owner of investment received"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="INVESTMENT_RECEIVED",
        variables={"amount": amount, "investor": investor_name},
        entity_type="startup",
        entity_id=startup_id
    )


# ===========================================
# MODERATION & GOVERNANCE NOTIFICATIONS
# ===========================================

def notify_content_reported(user_id: int, reason: str, content_type: str, content_id: int):
    """Notify user their content was reported"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="CONTENT_REPORTED",
        variables={"reason": reason},
        entity_type=content_type,
        entity_id=content_id
    )


def notify_warning_issued(user_id: int, reason: str):
    """Notify user they received a warning"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="WARNING_ISSUED",
        variables={"reason": reason}
    )


def notify_vote_started(user_ids: List[int], vote_title: str, vote_id: int):
    """Notify users a vote has started"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="VOTE_STARTED",
        variables={"title": vote_title},
        entity_type="vote",
        entity_id=vote_id
    )


# ===========================================
# EVENT NOTIFICATIONS
# ===========================================

def notify_event_reminder(user_id: int, event_title: str, event_id: int, time_until: str):
    """Notify user of upcoming event"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="EVENT_REMINDER",
        variables={"title": event_title, "time_until": time_until},
        entity_type="event",
        entity_id=event_id
    )


def notify_event_starting_soon(user_id: int, event_title: str, event_id: int, minutes: int):
    """Notify user event is starting soon"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="EVENT_STARTING_SOON",
        variables={"title": event_title, "minutes": minutes},
        entity_type="event",
        entity_id=event_id
    )


# ===========================================
# GENERIC NOTIFICATIONS
# ===========================================

def notify_success(user_id: int, message: str, **kwargs):
    """Send a generic success notification"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="GENERIC_SUCCESS",
        variables={"message": message},
        **kwargs
    )


def notify_info(user_id: int, message: str, **kwargs):
    """Send a generic info notification"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="GENERIC_INFO",
        variables={"message": message},
        **kwargs
    )


def notify_warning(user_id: int, message: str, **kwargs):
    """Send a generic warning notification"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="GENERIC_WARNING",
        variables={"message": message},
        **kwargs
    )


def notify_error(user_id: int, message: str, **kwargs):
    """Send a generic error notification"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="GENERIC_ERROR",
        variables={"message": message},
        **kwargs
    )