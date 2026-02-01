"""
SF Collab Notification Helpers
Complete helper functions for ALL notification types (4.1 - 4.12)
Based on SF Collab Notification System Documentation
"""

from typing import Optional, Dict, Any, List
from app.notifications.service import notification_service
from app.models.transaction import Transaction
import logging

logger = logging.getLogger(__name__)


# ===========================================
# 4.1 ACCOUNT & SYSTEM NOTIFICATIONS
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


def notify_password_reset(user_id: int):
    """Notify user a password reset was requested"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PASSWORD_RESET"
    )


def notify_new_device_login(user_id: int, location: str):
    """Notify user of login from new device"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="NEW_DEVICE_LOGIN",
        variables={"location": location}
    )


def notify_account_role_updated(user_id: int, role: str):
    """Notify user their role was updated"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="ACCOUNT_ROLE_UPDATED",
        variables={"role": role}
    )


def notify_permission_changed(user_id: int):
    """Notify user their permissions changed"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PERMISSION_CHANGED"
    )


def notify_account_suspended(user_id: int, reason: str):
    """Notify user their account was suspended"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="ACCOUNT_SUSPENDED",
        variables={"reason": reason}
    )


def notify_account_reinstated(user_id: int):
    """Notify user their account was reinstated"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="ACCOUNT_REINSTATED"
    )


def notify_platform_maintenance(user_ids: List[int], date: str, duration: str):
    """Notify users of scheduled maintenance"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="PLATFORM_MAINTENANCE",
        variables={"date": date, "duration": duration}
    )


def notify_terms_policy_update(user_ids: List[int]):
    """Notify users of terms/policy updates"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="TERMS_POLICY_UPDATE"
    )


# ===========================================
# 4.2 COLLABORATION & SOCIAL NOTIFICATIONS
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


def notify_post_reacted(user_id: int, reactor_id: int, reactor_name: str, entity_type: str, entity_id: int):
    """Notify user of a reaction to their content"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="POST_REACTED",
        variables={"actor_name": reactor_name, "entity_type": entity_type},
        actor_id=reactor_id,
        entity_type=entity_type,
        entity_id=entity_id
    )


def notify_content_shared(user_id: int, sharer_id: int, sharer_name: str, entity_type: str, entity_id: int):
    """Notify user their content was shared"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="CONTENT_SHARED",
        variables={"actor_name": sharer_name},
        actor_id=sharer_id,
        entity_type=entity_type,
        entity_id=entity_id
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


def notify_new_post_in_category(user_id: int, category: str, post_title: str, post_id: int):
    """Notify user of new post in followed category"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="NEW_POST_IN_CATEGORY",
        variables={"category": category, "title": post_title},
        entity_type="post",
        entity_id=post_id
    )


def notify_new_community_member(user_ids: List[int], member_id: int, member_name: str, entity_name: str, entity_id: int):
    """Notify community members of new member"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="NEW_COMMUNITY_MEMBER",
        variables={"actor_name": member_name, "entity_name": entity_name},
        actor_id=member_id,
        entity_type="community",
        entity_id=entity_id
    )


# ===========================================
# 4.3 IDEAS & INNOVATION NOTIFICATIONS
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


def notify_idea_flagged(user_id: int, idea_title: str, idea_id: int):
    """Notify user their idea was flagged"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_FLAGGED",
        variables={"title": idea_title},
        entity_type="idea",
        entity_id=idea_id
    )


def notify_idea_status_changed(user_id: int, idea_title: str, idea_id: int, old_status: str, new_status: str):
    """Notify user their idea status changed"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_STATUS_CHANGED",
        variables={"title": idea_title, "old_status": old_status, "new_status": new_status},
        entity_type="idea",
        entity_id=idea_id
    )


def notify_idea_to_project(user_id: int, idea_title: str, idea_id: int, project_id: int):
    """Notify user their idea was promoted to project"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_TO_PROJECT",
        variables={"title": idea_title},
        entity_type="idea",
        entity_id=idea_id,
        metadata={"project_id": project_id}
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


def notify_idea_voted(user_id: int, voter_id: int, voter_name: str, idea_title: str, idea_id: int):
    """Notify user someone voted on their idea"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_VOTED",
        variables={"actor_name": voter_name, "title": idea_title},
        actor_id=voter_id,
        entity_type="idea",
        entity_id=idea_id
    )


def notify_idea_milestone_reached(user_id: int, idea_title: str, idea_id: int, milestone: str):
    """Notify user their idea reached a milestone"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_MILESTONE_REACHED",
        variables={"title": idea_title, "milestone": milestone},
        entity_type="idea",
        entity_id=idea_id
    )


def notify_idea_collaboration_request(user_id: int, requester_id: int, requester_name: str, idea_title: str, idea_id: int):
    """Notify user someone wants to collaborate on their idea"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="IDEA_COLLABORATION_REQUEST",
        variables={"actor_name": requester_name, "title": idea_title},
        actor_id=requester_id,
        entity_type="idea",
        entity_id=idea_id
    )


# ===========================================
# 4.4 STARTUP & PROJECT NOTIFICATIONS
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


def notify_startup_profile_updated(user_ids: List[int], startup_name: str, startup_id: int):
    """Notify startup members of profile update"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="STARTUP_PROFILE_UPDATED",
        variables={"name": startup_name},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_project_created(user_ids: List[int], project_name: str, project_id: int):
    """Notify users of new project"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="PROJECT_CREATED",
        variables={"name": project_name},
        entity_type="project",
        entity_id=project_id
    )


def notify_project_status_changed(user_ids: List[int], project_name: str, project_id: int, status: str):
    """Notify users of project status change"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="PROJECT_STATUS_CHANGED",
        variables={"name": project_name, "status": status},
        entity_type="project",
        entity_id=project_id
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


def notify_startup_role_assigned(user_id: int, startup_name: str, startup_id: int, role: str):
    """Notify user of role assignment in startup"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="STARTUP_ROLE_ASSIGNED",
        variables={"startup_name": startup_name, "role": role},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_startup_ownership_changed(user_ids: List[int], startup_name: str, startup_id: int, new_owner: str):
    """Notify startup members of ownership change"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="STARTUP_OWNERSHIP_CHANGED",
        variables={"startup_name": startup_name, "new_owner": new_owner},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_startup_milestone(user_ids: List[int], startup_name: str, startup_id: int, milestone: str):
    """Notify startup members of milestone achievement"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="STARTUP_MILESTONE_ACHIEVED",
        variables={"startup_name": startup_name, "milestone": milestone},
        entity_type="startup",
        entity_id=startup_id
    )


# ===========================================
# 4.5 TASK & EXECUTION NOTIFICATIONS
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


def notify_task_updated(user_id: int, task_title: str, task_id: int):
    """Notify user task was updated"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="TASK_UPDATED",
        variables={"title": task_title},
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


def notify_task_reassigned(user_id: int, task_title: str, task_id: int, new_assignee: str):
    """Notify user task was reassigned"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="TASK_REASSIGNED",
        variables={"title": task_title, "new_assignee": new_assignee},
        entity_type="task",
        entity_id=task_id
    )


def notify_task_comment_added(user_id: int, commenter_id: int, commenter_name: str, task_title: str, task_id: int):
    """Notify user of comment on task"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="TASK_COMMENT_ADDED",
        variables={"actor_name": commenter_name, "title": task_title},
        actor_id=commenter_id,
        entity_type="task",
        entity_id=task_id
    )


def notify_task_file_attached(user_id: int, uploader_id: int, uploader_name: str, task_title: str, task_id: int):
    """Notify user of file attached to task"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="TASK_FILE_ATTACHED",
        variables={"actor_name": uploader_name, "title": task_title},
        actor_id=uploader_id,
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


def notify_meeting_scheduled(user_ids: List[int], meeting_title: str, meeting_id: int, date: str):
    """Notify users of scheduled meeting"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="MEETING_SCHEDULED",
        variables={"title": meeting_title, "date": date},
        entity_type="meeting",
        entity_id=meeting_id
    )


def notify_meeting_updated(user_ids: List[int], meeting_title: str, meeting_id: int):
    """Notify users of meeting update"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="MEETING_UPDATED",
        variables={"title": meeting_title},
        entity_type="meeting",
        entity_id=meeting_id
    )


def notify_meeting_canceled(user_ids: List[int], meeting_title: str, meeting_id: int, date: str):
    """Notify users of meeting cancellation"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="MEETING_CANCELED",
        variables={"title": meeting_title, "date": date},
        entity_type="meeting",
        entity_id=meeting_id
    )


# ===========================================
# 4.6 MESSAGING & COMMUNICATION
# ===========================================

def notify_new_message(user_id: int, sender_id: int, sender_name: str, message_id: int = None, conversation_id: int = None):
    """Notify user of a new direct message"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="NEW_DIRECT_MESSAGE",
        variables={"actor_name": sender_name},
        actor_id=sender_id,
        entity_type="message",
        entity_id=message_id or conversation_id
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


def notify_mention_in_chat(user_id: int, mentioner_id: int, mentioner_name: str, chat_name: str, message_id: int):
    """Notify user of mention in chat"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="MENTION_IN_CHAT",
        variables={"actor_name": mentioner_name, "chat_name": chat_name},
        actor_id=mentioner_id,
        entity_type="message",
        entity_id=message_id
    )


def notify_message_request(user_id: int, requester_id: int, requester_name: str):
    """Notify user of message request"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="MESSAGE_REQUEST",
        variables={"actor_name": requester_name},
        actor_id=requester_id
    )


def notify_message_reaction(user_id: int, reactor_id: int, reactor_name: str, message_id: int):
    """Notify user of message reaction"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="MESSAGE_REACTION",
        variables={"actor_name": reactor_name},
        actor_id=reactor_id,
        entity_type="message",
        entity_id=message_id
    )


def notify_voice_message_received(user_id: int, sender_id: int, sender_name: str, message_id: int):
    """Notify user of voice message"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="VOICE_MESSAGE_RECEIVED",
        variables={"actor_name": sender_name},
        actor_id=sender_id,
        entity_type="message",
        entity_id=message_id
    )


# ===========================================
# 4.7 FILE & RESOURCE NOTIFICATIONS
# ===========================================

def notify_file_uploaded(user_ids: List[int], uploader_id: int, uploader_name: str, filename: str, location: str, file_id: int):
    """Notify users of file upload"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="FILE_UPLOADED",
        variables={"actor_name": uploader_name, "filename": filename, "location": location},
        actor_id=uploader_id,
        entity_type="file",
        entity_id=file_id
    )


def notify_file_updated(user_ids: List[int], updater_id: int, updater_name: str, filename: str, file_id: int):
    """Notify users of file update"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="FILE_UPDATED",
        variables={"actor_name": updater_name, "filename": filename},
        actor_id=updater_id,
        entity_type="file",
        entity_id=file_id
    )


def notify_file_deleted(user_ids: List[int], deleter_id: int, deleter_name: str, filename: str):
    """Notify users of file deletion"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="FILE_DELETED",
        variables={"actor_name": deleter_name, "filename": filename},
        actor_id=deleter_id
    )


def notify_file_access_granted(user_id: int, filename: str, file_id: int):
    """Notify user of file access granted"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="FILE_ACCESS_GRANTED",
        variables={"filename": filename},
        entity_type="file",
        entity_id=file_id
    )


def notify_file_access_revoked(user_id: int, filename: str):
    """Notify user of file access revoked"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="FILE_ACCESS_REVOKED",
        variables={"filename": filename}
    )


def notify_file_comment_added(user_id: int, commenter_id: int, commenter_name: str, filename: str, file_id: int):
    """Notify user of comment on file"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="FILE_COMMENT_ADDED",
        variables={"actor_name": commenter_name, "filename": filename},
        actor_id=commenter_id,
        entity_type="file",
        entity_id=file_id
    )


def notify_file_new_version(user_ids: List[int], filename: str, file_id: int):
    """Notify users of new file version"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="FILE_NEW_VERSION",
        variables={"filename": filename},
        entity_type="file",
        entity_id=file_id
    )


# ===========================================
# 4.8 REWARDS, POINTS & ECONOMY
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


def notify_reward_claimed(user_id: int, reward_name: str, reward_id: int = None):
    """Notify user they claimed a reward"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="REWARD_CLAIMED",
        variables={"reward_name": reward_name},
        entity_type="reward",
        entity_id=reward_id
    )


def notify_payment_sent(user_id: int, amount: str, recipient: str, payment_id: int = None, transaction: Transaction = None):
    """Notify user payment was sent"""
    print("Transaction in notify_payment_sent:", transaction)
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PAYMENT_SENT",
        variables={"amount": amount, "recipient": recipient},
        entity_type="payment",
        entity_id=payment_id,
        transaction=transaction
    )


def notify_payment_received(user_id: int, amount: str, sender_name: str, payment_id: int = None):
    """Notify user they received a payment"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PAYMENT_RECEIVED",
        variables={"amount": amount, "sender": sender_name},
        entity_type="payment",
        entity_id=payment_id,
        send_email=True
    )


def notify_bounty_posted(user_ids: List[int], bounty_title: str, amount: str, bounty_id: int):
    """Notify users of new bounty"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="BOUNTY_POSTED",
        variables={"title": bounty_title, "amount": amount},
        entity_type="bounty",
        entity_id=bounty_id
    )


def notify_bounty_completed(user_id: int, bounty_title: str, amount: str, bounty_id: int):
    """Notify user they completed a bounty"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="BOUNTY_COMPLETED",
        variables={"title": bounty_title, "amount": amount},
        entity_type="bounty",
        entity_id=bounty_id
    )


def notify_revenue_share_update(user_id: int, period: str, amount: str):
    """Notify user of revenue share update"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="REVENUE_SHARE_UPDATE",
        variables={"period": period, "amount": amount}
    )


def notify_contribution_verified(user_id: int, project: str, contribution_id: int = None):
    """Notify user their contribution was verified"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="CONTRIBUTION_VERIFIED",
        variables={"project": project},
        entity_type="contribution",
        entity_id=contribution_id
    )


def notify_level_up(user_id: int, level: int):
    """Notify user they leveled up"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="LEVEL_UP",
        variables={"level": level}
    )


def notify_rank_upgraded(user_id: int, rank: str):
    """Notify user of rank upgrade"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="RANK_UPGRADED",
        variables={"rank": rank}
    )


# ===========================================
# 4.9 GOVERNANCE, MODERATION & TRUST
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


def notify_report_resolved(user_id: int, content_type: str, report_id: int = None):
    """Notify user their report was resolved"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="REPORT_RESOLVED",
        variables={"content_type": content_type},
        entity_type="report",
        entity_id=report_id
    )


def notify_warning_issued(user_id: int, reason: str):
    """Notify user they received a warning"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="WARNING_ISSUED",
        variables={"reason": reason}
    )


def notify_moderation_action_taken(user_id: int, action: str, reason: str, content_id: int = None):
    """Notify user of moderation action"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="MODERATION_ACTION_TAKEN",
        variables={"action": action, "reason": reason},
        entity_type="content",
        entity_id=content_id
    )


def notify_appeal_status_update(user_id: int, status: str, appeal_id: int = None):
    """Notify user of appeal status"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="APPEAL_STATUS_UPDATE",
        variables={"status": status},
        entity_type="appeal",
        entity_id=appeal_id
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


def notify_vote_result_announced(user_ids: List[int], vote_title: str, result: str, vote_id: int):
    """Notify users of vote result"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="VOTE_RESULT_ANNOUNCED",
        variables={"title": vote_title, "result": result},
        entity_type="vote",
        entity_id=vote_id
    )


def notify_proposal_accepted(user_id: int, proposal_title: str, proposal_id: int):
    """Notify user their proposal was accepted"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PROPOSAL_ACCEPTED",
        variables={"title": proposal_title},
        entity_type="proposal",
        entity_id=proposal_id
    )


def notify_proposal_rejected(user_id: int, proposal_title: str, proposal_id: int):
    """Notify user their proposal was rejected"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PROPOSAL_REJECTED",
        variables={"title": proposal_title},
        entity_type="proposal",
        entity_id=proposal_id
    )


# ===========================================
# 4.10 INVESTOR & FUNDING NOTIFICATIONS
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


def notify_pitch_deck_viewed(user_id: int, viewer_name: str, startup_id: int):
    """Notify startup owner pitch deck was viewed"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="PITCH_DECK_VIEWED",
        variables={"viewer_name": viewer_name},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_funding_round_opened(user_ids: List[int], startup_name: str, startup_id: int):
    """Notify users of funding round opening"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="FUNDING_ROUND_OPENED",
        variables={"startup_name": startup_name},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_funding_milestone_reached(user_ids: List[int], startup_name: str, percentage: str, startup_id: int):
    """Notify users of funding milestone"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="FUNDING_MILESTONE_REACHED",
        variables={"startup_name": startup_name, "percentage": percentage},
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


def notify_due_diligence_request(user_id: int, investor_name: str, startup_id: int):
    """Notify startup owner of due diligence request"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="DUE_DILIGENCE_REQUEST",
        variables={"investor_name": investor_name},
        entity_type="startup",
        entity_id=startup_id
    )


def notify_campaign_update_posted(user_ids: List[int], campaign_name: str, campaign_id: int):
    """Notify users of campaign update"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="CAMPAIGN_UPDATE_POSTED",
        variables={"campaign_name": campaign_name},
        entity_type="campaign",
        entity_id=campaign_id
    )


# ===========================================
# 4.11 AI & AUTOMATION NOTIFICATIONS
# ===========================================

def notify_ai_suggestion_available(user_id: int, context: str):
    """Notify user AI has a suggestion"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="AI_SUGGESTION_AVAILABLE",
        variables={"context": context}
    )


def notify_ai_report_ready(user_id: int, report_title: str, report_id: int = None):
    """Notify user AI report is ready"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="AI_REPORT_READY",
        variables={"title": report_title},
        entity_type="report",
        entity_id=report_id
    )


def notify_automation_completed(user_id: int, automation_name: str, automation_id: int = None):
    """Notify user automation completed"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="AUTOMATION_COMPLETED",
        variables={"name": automation_name},
        entity_type="automation",
        entity_id=automation_id
    )


def notify_automation_failed(user_id: int, automation_name: str, error: str, automation_id: int = None):
    """Notify user automation failed"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="AUTOMATION_FAILED",
        variables={"name": automation_name, "error": error},
        entity_type="automation",
        entity_id=automation_id
    )


def notify_ai_recommendation(user_id: int, recommendation: str):
    """Notify user of AI recommendation"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="AI_RECOMMENDATION",
        variables={"recommendation": recommendation}
    )


def notify_smart_reminder(user_id: int, entity_type: str, title: str, entity_id: int = None):
    """Send smart reminder notification"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="SMART_REMINDER",
        variables={"entity_type": entity_type, "title": title},
        entity_type=entity_type,
        entity_id=entity_id
    )


# ===========================================
# 4.12 EVENT & TIME-BASED NOTIFICATIONS
# ===========================================

def notify_event_created(user_ids: List[int], event_title: str, event_id: int, date: str):
    """Notify users of event creation"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="EVENT_CREATED",
        variables={"title": event_title, "date": date},
        entity_type="event",
        entity_id=event_id
    )


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


def notify_event_canceled(user_ids: List[int], event_title: str, event_id: int, date: str):
    """Notify users of event cancellation"""
    return notification_service.bulk_create_notifications(
        user_ids=user_ids,
        template_key="EVENT_CANCELED",
        variables={"title": event_title, "date": date},
        entity_type="event",
        entity_id=event_id
    )


def notify_deadline_reminder(user_id: int, title: str, time_until: str, entity_type: str = None, entity_id: int = None):
    """Notify user of deadline"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="DEADLINE_REMINDER",
        variables={"title": title, "time_until": time_until},
        entity_type=entity_type,
        entity_id=entity_id
    )


def notify_daily_summary(user_id: int, date: str):
    """Notify user daily summary is ready"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="DAILY_SUMMARY",
        variables={"date": date}
    )


def notify_weekly_summary(user_id: int):
    """Notify user weekly summary is ready"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="WEEKLY_SUMMARY"
    )


# ===========================================
# 4.13 FRIEND & CONNECTION NOTIFICATIONS
# ===========================================

def notify_friend_request_received(user_id: int, sender_id: int, sender_name: str, request_id: int = None):
    """Notify user of friend request"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="FRIEND_REQUEST_RECEIVED",
        variables={"actor_name": sender_name},
        actor_id=sender_id,
        entity_type="friend_request",
        entity_id=request_id
    )


def notify_friend_request_accepted(user_id: int, accepter_id: int, accepter_name: str, request_id: int = None):
    """Notify user friend request was accepted"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="FRIEND_REQUEST_ACCEPTED",
        variables={"actor_name": accepter_name},
        actor_id=accepter_id,
        entity_type="friend_request",
        entity_id=request_id
    )


def notify_connection_request(user_id: int, requester_id: int, requester_name: str, request_id: int = None):
    """Notify user of connection request"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="CONNECTION_REQUEST",
        variables={"actor_name": requester_name},
        actor_id=requester_id,
        entity_type="connection_request",
        entity_id=request_id
    )


# ===========================================
# 4.14 APPLICATION & ACCESS NOTIFICATIONS
# ===========================================

def notify_application_submitted(user_id: int, position: str, application_id: int):
    """Notify user their application was submitted"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="APPLICATION_SUBMITTED",
        variables={"position": position},
        entity_type="application",
        entity_id=application_id
    )


def notify_application_approved(user_id: int, position: str, application_id: int):
    """Notify user their application was approved"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="APPLICATION_APPROVED",
        variables={"position": position},
        entity_type="application",
        entity_id=application_id
    )


def notify_application_rejected(user_id: int, position: str, application_id: int):
    """Notify user their application was rejected"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="APPLICATION_REJECTED",
        variables={"position": position},
        entity_type="application",
        entity_id=application_id
    )


def notify_access_request_pending(user_id: int, resource: str, request_id: int = None):
    """Notify user their access request is pending"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="ACCESS_REQUEST_PENDING",
        variables={"resource": resource},
        entity_type="access_request",
        entity_id=request_id
    )


def notify_access_granted(user_id: int, resource: str, resource_id: int = None):
    """Notify user access was granted"""
    return notification_service.create_notification(
        user_id=user_id,
        template_key="ACCESS_GRANTED",
        variables={"resource": resource},
        entity_type="resource",
        entity_id=resource_id
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