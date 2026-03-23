"""
Chat Utilities - General Chat & Team Chats
Handles:
1. Site-wide General Chat (auto-join all users)
2. Team/Workspace Chats (founders + their team members)
"""

from datetime import datetime
from app.extensions import db
from app.models.chatConversation import ChatConversation, conversation_participants
from app.models.chatMessage import ChatMessage
import logging


# ============================================
# GENERAL CHAT (Site-wide, everyone joins)
# ============================================

GENERAL_CHAT_NAME = "🌐 Community Lounge"
GENERAL_CHAT_DESCRIPTION = "Welcome to the community! This is the general chat where everyone can hang out and connect."


def get_or_create_general_chat(admin_user_id=None):
    """
    Get the general chat conversation, or create it if it doesn't exist.
    This is the site-wide chat that ALL users join automatically.
    """
    general_chat = ChatConversation.query.filter_by(
        name=GENERAL_CHAT_NAME,
        conversation_type='general',
        is_active=True
    ).first()
    
    if general_chat:
        return general_chat
    
    try:
        creator_id = admin_user_id or 1
        
        general_chat = ChatConversation(
            name=GENERAL_CHAT_NAME,
            description=GENERAL_CHAT_DESCRIPTION,
            conversation_type='general',
            created_by_id=creator_id,
            is_active=True,
            settings={
                'is_general_chat': True,
                'auto_join': True,
                'allow_leave': False,
                'chat_category': 'community'
            }
        )
        
        db.session.add(general_chat)
        db.session.commit()
        
        from app.models.user import User
        creator = User.query.get(creator_id)
        if creator:
            general_chat.add_participant(creator, 'admin')
        
        welcome_message = ChatMessage(
            conversation_id=general_chat.id,
            sender_id=creator_id,
            original_content="👋 Welcome to the Community Lounge! This is our general chat where everyone can connect. Feel free to introduce yourself!",
            message_type='system',
            sender_timezone='UTC'
        )
        db.session.add(welcome_message)
        db.session.commit()
        
        logging.info(f"General chat created with ID: {general_chat.id}")
        return general_chat
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to create general chat: {e}")
        raise


def add_user_to_general_chat(user):
    """Add a user to the general community chat."""
    try:
        general_chat = get_or_create_general_chat()
        
        if not general_chat:
            logging.error("Could not find or create general chat")
            return False
        
        if general_chat.is_user_participant(user.id):
            return True
        
        general_chat.add_participant(user, 'member')
        
        join_message = ChatMessage(
            conversation_id=general_chat.id,
            sender_id=user.id,
            original_content=f"👋 {user.first_name} {user.last_name} joined the community!",
            message_type='system',
            metadata_data={'action': 'user_joined', 'user_id': user.id},
            sender_timezone='UTC'
        )
        db.session.add(join_message)
        general_chat.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit socket event
        try:
            from app.socket_events import emit_new_message
            emit_new_message(general_chat.id, join_message.to_dict())
        except ImportError:
            pass
        
        logging.info(f"User {user.id} added to general chat")
        return True
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to add user {user.id} to general chat: {e}")
        return False


# ============================================
# TEAM CHATS (Founders + Team Members)
# ============================================

def get_or_create_team_chat(founder, team_name=None):
    """
    Get or create a team chat for a founder and their team.
    Each founder has ONE team chat that all their team members join.
    
    Args:
        founder: User model instance (the founder/team owner)
        team_name: Optional custom name for the team chat
    
    Returns:
        ChatConversation: The team chat
    """
    # Check if founder already has a team chat
    existing_team_chat = ChatConversation.query.filter_by(
        created_by_id=founder.id,
        conversation_type='team',
        is_active=True
    ).first()
    
    if existing_team_chat:
        return existing_team_chat
    
    try:
        chat_name = team_name or f"🚀 {founder.first_name}'s Team"
        
        team_chat = ChatConversation(
            name=chat_name,
            description=f"Private team chat for {founder.first_name}'s team. Collaborate and communicate here!",
            conversation_type='team',
            created_by_id=founder.id,
            is_active=True,
            settings={
                'is_team_chat': True,
                'founder_id': founder.id,
                'auto_join_team': True,
                'allow_leave': False,
                'chat_category': 'team'
            }
        )
        
        db.session.add(team_chat)
        db.session.commit()
        
        # Add founder as admin
        team_chat.add_participant(founder, 'admin')
        
        # Welcome message
        welcome_message = ChatMessage(
            conversation_id=team_chat.id,
            sender_id=founder.id,
            original_content=f"🚀 Welcome to the team chat! This is a private space for {founder.first_name}'s team to collaborate.",
            message_type='system',
            sender_timezone='UTC'
        )
        db.session.add(welcome_message)
        db.session.commit()
        
        logging.info(f"Team chat created for founder {founder.id}")
        return team_chat
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to create team chat for founder {founder.id}: {e}")
        raise


def add_member_to_team_chat(founder_id, team_member):
    """
    Add a team member to a founder's team chat.
    Called when a founder adds someone to their team.
    
    Args:
        founder_id: ID of the founder (team owner)
        team_member: User model instance of the new team member
    
    Returns:
        bool: Success status
    """
    try:
        from app.models.user import User
        founder = User.query.get(founder_id)
        
        if not founder:
            logging.error(f"Founder {founder_id} not found")
            return False
        
        team_chat = get_or_create_team_chat(founder)
        
        if not team_chat:
            logging.error(f"Could not find or create team chat for founder {founder_id}")
            return False
        
        if team_chat.is_user_participant(team_member.id):
            logging.info(f"User {team_member.id} already in team chat")
            return True
        
        team_chat.add_participant(team_member, 'member')
        
        # System message
        join_message = ChatMessage(
            conversation_id=team_chat.id,
            sender_id=founder_id,
            original_content=f"🎉 {team_member.first_name} {team_member.last_name} joined the team!",
            message_type='system',
            metadata_data={
                'action': 'team_member_added',
                'user_id': team_member.id,
                'added_by': founder_id
            },
            sender_timezone='UTC'
        )
        db.session.add(join_message)
        team_chat.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit socket events
        try:
            from app.socket_events import emit_new_message, emit_to_user
            emit_new_message(team_chat.id, join_message.to_dict())
            emit_to_user(team_member.id, 'added_to_team_chat', {
                'conversation': team_chat.to_dict(for_user=team_member)
            })
        except ImportError:
            pass
        
        logging.info(f"User {team_member.id} added to team chat of founder {founder_id}")
        return True
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to add team member to chat: {e}")
        return False


def remove_member_from_team_chat(founder_id, team_member):
    """
    Remove a team member from a founder's team chat.
    Called when a founder removes someone from their team.
    """
    try:
        team_chat = ChatConversation.query.filter_by(
            created_by_id=founder_id,
            conversation_type='team',
            is_active=True
        ).first()
        
        if not team_chat:
            return True  # No team chat exists
        
        if not team_chat.is_user_participant(team_member.id):
            return True  # Not a participant
        
        team_chat.remove_participant(team_member)
        
        # System message
        leave_message = ChatMessage(
            conversation_id=team_chat.id,
            sender_id=founder_id,
            original_content=f"👋 {team_member.first_name} {team_member.last_name} left the team.",
            message_type='system',
            metadata_data={
                'action': 'team_member_removed',
                'user_id': team_member.id
            },
            sender_timezone='UTC'
        )
        db.session.add(leave_message)
        team_chat.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit socket events
        try:
            from app.socket_events import emit_new_message, emit_to_user
            emit_new_message(team_chat.id, leave_message.to_dict())
            emit_to_user(team_member.id, 'removed_from_team_chat', {
                'conversation_id': team_chat.id
            })
        except ImportError:
            pass
        
        logging.info(f"User {team_member.id} removed from team chat of founder {founder_id}")
        return True
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to remove team member from chat: {e}")
        return False


def get_user_team_chat(user_id):
    """
    Get the team chat a user belongs to (either as founder or member).
    
    Returns:
        ChatConversation or None
    """
    # Check if user is a founder with a team chat
    team_chat = ChatConversation.query.filter_by(
        created_by_id=user_id,
        conversation_type='team',
        is_active=True
    ).first()
    
    if team_chat:
        return team_chat
    
    # Check if user is a member of any team chat
    team_chat = ChatConversation.query\
        .join(conversation_participants)\
        .filter(conversation_participants.c.user_id == user_id)\
        .filter(ChatConversation.conversation_type == 'team')\
        .filter(ChatConversation.is_active == True)\
        .first()
    
    return team_chat


# ============================================
# COMBINED HOOKS
# ============================================

def on_user_profile_created(user):
    """
    Hook called after a user creates their profile.
    Adds them to the general chat.
    
    Usage:
        from app.utils.chat_utils import on_user_profile_created
        on_user_profile_created(new_user)
    """
    return add_user_to_general_chat(user)


def on_founder_created(founder, team_name=None):
    """
    Hook called when a founder account is created.
    Creates their team chat and startup group chat.
    
    Usage:
        from app.utils.chat_utils import on_founder_created
        on_founder_created(founder_user, "Acme Inc Team")
    """
    # Add to general chat
    add_user_to_general_chat(founder)
    
    # Create per-founder team chat (existing behaviour)
    team_chat = get_or_create_team_chat(founder, team_name)

    # ── NEW: create per-startup group chat and add founder immediately ────
    _sync_founder_startup_chats(founder, match_name=team_name)

    return team_chat


def on_team_member_added(founder_id, team_member):
    """
    Hook called when a founder adds a team member.
    Adds them to general chat, the founder's team chat, and all startup group chats.
    
    Usage:
        from app.utils.chat_utils import on_team_member_added
        on_team_member_added(founder.id, new_team_member)
    """
    # Add to general chat
    add_user_to_general_chat(team_member)
    
    # Add to per-founder team chat (existing behaviour)
    add_member_to_team_chat(founder_id, team_member)

    # ── NEW: add to every startup group chat owned by this founder ────────
    _sync_member_to_startup_chats(founder_id, team_member)


def on_team_member_removed(founder_id, team_member):
    """
    Hook called when a founder removes a team member.
    Removes them from the team chat and all startup group chats.
    
    Usage:
        from app.utils.chat_utils import on_team_member_removed
        on_team_member_removed(founder.id, removed_member)
    """
    # Remove from per-founder team chat (existing behaviour)
    remove_member_from_team_chat(founder_id, team_member)

    # ── NEW: remove from every startup group chat owned by this founder ───
    _remove_member_from_startup_chats(founder_id, team_member)


# ============================================
# ADMIN UTILITIES
# ============================================

def sync_all_users_to_general_chat():
    """Sync all existing users to the general chat."""
    from app.models.user import User
    
    stats = {
        'total_users': 0,
        'already_members': 0,
        'newly_added': 0,
        'failed': 0
    }
    
    try:
        general_chat = get_or_create_general_chat()
        all_users = User.query.filter_by(is_active=True).all()
        
        stats['total_users'] = len(all_users)
        
        for user in all_users:
            if general_chat.is_user_participant(user.id):
                stats['already_members'] += 1
            else:
                try:
                    general_chat.add_participant(user, 'member')
                    stats['newly_added'] += 1
                except Exception:
                    stats['failed'] += 1
        
        db.session.commit()
        logging.info(f"General chat sync complete: {stats}")
        return stats
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to sync users to general chat: {e}")
        raise


def get_chat_stats():
    """Get statistics about chats."""
    general_chat = get_or_create_general_chat()
    team_chats = ChatConversation.query.filter_by(
        conversation_type='team',
        is_active=True
    ).all()
    
    return {
        'general_chat': {
            'id': general_chat.id,
            'member_count': len(general_chat.participants),
            'message_count': general_chat.messages.count()
        },
        'team_chats': {
            'total_count': len(team_chats),
            'chats': [{
                'id': tc.id,
                'name': tc.name,
                'founder_id': tc.created_by_id,
                'member_count': len(tc.participants),
                'message_count': tc.messages.count()
            } for tc in team_chats]
        }
    }


# ============================================
# STARTUP GROUP CHAT HELPERS  (private)
# These are NOT exported — only called from the hooks above.
# Uses ChatConversation.add_to_startup_chat / remove_from_startup_chat
# which handle socket emission (conversation_added / conversation_removed /
# conversation_updated) so the frontend updates with no refresh needed.
# ============================================

def _get_startups_by_founder(founder_id):
    """
    Return all Startup objects owned by this founder.
    Tries ORM first, falls back to raw SQL so this works even if the
    Startup model import path varies across environments.
    """
    try:
        from app.models.startup import Startup
        return Startup.query.filter_by(created_by_id=int(founder_id)).all()
    except Exception:
        pass

    try:
        rows = db.session.execute(
            db.text("SELECT id, name FROM startups WHERE created_by_id = :fid"),
            {'fid': int(founder_id)}
        ).fetchall()

        class _S:
            def __init__(self, sid, name):
                self.id = sid
                self.name = name

        return [_S(r[0], r[1]) for r in rows]
    except Exception as e:
        logging.warning(f"[_get_startups_by_founder] fallback failed: {e}")
        return []


def _sync_founder_startup_chats(founder, match_name=None):
    """
    Create/sync startup group chats for all startups owned by `founder`.
    When match_name is provided (startup.name passed as team_name), only
    that specific startup is synced — used on first creation so we don't
    accidentally touch unrelated startups.
    Called from on_founder_created.
    """
    try:
        startups = _get_startups_by_founder(founder.id)
        for startup in startups:
            # If the caller passed the startup name, only sync the matching one
            if match_name and startup.name and startup.name != match_name:
                continue
            ChatConversation.add_to_startup_chat(user=founder, startup=startup)
            logging.info(
                f"[_sync_founder_startup_chats] founder={founder.id} startup={startup.id}"
            )
    except Exception as e:
        logging.warning(f"[_sync_founder_startup_chats] error: {e}")


def _sync_member_to_startup_chats(founder_id, member):
    """
    Add `member` to every startup group chat owned by `founder_id`.
    Called from on_team_member_added.
    ChatConversation.add_to_startup_chat is idempotent — safe to call if
    the member is already in the chat.
    """
    try:
        startups = _get_startups_by_founder(founder_id)
        for startup in startups:
            ChatConversation.add_to_startup_chat(user=member, startup=startup)
            logging.info(
                f"[_sync_member_to_startup_chats] user={member.id} startup={startup.id}"
            )
    except Exception as e:
        logging.warning(f"[_sync_member_to_startup_chats] error: {e}")


def _remove_member_from_startup_chats(founder_id, member):
    """
    Remove `member` from every startup group chat owned by `founder_id`.
    Called from on_team_member_removed.
    """
    try:
        startups = _get_startups_by_founder(founder_id)
        for startup in startups:
            ChatConversation.remove_from_startup_chat(
                user=member, startup_id=startup.id
            )
            logging.info(
                f"[_remove_member_from_startup_chats] user={member.id} startup={startup.id}"
            )
    except Exception as e:
        logging.warning(f"[_remove_member_from_startup_chats] error: {e}")