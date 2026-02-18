from datetime import datetime
from app.extensions import db
from sqlalchemy import JSON
from .chatMessage import ChatMessage

class ChatConversation(db.Model):
    __tablename__ = 'chat_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)  # For group chats
    conversation_type = db.Column(db.String(20), default='direct')  # direct, group
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Group chat properties
    description = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Settings
    is_active = db.Column(db.Boolean, default=True)
    settings = db.Column(JSON, default={})  # Notification settings, etc.
    unread_count = db.Column(db.Integer, default=0) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation_creator = db.relationship('User', back_populates='created_conversations', foreign_keys=[created_by_id])
    participants = db.relationship('User', secondary='conversation_participants', back_populates='conversations')
    messages = db.relationship('ChatMessage', back_populates='conversation', lazy='dynamic', cascade='all, delete-orphan')

    # HELPER FUNCTIONS
    
    def add_participant(self, user, role='member'):
        """Add participant to conversation"""
        from sqlalchemy import insert
        
        # Check if user is already a participant
        existing = db.session.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == self.id,
                conversation_participants.c.user_id == user.id
            )
        ).first()
        
        if not existing:
            stmt = conversation_participants.insert().values(
                conversation_id=self.id,
                user_id=user.id,
                role=role
            )
            db.session.execute(stmt)
            db.session.commit()
    
    def remove_participant(self, user):
        """Remove participant from conversation"""
        stmt = conversation_participants.delete().where(
            conversation_participants.c.conversation_id == self.id,
            conversation_participants.c.user_id == user.id
        )
        db.session.execute(stmt)
        db.session.commit()
    
    def get_participant_role(self, user):
        """Get participant role in conversation"""
        result = db.session.execute(
            conversation_participants.select().where(
                conversation_participants.c.conversation_id == self.id,
                conversation_participants.c.user_id == user.id
            )
        ).first()
        
        return result.role if result else None
    
    def get_messages_for_user(self, user, limit=50, offset=0):
        """Get messages for specific user with timezone conversion"""
        messages = self.messages.order_by(ChatMessage.created_at.desc())\
                               .limit(limit)\
                               .offset(offset)\
                               .all()
        
        # Convert messages for user's timezone
        converted_messages = []
        for message in reversed(messages):  # Reverse to get chronological order
            converted_messages.append(message.to_dict(for_user=user))
        
        return converted_messages
    
    def get_last_message_preview(self, for_user=None):
        """Get last message preview with timezone conversion"""
        from app.models.user import User
        
        last_message = self.messages.order_by(ChatMessage.created_at.desc()).first()
        
        # Check if there's a last message
        if not last_message:
            return None
        
        # Get the sender
        user = User.query.get(last_message.sender_id)
        
        # Build preview (even if user not found, show message)
        preview = {
            'content': last_message.get_content_for_user(for_user) if for_user else last_message.prepare_for_sending(),
            'created_at': last_message.created_at.isoformat(),
            'sender_name': user.get_full_name() if user else 'Unknown',
            'display_time': last_message.get_display_time_info(for_user) if for_user else None,
            'is_deleted': last_message.is_deleted
        }
        
        return preview
        
    def add_message(self, sender, content, message_type='text', metadata_data=None, reply_to_id=None):
        """Add new message to conversation with timezone handling"""
        message = ChatMessage(
            conversation_id=self.id,
            sender_id=sender.id,
            original_content=content,
            message_type=message_type,
            metadata_data=metadata_data or {},
            reply_to_id=reply_to_id,
            sender_timezone=sender.get_timezone()
        )
        
        db.session.add(message)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
        return message
    @staticmethod
    def add_to_general_chat(user):
        """Add user to general chat conversation"""
        general_chat = ChatConversation.query.filter_by(conversation_type='general').first()

        if general_chat:
            general_chat.add_participant(user, role='member')
            db.session.commit()
        # if not general_chat create one
        else:
            general_chat = ChatConversation(
                name='General Chat',
                conversation_type='general',
                created_by_id= user.id 
            )
            db.session.add(general_chat)
            db.session.flush()  # Get ID before adding participant
            general_chat.add_participant(user, role='member')
            # You might want to send a welcome message here as well
            welcome_message = ChatMessage(
                conversation_id=general_chat.id,
                sender_id=user.id,
                original_content="Welcome to the General Chat!",
                message_type='text',
                metadata_data={},
                sender_timezone=user.get_timezone()
            )
            db.session.add(welcome_message)
            db.session.commit()
        
    def is_user_participant(self, user_id):
        """Check if user is a participant in this conversation"""
        return any(str(participant.id) == str(user_id) for participant in self.participants)
    
    def get_unread_message_count(self, user_id):
        """Get count of unread messages for specific user"""
        # Get the user's read status for this conversation
        read_status = db.session.execute(
            conversation_user_reads.select().where(
                (conversation_user_reads.c.conversation_id == self.id) &
                (conversation_user_reads.c.user_id == user_id)
            )
        ).first()
        
        if read_status:
            # Return the stored unread count
            return read_status.unread_count
        else:
            # If no read status exists, all messages are unread
            return self.messages.count()
            
    def mark_as_read(self, user_id):
        """Mark all messages as read for user"""
        from sqlalchemy import and_
        
        try:
            # Try to update existing record
            stmt = conversation_user_reads.update().where(
                and_(
                    conversation_user_reads.c.conversation_id == self.id,
                    conversation_user_reads.c.user_id == user_id
                )
            ).values(
                last_read_at=datetime.utcnow(),
                unread_count=0
            )
            
            result = db.session.execute(stmt)
            
            # If no rows were updated, insert new record
            if result.rowcount == 0:
                stmt = conversation_user_reads.insert().values(
                    conversation_id=self.id,
                    user_id=user_id,
                    last_read_at=datetime.utcnow(),
                    unread_count=0
                )
                db.session.execute(stmt)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def increment_unread_count(self, sender_id):
        """Increment unread count for all participants except sender"""
        from sqlalchemy import update, and_
        
        for participant in self.participants:
            if participant.id != sender_id:  # Don't increment for message sender
                # Check if record exists
                existing = db.session.execute(
                    conversation_user_reads.select().where(
                        and_(
                            conversation_user_reads.c.conversation_id == self.id,
                            conversation_user_reads.c.user_id == participant.id
                        )
                    )
                ).first()
                
                if existing:
                    # Update existing record
                    stmt = conversation_user_reads.update().where(
                        and_(
                            conversation_user_reads.c.conversation_id == self.id,
                            conversation_user_reads.c.user_id == participant.id
                        )
                    ).values(
                        unread_count=conversation_user_reads.c.unread_count + 1
                    )
                else:
                    # Insert new record
                    stmt = conversation_user_reads.insert().values(
                        conversation_id=self.id,
                        user_id=participant.id,
                        unread_count=1,
                        last_read_at=datetime.utcnow()
                    )
                
                db.session.execute(stmt)
        
        db.session.commit()
        
    
    def to_dict(self, for_user=None):
        """Convert conversation to dictionary with user-specific timezone"""
        data = {
            'id': self.id,
            'name': self.name,
            'conversation_type': self.conversation_type,
            'description': self.description,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'participants': [{
                'id': user.id,
                'firstName': user.first_name,
                'role': self.get_participant_role(user),
                'lastName': user.last_name,
                'profilePicture': user.profile_picture,
                'timezone': user.get_timezone()
            } for user in self.participants],
            'last_message': self.get_last_message_preview(for_user),
            'message_count': self.messages.count(),
            'unread_count': self.get_unread_message_count(for_user.id) if for_user else 0
        }
        
        return data

    @classmethod
    def find_or_create_direct_conversation(cls, user1, user2):
        """
        Find existing direct conversation between two users, or create a new one.
        Optimized for MySQL with proper indexing and query structure.
        
        Returns the conversation object.
        """
        if user1.id == user2.id:
            raise ValueError("Cannot create direct conversation with self")
        
        # Find existing direct conversation between these two users
        # Use a more efficient query for MySQL
        existing_conversation = cls.query\
            .join(conversation_participants)\
            .filter(cls.conversation_type == 'direct')\
            .filter(cls.is_active == True)\
            .filter(conversation_participants.c.user_id.in_([user1.id, user2.id]))\
            .group_by(cls.id)\
            .having(db.func.count(conversation_participants.c.user_id) == 2)\
            .first()
        
        if existing_conversation:
            return existing_conversation
        
        # Create new direct conversation
        conversation = cls(
            name=None,  # Direct conversations don't need names
            conversation_type='direct',
            created_by_id=user1.id
        )
        
        db.session.add(conversation)
        db.session.flush()  # Get the ID before committing
        
        # Add both participants
        conversation.add_participant(user1, 'member')
        conversation.add_participant(user2, 'member')
        
        db.session.commit()
        return conversation

# Association table for conversation participants
conversation_participants = db.Table('conversation_participants',
    db.Column('conversation_id', db.Integer, db.ForeignKey('chat_conversations.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow),
    db.Column('role', db.String(20), default='member')
)

conversation_user_reads = db.Table('conversation_user_reads',
    db.Column('conversation_id', db.Integer, db.ForeignKey('chat_conversations.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('last_read_at', db.DateTime, default=datetime.utcnow),
    db.Column('unread_count', db.Integer, default=0)
)