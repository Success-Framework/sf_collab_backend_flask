from app.extensions import db
from app.utils.socketio import socketio, get_user_sid
from app.models.chatMessage import ChatMessage
from app.models.chatConversation import ChatConversation
from app.models.user import User
from app.utils.timezone_converter import TimezoneConverter
import json
import logging
from datetime import datetime, timedelta


class RealtimeService:
    """Service for emitting real-time events via WebSocket with timezone support"""
    
    @staticmethod
    def emit_new_message(message_id, skip_sid=None):
        """
        Emit new message to all conversation participants with timezone conversion
        
        Args:
            message_id: ID of the newly created message
            skip_sid: Optional socket ID to skip (e.g., sender's own socket)
        """
        try:
            message = ChatMessage.query.get(message_id)
            if not message:
                print(f'Message {message_id} not found')
                return
            
            conversation = message.conversation
            
            # Get the sender as a User object
            sender = User.query.get(message.sender_id)
            if not sender:
                print(f'Sender {message.sender_id} not found')
                return
            
            # Get message in sender's timezone (for sender's own display)
            sender_message_data = message.to_dict(for_user=sender)
            
            # Send to each participant with their timezone conversion
            for participant in conversation.participants:
                if participant.id == sender.id:
                    # For sender, use the sender version
                    participant_message_data = sender_message_data
                else:
                    # For receivers, convert time to their timezone
                    participant_message_data = message.to_dict(for_user=participant)
                
                # Get participant's socket ID
                participant_sid = get_user_sid(participant.id)
                
                if participant_sid:
                    socketio.emit('new_message', {
                        'conversation_id': conversation.id,
                        'message': participant_message_data,
                        'is_own_message': participant.id == sender.id
                    }, room=participant_sid)
            
            # Also broadcast to conversation room for any listening clients
            socketio.emit('conversation_updated', {
                'conversation_id': conversation.id,
                'last_message': sender_message_data,
                'updated_at': conversation.updated_at.isoformat()
            }, room=f'conversation_{conversation.id}', skip_sid=skip_sid)
            
            print(f'Emitted new_message event for message {message_id}')
            
        except Exception as e:
            print(f'Error emitting new_message event: {str(e)}')
            
            
    @staticmethod
    def emit_message_edited(message_id):
        """
        Emit message edit to all conversation participants with timezone conversion
        
        Args:
            message_id: ID of the edited message
        """
        try:
            message = ChatMessage.query.get(message_id)
            if not message:
                print(f'Message {message_id} not found')
                return
            
            conversation = message.conversation
            
            # Send to each participant with their timezone conversion
            for participant in conversation.participants:
                participant_message_data = message.to_dict(for_user=participant)
                
                from app.utils.socketio import get_user_sid
                participant_sid = get_user_sid(participant.id)
                
                if participant_sid:
                    socketio.emit('message_edited', {
                        'conversation_id': conversation.id,
                        'message': participant_message_data
                    }, room=participant_sid)
            
            print(f'Emitted message_edited event for message {message_id}')
            
        except Exception as e:
            print(f'Error emitting message_edited event: {str(e)}')
    
    @staticmethod
    def emit_message_deleted(message_id, conversation_id):
        """
        Emit message deleted event to all participants
        
        Args:
            message_id: ID of the deleted message
            conversation_id: ID of the conversation
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                print(f'Conversation {conversation_id} not found')
                return
            
            # Send to each participant
            for participant in conversation.participants:
                from app.utils.socketio import get_user_sid
                participant_sid = get_user_sid(participant.id)
                
                if participant_sid:
                    socketio.emit('message_deleted', {
                        'conversation_id': conversation_id,
                        'message_id': message_id
                    }, room=participant_sid)
            
            print(f'Emitted message_deleted event for message {message_id}')
            
        except Exception as e:
            print(f'Error emitting message_deleted event: {str(e)}')
    
    @staticmethod
    def emit_conversation_created(conversation_id, creator_id):
        """
        Emit new conversation to all participants with timezone conversion
        
        Args:
            conversation_id: ID of the newly created conversation
            creator_id: ID of the user who created the conversation
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                print(f'Conversation {conversation_id} not found')
                return
            
            creator = User.query.get(creator_id)
            if not creator:
                print(f'Creator {creator_id} not found')
                return
            
            # Send to each participant with their timezone conversion
            for participant in conversation.participants:
                participant_conversation_data = conversation.to_dict(for_user=participant)
                
                from app.utils.socketio import get_user_sid
                participant_sid = get_user_sid(participant.id)
                
                if participant_sid:
                    # Emit the 'conversation_created' event with the following payload:
                    # - 'conversation': A dictionary containing conversation details tailored for the participant
                    socketio.emit('conversation_created', {
                        'conversation': participant_conversation_data
                    }, room=participant_sid)
            
            print(f'Emitted conversation_created event for conversation {conversation_id}')
            
        except Exception as e:
            print(f'Error emitting conversation_created event: {str(e)}')
    
    @staticmethod
    def emit_conversation_updated(conversation_id):
        """
        Emit conversation updated event (name change, avatar, etc.)
        
        Args:
            conversation_id: ID of the updated conversation
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                print(f'Conversation {conversation_id} not found')
            # Cache the conversation data for each participant
            participant_data_cache = {
                participant.id: conversation.to_dict(for_user=participant)
                for participant in conversation.participants
            }
            
            for participant in conversation.participants:
                participant_conversation_data = participant_data_cache[participant.id]
                
                from app.utils.socketio import get_user_sid
                participant_sid = get_user_sid(participant.id)
                
                if participant_sid:
                    socketio.emit('conversation_updated', {
                        'conversation': participant_conversation_data
                    }, room=participant_sid)
                    socketio.emit('conversation_updated', {
                        'conversation': participant_conversation_data
                    }, room=participant_sid)
            
            print(f'Emitted conversation_updated event for conversation {conversation_id}')
            
        except Exception as e:
            print(f'Error emitting conversation_updated event: {str(e)}')
    
    @staticmethod
    def emit_user_typing(conversation_id, user_id, is_typing=True):
        """
        Emit typing indicators to conversation participants
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user typing
            is_typing: Boolean indicating if user is typing (default: True)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                print(f'User {user_id} not found')
                return
            
            typing_data = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'user_name': f"{user.first_name} {user.last_name}",
                'is_typing': is_typing
            }
            
            # Send to all participants except the typing user
            conversation = ChatConversation.query.get(conversation_id)
            if conversation:
                for participant in conversation.participants:
                    if participant.id != user_id:
                        from app.utils.socketio import get_user_sid
                        participant_sid = get_user_sid(participant.id)
                        
                        if participant_sid:
                            socketio.emit('user_typing', typing_data, room=participant_sid)
                
                print(f'User {user_id} typing status: {is_typing} in conversation {conversation_id}')
            
        except Exception as e:
            print(f'Error emitting user_typing event: {str(e)}')
    
    @staticmethod
    def emit_message_read(conversation_id, user_id, message_id):
        """
        Emit message read receipts to conversation participants
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user who read the message
            message_id: ID of the message that was read
        """
        try:
            read_data = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'message_id': message_id,
                'read_at': datetime.utcnow().isoformat()
            }
            
            # Send to all participants except the reader
            conversation = ChatConversation.query.get(conversation_id)
            if conversation:
                for participant in conversation.participants:
                    if participant.id != user_id:
                        from app.utils.socketio import get_user_sid
                        participant_sid = get_user_sid(participant.id)
                        
                        if participant_sid:
                            socketio.emit('message_read', read_data, room=participant_sid)
                
                print(f'User {user_id} read message {message_id}')
            
        except Exception as e:
            print(f'Error emitting message_read event: {str(e)}')
    
    @staticmethod
    def emit_participant_added(conversation_id, user_id, added_by_id):
        """
        Emit participant added event
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user added
            added_by_id: ID of the user who added them
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)
            user = User.query.get(user_id)
            added_by = User.query.get(added_by_id)
            
            if not conversation or not user or not added_by:
                print('Conversation, user, or added_by not found')
                return
            
            # Send to all participants in the conversation
            for participant in conversation.participants:
                from app.utils.socketio import get_user_sid
                participant_sid = get_user_sid(participant.id)
                
                if participant_sid:
                    socketio.emit('participant_added', {
                        'conversation_id': conversation_id,
                        'user_id': user_id,
                        'user_name': f"{user.first_name} {user.last_name}",
                        'added_by_id': added_by_id,
                        'added_by_name': f"{added_by.first_name} {added_by.last_name}"
                    }, room=participant_sid)
            
            # Also notify the newly added user with full conversation details
            from app.utils.socketio import get_user_sid
            user_sid = get_user_sid(user_id)
            if user_sid:
                socketio.emit('added_to_conversation', {
                    'conversation': conversation.to_dict(for_user=user),
                    'added_by_id': added_by_id,
                    'added_by_name': f"{added_by.first_name} {added_by.last_name}"
                }, room=user_sid)
            
            print(f'User {user_id} added to conversation {conversation_id}')
            
        except Exception as e:
            print(f'Error emitting participant_added event: {str(e)}')
    
    @staticmethod
    def emit_participant_removed(conversation_id, user_id, removed_by_id):
        """
        Emit participant removed event
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user removed
            removed_by_id: ID of the user who removed them
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)
            user = User.query.get(user_id)
            removed_by = User.query.get(removed_by_id)
            
            if not conversation or not user or not removed_by:
                print('Conversation, user, or removed_by not found')
                return
            
            # Send to all remaining participants
            for participant in conversation.participants:
                from app.utils.socketio import get_user_sid
                participant_sid = get_user_sid(participant.id)
                
                if participant_sid:
                    socketio.emit('participant_removed', {
                        'conversation_id': conversation_id,
                        'user_id': user_id,
                        'user_name': f"{user.first_name} {user.last_name}",
                        'removed_by_id': removed_by_id,
                        'removed_by_name': f"{removed_by.first_name} {removed_by.last_name}"
                    }, room=participant_sid)
            
            # Notify the removed user
            from app.utils.socketio import get_user_sid
            user_sid = get_user_sid(user_id)
            if user_sid:
                socketio.emit('removed_from_conversation', {
                    'conversation_id': conversation_id,
                    'removed_by_id': removed_by_id,
                    'removed_by_name': f"{removed_by.first_name} {removed_by.last_name}"
                }, room=user_sid)
            
            print(f'User {user_id} removed from conversation {conversation_id}')
            
        except Exception as e:
            print(f'Error emitting participant_removed event: {str(e)}')
    
    @staticmethod
    def emit_user_status_change(user_id, status):
        """
        Emit user status change (online/offline/away/busy)
        
        Args:
            user_id: ID of the user
            status: New status (online/offline/away/busy)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                print(f'User {user_id} not found')
                return
            
            # Broadcast to all connected users
            socketio.emit('user_status_changed', {
                'user_id': user_id,
                'user_name': f"{user.first_name} {user.last_name}",
                'status': status
            }, broadcast=True)
            
            print(f'User {user_id} status changed to {status}')
            
        except Exception as e:
            print(f'Error emitting user_status_change event: {str(e)}')
            
    #! new handlers:
    #? Emit whiteboard drawing/image data to conversation participants
    @staticmethod
    def emit_whiteboard_image(conversation_id, image_data, sender_user_id):
        """
        Emit whiteboard drawing/image data to conversation participants
        
        Args:
            conversation_id: ID of the conversation (used as whiteboard room)
            image_data: Base64 image data or drawing coordinates
            sender_user_id: ID of the user who sent the drawing
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                logging.error(f'Conversation {conversation_id} not found')
                return
            
            sender = User.query.get(sender_user_id)
            if not sender:
                logging.error(f'Sender {sender_user_id} not found')
                return
            
            image_payload = {
                'conversation_id': conversation_id,
                'image_data': image_data,
                'sender_id': sender_user_id,
                'sender_name': f"{sender.first_name} {sender.last_name}",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to all participants in the conversation/whiteboard room
            for participant in conversation.participants:
                if participant.id != sender_user_id:  # Skip sender
                    participant_sid = get_user_sid(participant.id)
                    if participant_sid:
                        socketio.emit('whiteboard_image', image_payload, room=participant_sid)
            
            # Also emit to the conversation's whiteboard room for any listening clients
            socketio.emit('whiteboard_image', image_payload, room=f'whiteboard_{conversation_id}')
            
            logging.info(f'Emitted whiteboard image for conversation {conversation_id} from user {sender_user_id}')
            
        except Exception as e:
            logging.error(f'Error emitting whiteboard image: {str(e)}')
            logging.exception(e)
    
    #? Emit whiteboard clear event to conversation participants
    @staticmethod
    def emit_whiteboard_clear(conversation_id, cleared_by_user_id):
        """
        Emit whiteboard clear event to conversation participants
        
        Args:
            conversation_id: ID of the conversation (whiteboard room)
            cleared_by_user_id: ID of the user who cleared the whiteboard
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                logging.error(f'Conversation {conversation_id} not found')
                return
            
            clearer = User.query.get(cleared_by_user_id)
            if not clearer:
                logging.error(f'User {cleared_by_user_id} not found')
                return
            
            clear_payload = {
                'conversation_id': conversation_id,
                'cleared_by_id': cleared_by_user_id,
                'cleared_by_name': f"{clearer.first_name} {clearer.last_name}",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to all participants
            for participant in conversation.participants:
                participant_sid = get_user_sid(participant.id)
                if participant_sid:
                    socketio.emit('whiteboard_cleared', clear_payload, room=participant_sid)
            
            # Also emit to the whiteboard room
            socketio.emit('whiteboard_cleared', clear_payload, room=f'whiteboard_{conversation_id}')
            
            logging.info(f'Emitted whiteboard clear for conversation {conversation_id} by user {cleared_by_user_id}')
            
        except Exception as e:
            logging.error(f'Error emitting whiteboard clear: {str(e)}')
            logging.exception(e)
    
    #? Emit whiteboard undo action to conversation participants
    @staticmethod
    def emit_whiteboard_undo(conversation_id, undone_by_user_id):
        """
        Emit whiteboard undo action to conversation participants
        
        Args:
            conversation_id: ID of the conversation (whiteboard room)
            undone_by_user_id: ID of the user who performed undo
        """
        try:
            undo_payload = {
                'conversation_id': conversation_id,
                'undone_by_id': undone_by_user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Emit to the whiteboard room only
            socketio.emit('whiteboard_undo', undo_payload, room=f'whiteboard_{conversation_id}')
            
            logging.info(f'Emitted whiteboard undo for conversation {conversation_id} by user {undone_by_user_id}')
            
        except Exception as e:
            logging.error(f'Error emitting whiteboard undo: {str(e)}')
            logging.exception(e)
    
    #? Emit whiteboard redo action to conversation participants
    @staticmethod
    def emit_whiteboard_redo(conversation_id, redone_by_user_id):
        """
        Emit whiteboard redo action to conversation participants
        
        Args:
            conversation_id: ID of the conversation (whiteboard room)
            redone_by_user_id: ID of the user who performed redo
        """
        try:
            redo_payload = {
                'conversation_id': conversation_id,
                'redone_by_id': redone_by_user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Emit to the whiteboard room only
            socketio.emit('whiteboard_redo', redo_payload, room=f'whiteboard_{conversation_id}')
            
            logging.info(f'Emitted whiteboard redo for conversation {conversation_id} by user {redone_by_user_id}')
            
        except Exception as e:
            logging.error(f'Error emitting whiteboard redo: {str(e)}')
            logging.exception(e)
    
    #? Emit when a user joins a whiteboard session
    @staticmethod
    def emit_user_joined_whiteboard(conversation_id, user_id):
        """
        Emit when a user joins a whiteboard session
        
        Args:
            conversation_id: ID of the conversation (whiteboard room)
            user_id: ID of the user who joined
        """
        try:
            user = User.query.get(user_id)
            if not user:
                logging.error(f'User {user_id} not found')
                return
            
            join_payload = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'user_name': f"{user.first_name} {user.last_name}",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Emit to all other participants in the whiteboard room
            socketio.emit('user_joined_whiteboard', join_payload, 
                         room=f'whiteboard_{conversation_id}', 
                         skip_sid=get_user_sid(user_id))
            
            logging.info(f'Emitted user joined whiteboard for conversation {conversation_id}, user {user_id}')
            
        except Exception as e:
            logging.error(f'Error emitting user joined whiteboard: {str(e)}')
            logging.exception(e)
    
    #? Emit when a user leaves a whiteboard session
    @staticmethod
    def emit_user_left_whiteboard(conversation_id, user_id):
        """
        Emit when a user leaves a whiteboard session
        
        Args:
            conversation_id: ID of the conversation (whiteboard room)
            user_id: ID of the user who left
        """
        try:
            user = User.query.get(user_id)
            if not user:
                logging.error(f'User {user_id} not found')
                return
            
            leave_payload = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'user_name': f"{user.first_name} {user.last_name}",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Emit to all participants in the whiteboard room
            socketio.emit('user_left_whiteboard', leave_payload, 
                         room=f'whiteboard_{conversation_id}')
            
            logging.info(f'Emitted user left whiteboard for conversation {conversation_id}, user {user_id}')
            
        except Exception as e:
            logging.error(f'Error emitting user left whiteboard: {str(e)}')
            logging.exception(e)
    
    #? Emit list of active users in a whiteboard session
    @staticmethod
    def emit_active_whiteboard_users(conversation_id, user_ids):
        """
        Send list of active users in a whiteboard session
        
        Args:
            conversation_id: ID of the conversation (whiteboard room)
            user_ids: List of user IDs currently in the whiteboard
        """
        try:
            users = User.query.filter(User.id.in_(user_ids)).all()
            
            active_users_payload = {
                'conversation_id': conversation_id,
                'active_users': [
                    {
                        'id': user.id,
                        'name': f"{user.first_name} {user.last_name}",
                        'profile_picture': user.profile_picture
                    }
                    for user in users
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Emit to the whiteboard room
            socketio.emit('active_whiteboard_users', active_users_payload, 
                         room=f'whiteboard_{conversation_id}')
            
            logging.info(f'Emitted active whiteboard users for conversation {conversation_id}')
            
        except Exception as e:
            logging.error(f'Error emitting active whiteboard users: {str(e)}')
            logging.exception(e)
            

    # In realtime_service.py, add this method:
    #? Emit user cursor movement to whiteboard
    @staticmethod
    def emit_user_cursor_move(conversation_id, user_id, x, y, color=None, user_name=None):
        """Emit user cursor movement to whiteboard"""
        try:
            room_name = f'whiteboard_{conversation_id}'
            socketio.emit('user_cursor_moved', {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'user_name': user_name or f'User {user_id}',
                'x': x,
                'y': y,
                'color': color or '#3B82F6',
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_name)
        except Exception as e:
            logging.error(f'Error emitting cursor move: {str(e)}')