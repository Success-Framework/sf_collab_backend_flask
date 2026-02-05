from flask import Blueprint, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.models.chatConversation import ChatConversation, conversation_participants
from app.models.chatMessage import ChatMessage
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response
from app.utils.timezone_converter import get_user_timezone

import logging
import re
import os
import json
from datetime import datetime

from app.utils.chat_utils import (
    get_or_create_general_chat,
    add_user_to_general_chat,
    on_user_profile_created,
    on_founder_created,
    on_team_member_added,
    on_team_member_removed
)
from app.notifications.helpers import (
    notify_new_message,
    notify_group_message,
    notify_mention_in_chat,
    notify_message_request,
    notify_voice_message_received
)

# Import socket events for real-time updates
try:
    from app.socket_events import (
        emit_new_message,
        emit_message_edited,
        emit_message_deleted,
        emit_conversation_update,
        emit_to_user,
        emit_notification,
    )
    SOCKET_ENABLED = True
except ImportError:
    SOCKET_ENABLED = False
    logging.warning("Socket events not available - real-time updates disabled")


chat_bp = Blueprint("chat", __name__)

# Upload configurations
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "chat_files")
AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "chat_avatars")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "txt"}
ALLOWED_AVATAR_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_avatar(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS


def validate_file_size(file, max_size=MAX_FILE_SIZE) -> bool:
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= max_size

def get_user_full_name(user_id):
    """Helper to get user's full name"""
    from app.models.user import User
    user = User.query.get(user_id)
    if user:
        return f"{user.first_name or ''} {user.last_name or ''}".strip() or "Someone"
    return "Someone"


def extract_mentions(content):
    """Extract @mentions from message content"""
    import re
    # Match @username patterns
    mentions = re.findall(r'@(\w+)', content)
    return mentions


def get_user_by_username(username):
    """Get user by username for mentions"""
    from app.models.user import User
    return User.query.filter_by(username=username).first()



# ─────────────────────────────────────────────────────────────
# GET CONVERSATIONS
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations", methods=["GET"], strict_slashes=False)
@jwt_required()
def get_conversations():
    try:
        current_user_id = get_jwt_identity()

        user = User.query.get(current_user_id)
        if not user:
            return error_response("User not found", 404)

        conversations = (
            ChatConversation.query.join(conversation_participants)
            .filter(conversation_participants.c.user_id == current_user_id)
            .order_by(ChatConversation.updated_at.desc())
            .all()
        )

        conversations_data = []
        for conv in conversations:
            try:
                conversations_data.append(conv.to_dict(for_user=user))
            except Exception as e:
                logging.error(f"Error converting conversation {conv.id}: {str(e)}")
                continue

        return success_response({"conversations": conversations_data})

    except Exception as e:
        logging.error(f"Error in get_conversations: {str(e)}")
        return error_response(f"Failed to load conversations: {str(e)}", 500)

@chat_bp.route("/conversations", methods=["POST"], strict_slashes=False)
@jwt_required()
def create_conversation():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        # accept either participant_ids or participantIds (frontend sometimes differs)
        participant_ids = data.get("participant_ids") or data.get("participantIds")
        if not participant_ids or not isinstance(participant_ids, list):
            return error_response("Missing required field: participant_ids (must be a list)", 400)

        creator = User.query.get(current_user_id)
        if not creator:
            return error_response("Creator not found", 404)

        conversation = ChatConversation(
            name=data.get("name"),
            conversation_type=data.get("conversation_type", "group"),  # group chat
            created_by_id=creator.id,
            description=data.get("description"),
            avatar_url=data.get("avatar_url"),
        )

        db.session.add(conversation)
        db.session.flush()

        # creator is admin
        conversation.add_participant(creator, "admin")

        # add other participants
        participants = User.query.filter(User.id.in_(participant_ids)).all()
        for user in participants:
            if user.id != creator.id:
                conversation.add_participant(user, "member")

        db.session.commit()

        return success_response(
            {"conversation": conversation.to_dict(for_user=creator)},
            "Conversation created successfully",
            201,
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create conversation: {str(e)}", 500)


@chat_bp.route("/conversations/<int:conversation_id>", methods=["GET"])
@jwt_required()
def get_conversation(conversation_id):
    try:
        current_user_id = get_jwt_identity()

        user = User.query.get(current_user_id)
        conversation = ChatConversation.query.get(conversation_id)

        if not user or not conversation:
            return error_response("User or conversation not found", 404)

        if not conversation.is_user_participant(current_user_id):
            return error_response("Access denied", 403)

        return success_response({"conversation": conversation.to_dict(for_user=user)})

    except Exception as e:
        logging.error(f"Error getting conversation {conversation_id}: {str(e)}")
        return error_response(f"Failed to load conversation: {str(e)}", 500)


@chat_bp.route("/conversations/with-user/<int:other_user_id>", methods=["GET"])
@jwt_required()
def get_or_create_direct_conversation(other_user_id):
    try:
        current_user_id = get_jwt_identity()

        if current_user_id == other_user_id:
            return error_response("You cannot create a conversation with yourself", 400)

        current_user = User.query.get(current_user_id)
        other_user = User.query.get(other_user_id)

        if not current_user or not other_user:
            return error_response("User not found", 404)

        conversation = (
            ChatConversation.query.join(conversation_participants)
            .filter(ChatConversation.conversation_type == "direct")
            .filter(conversation_participants.c.user_id.in_([current_user_id, other_user_id]))
            .group_by(ChatConversation.id)
            .having(db.func.count(ChatConversation.id) == 2)
            .first()
        )

        if conversation:
            return success_response(
                {"conversation": conversation.to_dict(for_user=current_user), "created": False}
            )

        conversation = ChatConversation(conversation_type="direct", created_by_id=current_user_id)
        db.session.add(conversation)
        db.session.flush()

        conversation.add_participant(current_user, "member")
        conversation.add_participant(other_user, "member")

        db.session.commit()

        return success_response(
            {"conversation": conversation.to_dict(for_user=current_user), "created": True},
            "Conversation created",
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to get/create conversation: {str(e)}")
        return error_response(f"Failed to get or create conversation: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# GENERAL CHAT
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/general", methods=["GET"])
@jwt_required()
def get_general_chat():
    try:
        from app.utils.general_chat import get_or_create_general_chat as _get_general

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return error_response("User not found", 404)

        general_chat = _get_general()
        if not general_chat:
            return error_response("General chat not available", 404)

        return success_response({"conversation": general_chat.to_dict(for_user=user)})

    except Exception as e:
        logging.error(f"Error getting general chat: {str(e)}")
        return error_response(f"Failed to get general chat: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# MARK CONVERSATION AS READ
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>/mark-read", methods=["POST"])
@jwt_required()
def mark_conversation_read(conversation_id):
    try:
        current_user_id = get_jwt_identity()

        user = User.query.get(current_user_id)
        conversation = ChatConversation.query.get(conversation_id)

        if not user or not conversation:
            return error_response("User or conversation not found", 404)

        if not conversation.is_user_participant(current_user_id):
            return error_response("Access denied", 403)

        conversation.mark_as_read(current_user_id)

        return success_response({"message": "Conversation marked as read"})

    except Exception as e:
        logging.error(f"Error marking conversation as read: {str(e)}")
        return error_response(f"Failed to mark conversation as read: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# GET MESSAGES
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
@jwt_required()
def get_messages(conversation_id):
    try:
        current_user_id = get_jwt_identity()
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        user = User.query.get(current_user_id)
        conversation = ChatConversation.query.get(conversation_id)

        if not user or not conversation:
            return error_response("User or conversation not found", 404)

        if not conversation.is_user_participant(current_user_id):
            return error_response("Access denied", 403)

        messages = conversation.get_messages_for_user(user, limit, offset)

        return success_response(
            {"conversation": conversation.to_dict(for_user=user), "messages": messages}
        )

    except Exception as e:
        logging.error(f"Error in get_messages: {str(e)}")
        return error_response(f"Failed to load messages: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# SEND MESSAGE (conversation_id)
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>/messages", methods=["POST"])
@jwt_required()
def send_message(conversation_id):
    current_user_id = get_jwt_identity()
    is_file_upload = "file" in request.files

    if is_file_upload:
        file = request.files.get("file")
        if not file:
            return error_response("No file provided", 400)

        if file.filename == "":
            return error_response("No file selected", 400)

        if not allowed_file(file.filename):
            return error_response(
                f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', 400
            )

        if not validate_file_size(file):
            return error_response(
                f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024*1024)}MB", 400
            )

        content = request.form.get("content", "Sent a file")
        message_type = request.form.get("message_type", "file")
        reply_to_id = request.form.get("reply_to_id", type=int)
        data = None
    else:
        data = request.get_json() or {}
        content = data.get("content")
        message_type = data.get("message_type", "text")
        reply_to_id = data.get("reply_to_id")
        file = None

    if not content:
        return error_response("Missing required field: content", 400)

    user = User.query.get(current_user_id)
    conversation = ChatConversation.query.get(conversation_id)

    if not user or not conversation:
        return error_response("User or conversation not found", 404)

    if not conversation.is_user_participant(user.id):
        return error_response("Access denied", 403)

    try:
        sender_timezone = get_user_timezone(user)
        original_content = content
        metadata_data = {} if is_file_upload else (data.get("metadata_data", {}) if data else {})

        time_pattern = r"\[(\d{1,2}:\d{2})\]"
        has_existing_placeholders = bool(re.search(time_pattern, original_content))
        if has_existing_placeholders:
            metadata_data["has_time_placeholders"] = True
            metadata_data["sender_timezone"] = sender_timezone
            metadata_data["sent_at_utc"] = datetime.utcnow().isoformat()

        file_url = None
        file_name = None
        file_size = None
        file_type = None

        if file:
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{current_user_id}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

            file.save(file_path)

            file_name = filename
            file_size = os.path.getsize(file_path)
            file_type = file.content_type
            file_url = f"/api/chat/uploads/{unique_filename}"

            metadata_data["file_info"] = {
                "original_name": file_name,
                "size": file_size,
                "type": file_type,
                "uploaded_at": datetime.utcnow().isoformat(),
            }

        message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=user.id,
            original_content=original_content,
            message_type=message_type,
            metadata_data=metadata_data,
            reply_to_id=reply_to_id,
            sender_timezone=sender_timezone,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
        )

        db.session.add(message)
        conversation.updated_at = datetime.utcnow()

        # ✅ FIX: was user_id (undefined)
        conversation.increment_unread_count(current_user_id)

        db.session.commit()

        # Emit new message realtime
        if SOCKET_ENABLED:
            emit_new_message(conversation_id, message.to_dict(for_user=user))

        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: New Message (4.6) - Using Helpers
        # ════════════════════════════════════════════════════════════
        try:
            sender_name = get_user_full_name(current_user_id)
            
            # Notify all participants except sender
            for participant in conversation.participants:
                if participant.id != current_user_id:
                    # Use appropriate notification based on conversation type
                    if conversation.conversation_type == 'group':
                        notify_group_message(
                            user_id=participant.id,
                            sender_id=current_user_id,
                            sender_name=sender_name,
                            group_name=conversation.name or "Group Chat",
                            message_id=message.id
                        )
                    elif message_type == 'voice':
                        notify_voice_message_received(
                            user_id=participant.id,
                            sender_id=current_user_id,
                            sender_name=sender_name,
                            message_id=message.id
                        )
                    else:
                        notify_new_message(
                            user_id=participant.id,
                            sender_id=current_user_id,
                            sender_name=sender_name,
                            message_id=message.id,
                            conversation_id=conversation.id
                        )
            
            # Handle @mentions in message content
            mentions = extract_mentions(original_content)
            for username in mentions:
                mentioned_user = get_user_by_username(username)
                if mentioned_user and mentioned_user.id != current_user_id:
                    # Check if mentioned user is part of the conversation
                    if mentioned_user in conversation.participants:
                        notify_mention_in_chat(
                            user_id=mentioned_user.id,
                            mentioner_id=current_user_id,
                            mentioner_name=sender_name,
                            chat_name=conversation.name or "Direct Message",
                            message_id=message.id
                        )
                        
        except Exception as e:
            print(f"⚠️ Message notification failed: {e}")

        # ✅ FIX: always return a response
        return success_response(
            {
                "message": message.to_dict(for_user=user),
                "conversation": conversation.to_dict(for_user=user),
            },
            "Message sent",
            201,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to send message: {str(e)}")
        return error_response(f"Failed to send message: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# SEND DIRECT MESSAGE (and Message Request on first contact)
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/direct", methods=["POST"])
@jwt_required()
def send_direct_message():
    """
    Send a message to a user.
    If a direct conversation does not exist, create it automatically.
    Also send a "Message Request" notification on first contact.
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        recipient_id = data.get("recipient_user_id")
        content = data.get("content")

        if not recipient_id or not content:
            return error_response("recipient_user_id and content are required", 400)

        if recipient_id == current_user_id:
            return error_response("You cannot message yourself", 400)

        sender = User.query.get(current_user_id)
        recipient = User.query.get(recipient_id)

        if not sender or not recipient:
            return error_response("User not found", 404)

        conversation = (
            ChatConversation.query.join(conversation_participants)
            .filter(ChatConversation.conversation_type == "direct")
            .filter(conversation_participants.c.user_id.in_([current_user_id, recipient_id]))
            .group_by(ChatConversation.id)
            .having(db.func.count(ChatConversation.id) == 2)
            .first()
        )

        is_new_conversation = False

        if not conversation:
            is_new_conversation = True
            conversation = ChatConversation(conversation_type="direct", created_by_id=current_user_id)
            db.session.add(conversation)
            db.session.flush()

            conversation.add_participant(sender, "member")
            conversation.add_participant(recipient, "member")

        message = ChatMessage(
            conversation_id=conversation.id,
            sender_id=current_user_id,
            original_content=content,
            message_type="text",
            sender_timezone=get_user_timezone(sender),
        )

        db.session.add(message)
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Direct Message (4.6)
        # ════════════════════════════════════════════════════════════
        try:
            sender_name = get_user_full_name(current_user_id)
            notify_new_message(
                user_id=recipient_id,
                sender_id=current_user_id,
                sender_name=sender_name,
                message_id=message.id,
                conversation_id=conversation.id
            )
        except Exception as e:
            print(f"⚠️ Direct message notification failed: {e}")
        
        conversation.updated_at = datetime.utcnow()
        conversation.increment_unread_count(current_user_id)
        db.session.commit()

        if SOCKET_ENABLED:
            emit_new_message(conversation.id, message.to_dict(for_user=sender))

        # ─────────────────────────────────────────────────────────
        # ✨ NOTIFICATION: Message Request (first contact only)
        # ─────────────────────────────────────────────────────────
        if is_new_conversation:
            try:
                from app.models.notification import Notification

                notification = Notification(
                    user_id=recipient_id,
                    notification_type="info",
                    title="📩 New message request",
                    message=f"{sender.first_name} {sender.last_name} wants to message you",
                    data={
                        "requester_id": current_user_id,
                        "message_preview": content[:100] if content else "",
                        "entity_type": "message_request",
                        "entity_id": conversation.id,
                    },
                )
                db.session.add(notification)
                db.session.commit()

                if SOCKET_ENABLED:
                    emit_notification(recipient_id, notification.to_dict())

            except Exception as e:
                logging.warning(f"⚠️ Message request notification failed: {e}")
                db.session.rollback()

        return success_response(
            {
                "conversation": conversation.to_dict(for_user=sender),
                "message": message.to_dict(for_user=sender),
                "conversation_created": is_new_conversation,
            },
            "Message sent",
            201,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to send direct message: {str(e)}")
        return error_response(f"Failed to send message: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# EDIT MESSAGE
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>/messages/<int:message_id>", methods=["PUT"])
@jwt_required()
def edit_message(conversation_id, message_id):
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}

    if not data.get("content"):
        return error_response("Content is required", 400)

    try:
        message = ChatMessage.query.get(message_id)
        if not message:
            return error_response("Message not found", 404)

        if message.conversation_id != conversation_id:
            return error_response("Message does not belong to this conversation", 400)

        if message.sender_id != current_user_id:
            return error_response("You can only edit your own messages", 403)

        new_content = data.get("content")
        metadata_data = data.get("metadata_data", message.metadata_data or {})

        time_pattern = r"\[(\d{1,2}:\d{2})\]"
        has_existing_placeholders = bool(re.search(time_pattern, new_content))
        if has_existing_placeholders:
            metadata_data["has_time_placeholders"] = True
            metadata_data["edited_with_time_placeholders"] = True

        message.edit_message(new_content, metadata_data)

        user = User.query.get(current_user_id)
        response_data = message.to_dict(for_user=user)

        if SOCKET_ENABLED:
            emit_message_edited(conversation_id, response_data)

        return success_response({"message": response_data}, "Message edited successfully")

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to edit message: {str(e)}")
        return error_response(f"Failed to edit message: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# REACT TO MESSAGE (toggle reaction)
# ─────────────────────────────────────────────────────────────
@chat_bp.route(
    "/conversations/<int:conversation_id>/messages/<int:message_id>/reactions",
    methods=["POST"],
)
@jwt_required()
def react_to_message(conversation_id, message_id):
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    reaction_emoji = data.get("emoji")

    if not reaction_emoji:
        return error_response("emoji is required", 400)

    try:
        message = ChatMessage.query.get(message_id)
        if not message or message.conversation_id != conversation_id:
            return error_response("Message not found", 404)

        conversation = ChatConversation.query.get(conversation_id)
        if not conversation or not conversation.is_user_participant(current_user_id):
            return error_response("Access denied", 403)

        metadata = message.metadata_data or {}
        reactions = metadata.get("reactions", {})  # {"👍":[1,2], "❤️":[3]}

        users = reactions.get(reaction_emoji, [])
        if current_user_id in users:
            users.remove(current_user_id)
            if users:
                reactions[reaction_emoji] = users
            else:
                reactions.pop(reaction_emoji, None)
        else:
            users.append(current_user_id)
            reactions[reaction_emoji] = users

        metadata["reactions"] = reactions
        message.metadata_data = metadata
        db.session.commit()

        if SOCKET_ENABLED:
            emit_message_edited(conversation_id, message.to_dict())

        # ─────────────────────────────────────────────────────────
        # ✨ NOTIFICATION: Message Reaction
        # ─────────────────────────────────────────────────────────
        try:
            from app.models.notification import Notification

            if message.sender_id != current_user_id:
                reactor = User.query.get(current_user_id)
                if reactor:
                    notification = Notification(
                        user_id=message.sender_id,
                        notification_type="info",
                        title=f"😊 {reactor.first_name} reacted to your message",
                        message=f"Reacted with {reaction_emoji}",
                        data={
                            "message_id": message.id,
                            "conversation_id": message.conversation_id,
                            "reactor_id": current_user_id,
                            "reaction": reaction_emoji,
                            "entity_type": "message",
                            "entity_id": message.id,
                        },
                    )
                    db.session.add(notification)
                    db.session.commit()

                    if SOCKET_ENABLED:
                        emit_notification(message.sender_id, notification.to_dict())

        except Exception as e:
            logging.warning(f"⚠️ Reaction notification failed: {e}")
            db.session.rollback()

        return success_response({"message": message.to_dict()}, "Reaction updated")

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to react to message: {str(e)}")
        return error_response(f"Failed to react to message: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# DELETE MESSAGE
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>/messages/<int:message_id>", methods=["DELETE"])
@jwt_required()
def delete_message(conversation_id, message_id):
    current_user_id = get_jwt_identity()

    try:
        message = ChatMessage.query.get(message_id)
        conversation = ChatConversation.query.get(conversation_id)

        if not message:
            return error_response("Message not found", 404)

        if message.conversation_id != conversation_id:
            return error_response("Message does not belong to this conversation", 400)

        if message.sender_id != current_user_id and conversation.created_by_id != current_user_id:
            return error_response(
                "You can only delete your own messages or you must be the conversation creator", 403
            )

        if message.file_url:
            try:
                file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(message.file_url))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.error(f"Failed to delete file: {str(e)}")

        db.session.delete(message)
        db.session.commit()

        if SOCKET_ENABLED:
            emit_message_deleted(conversation_id, message_id)

        return success_response({"message_id": message_id}, "Message deleted successfully")

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete message: {str(e)}")
        return error_response(f"Failed to delete message: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# SERVE UPLOADED FILE
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/uploads/<path:filename>", methods=["GET"])
def serve_uploaded_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)
    except FileNotFoundError:
        return error_response("File not found", 404)


# ─────────────────────────────────────────────────────────────
# GET CONVERSATION FILES
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>/files", methods=["GET"])
@jwt_required()
def get_conversation_files(conversation_id):
    try:
        current_user_id = get_jwt_identity()

        conversation = ChatConversation.query.get(conversation_id)
        if not conversation:
            return error_response("Conversation not found", 404)

        if not conversation.is_user_participant(current_user_id):
            return error_response("Access denied", 403)

        messages_with_files = (
            ChatMessage.query.filter_by(conversation_id=conversation_id)
            .filter(ChatMessage.file_url.isnot(None))
            .order_by(ChatMessage.created_at.desc())
            .all()
        )

        files = []
        for msg in messages_with_files:
            file_url = msg.file_url
            if file_url and not file_url.startswith("http"):
                file_url = request.host_url.rstrip("/") + file_url

            files.append(
                {
                    "id": msg.id,
                    "file_name": msg.file_name,
                    "file_url": file_url,
                    "file_size": msg.file_size,
                    "file_type": msg.file_type,
                    "uploaded_by": {
                        "id": msg.sender_id,
                        "firstName": msg.message_sender.first_name,
                        "lastName": msg.message_sender.last_name,
                    },
                    "uploaded_at": msg.created_at.isoformat(),
                    "is_image": msg.is_image(),
                    "is_document": msg.is_document(),
                }
            )

        return success_response({"files": files, "total_count": len(files)}, "Files retrieved successfully")

    except Exception as e:
        logging.error(f"Failed to get conversation files: {str(e)}")
        return error_response(f"Failed to get files: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# ADD PARTICIPANT (with notifications)
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>/participants", methods=["POST"])
@jwt_required()
def add_participant(conversation_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        user_id = data.get("user_id")
        role = data.get("role", "member")

        if not user_id:
            return error_response("User ID is required", 400)

        conversation = ChatConversation.query.get(conversation_id)
        if not conversation:
            return error_response("Conversation not found", 404)

        if conversation.created_by_id != current_user_id:
            return error_response("Only conversation creator can add participants", 403)

        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", 404)

        if conversation.is_user_participant(user_id):
            return error_response("User is already a participant", 400)

        conversation.add_participant(user, role)

        creator = User.query.get(current_user_id)
        notif_content = f"👥 {creator.get_full_name()} added {user.get_full_name()} to the conversation"

        notif_message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=current_user_id,
            original_content=notif_content,
            message_type="system",
            metadata_data={"action": "participant_added", "user_id": user_id},
            sender_timezone="UTC",
        )

        db.session.add(notif_message)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()

        if SOCKET_ENABLED:
            emit_new_message(conversation_id, notif_message.to_dict())
            emit_to_user(user_id, "added_to_conversation", {"conversation": conversation.to_dict(for_user=user)})

        # ─────────────────────────────────────────────────────────
        # ✨ NOTIFICATION: Added to Group Chat
        # ─────────────────────────────────────────────────────────
        if user_id != current_user_id:
            try:
                from app.models.notification import Notification

                adder = creator
                notification = Notification(
                    user_id=user_id,  # ✅ FIX: was new_participant_id (undefined)
                    notification_type="info",
                    title="👥 Added to group chat",
                    message=f'{adder.first_name} added you to "{conversation.name or "a group"}"',
                    data={
                        "conversation_id": conversation.id,
                        "added_by": current_user_id,
                        "entity_type": "conversation",
                        "entity_id": conversation.id,
                    },
                )
                db.session.add(notification)
                db.session.commit()

                if SOCKET_ENABLED:
                    emit_notification(user_id, notification.to_dict())  # ✅ FIX: emit to user_id

            except Exception as e:
                logging.warning(f"⚠️ Group add notification failed: {e}")
                db.session.rollback()

        return success_response(
            {"message": "Participant added successfully", "notification": notif_message.to_dict()}
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to add participant: {str(e)}")
        return error_response(f"Failed to add participant: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# REMOVE PARTICIPANT
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>/participants/<int:user_id>", methods=["DELETE"])
@jwt_required()
def remove_participant(conversation_id, user_id):
    try:
        current_user_id = get_jwt_identity()

        conversation = ChatConversation.query.get(conversation_id)
        if not conversation:
            return error_response("Conversation not found", 404)

        if conversation.created_by_id != current_user_id:
            return error_response("Only conversation creator can remove participants", 403)

        if user_id == conversation.created_by_id:
            return error_response("Cannot remove conversation creator", 400)

        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", 404)

        if not conversation.is_user_participant(user_id):
            return error_response("User is not a participant", 400)

        stmt = (
            conversation_participants.update()
            .where(
                (conversation_participants.c.conversation_id == conversation_id)
                & (conversation_participants.c.user_id == user_id)
            )
            .values(left_at=datetime.utcnow())
        )

        db.session.execute(stmt)
        db.session.commit()

        creator = User.query.get(current_user_id)
        notif_content = f"👋 {user.get_full_name()} was removed from the conversation"

        notif_message = ChatMessage(
            conversation_id=conversation_id,
            sender_id=current_user_id,
            original_content=notif_content,
            message_type="system",
            metadata_data={"action": "participant_removed", "user_id": user_id},
            sender_timezone="UTC",
        )

        db.session.add(notif_message)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()

        if SOCKET_ENABLED:
            emit_new_message(conversation_id, notif_message.to_dict())
            emit_to_user(user_id, "removed_from_conversation", {"conversation_id": conversation_id})

        return success_response(
            {"message": "Participant removed successfully", "notification": notif_message.to_dict()}
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to remove participant: {str(e)}")
        return error_response(f"Failed to remove participant: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# DELETE CONVERSATION (soft delete via left_at for current user)
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/conversations/<int:conversation_id>", methods=["DELETE"])
@jwt_required()
def delete_conversation(conversation_id):
    try:
        current_user_id = get_jwt_identity()

        conversation = ChatConversation.query.get(conversation_id)
        if not conversation:
            return error_response("Conversation not found", 404)

        if conversation.created_by_id != current_user_id:
            return error_response("Only conversation creator can delete conversation", 403)

        if conversation.conversation_type == "general":
            return error_response("Cannot delete the general chat", 403)

        if conversation.avatar_url:
            try:
                file_path = os.path.join(AVATAR_UPLOAD_FOLDER, os.path.basename(conversation.avatar_url))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.error(f"Failed to delete avatar: {str(e)}")

        participant_ids = [p.id for p in conversation.participants]

        stmt = (
            conversation_participants.update()
            .where(
                (conversation_participants.c.conversation_id == conversation_id)
                & (conversation_participants.c.user_id == current_user_id)
            )
            .values(left_at=datetime.utcnow())
        )

        db.session.execute(stmt)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()

        if SOCKET_ENABLED:
            for uid in participant_ids:
                emit_to_user(uid, "conversation_deleted", {"conversation_id": conversation_id})

        return success_response({"message": "Conversation deleted successfully"})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete conversation: {str(e)}")
        return error_response(f"Failed to delete conversation: {str(e)}", 500)


# ─────────────────────────────────────────────────────────────
# TESTING: SETUP GENERAL CHAT
# ─────────────────────────────────────────────────────────────
@chat_bp.route("/setup-general-chat", methods=["POST"])
@jwt_required()
def setup_general_chat():
    from app.utils.chat_utils import get_or_create_general_chat as _get_or_create, sync_all_users_to_general_chat

    current_user_id = get_jwt_identity()

    general_chat = _get_or_create(admin_user_id=current_user_id)
    stats = sync_all_users_to_general_chat()

    return success_response(
        {"general_chat_id": general_chat.id, "sync_stats": stats},
        "General chat setup complete!",
    )
