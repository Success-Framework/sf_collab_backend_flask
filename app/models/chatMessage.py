from datetime import datetime
from app.extensions import db
from sqlalchemy import JSON
from app.models.user import User

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Store original message content without time conversion
    original_content = db.Column(db.Text, nullable=False)
    
    # Store sender's timezone for proper conversion
    sender_timezone = db.Column(db.String(50), default='UTC')
    
    # Message metadata
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    metadata_data = db.Column(JSON, default={})  # For file URLs, image dimensions, etc.
    
    # Status tracking
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)
    
    # Reply functionality
    reply_to_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'), nullable=True)
    
    # File fields
    file_url = db.Column(db.String(500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    file_type = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    message_sender = db.relationship(
        'User', 
        back_populates='sent_messages', 
        foreign_keys=[sender_id])
        
    conversation = db.relationship(
        'ChatConversation', 
        back_populates='messages', 
        foreign_keys=[conversation_id])
        
    reply_to = db.relationship(
        'ChatMessage', 
        remote_side=[id], 
        back_populates='replies', 
        foreign_keys=[reply_to_id])
        
    replies = db.relationship(
        "ChatMessage",
        back_populates="reply_to",
        cascade="all, delete-orphan",
        foreign_keys=[reply_to_id]
    )
    
    # HELPER FUNCTIONS
    
    def prepare_for_sending(self, sender_user=None):
        """Prepare message for sending by adding time placeholder"""
        from app.utils.timezone_converter import TimezoneConverter
        
        if sender_user:
            self.sender_timezone = sender_user.get_timezone()
        
        # Check if content already has time placeholders
        import re
        time_pattern = r'\[(\d{1,2}:\d{2})\]'
        has_existing_placeholders = bool(re.search(time_pattern, self.original_content))
        
        if has_existing_placeholders:
            # If content already has placeholders, return as-is
            return self.original_content
        
        # # Only add time placeholder if there are no existing placeholders
        # time_placeholder = TimezoneConverter.create_time_placeholder(
        #     self.created_at, 
        #     self.sender_timezone
        # )
        
        # Combine placeholder with original content
        return f"{self.original_content}"
    
    def get_content_for_user(self, user):
        """Get message content converted for specific user's timezone"""
        from app.utils.timezone_converter import TimezoneConverter
        
        user_tz = user.get_timezone()
        
        # Check if content already has time placeholders
        import re
        time_pattern = r'\[(\d{1,2}:\d{2})\]'
        has_existing_placeholders = bool(re.search(time_pattern, self.original_content))
        
        if has_existing_placeholders:
            # Convert existing placeholders to user's timezone
            converted_content = TimezoneConverter.replace_time_placeholder_for_user(
                self.original_content,  # Use original content directly
                self.created_at,
                user_tz,
                self.sender_timezone
            )
            return converted_content
        else:
            # No placeholders, use the standard preparation
            return self.prepare_for_sending()
    
    def to_dict(self, for_user=None):
        """Convert message to dictionary, with timezone conversion if user provided"""
        base_data = {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'original_content': self.original_content,
            'message_type': self.message_type,
            'metadata': self.metadata_data or {},
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'reply_to_id': self.reply_to_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'sender_timezone': self.sender_timezone,
            # File fields
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
        }
        
        # If specific user provided, convert time for them
        if for_user:
            base_data['content'] = self.get_content_for_user(for_user)
            base_data['display_time'] = self.get_display_time_info(for_user)
        else:
            base_data['content'] = self.prepare_for_sending()
        
        # Include sender info if available
        if self.sender_id:
            user = User.query.get(self.sender_id)
            base_data['sender'] = {
                'id': user.id,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'profilePicture': user.profile_picture
            }
        
        # Include reply info if available
        if self.reply_to:
            base_data['reply_to'] = {
                'id': self.reply_to.id,
                'content': self.reply_to.original_content,
                'sender_id': self.reply_to.sender_id
            }
        
        return base_data
    
    def get_display_time_info(self, user):
        """Get comprehensive time display information for a user"""
        from app.utils.timezone_converter import TimezoneConverter
        user_tz = user.get_timezone()
        return TimezoneConverter.get_time_display_info(self.created_at, user_tz)
    
    def edit_message(self, new_content, metadata_data):
        """Edit message content"""
        self.original_content = new_content
        self.metadata_data = metadata_data
        self.is_edited = True
        self.edited_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_read(self, user_id):
        """Mark message as read by user"""
        # This would require a read_receipts table in a real implementation
        # For now, this is a placeholder
        pass
    
    def has_file(self):
        """Check if message has an attached file"""
        return self.file_url is not None
    
    def is_image(self):
        """Check if the attached file is an image"""
        if not self.file_type:
            return False
        return self.file_type.startswith('image/')
    
    def is_document(self):
        """Check if the attached file is a document"""
        if not self.file_type:
            return False
        document_types = ['application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'text/plain']
        return self.file_type in document_types
    
    def get_file_info(self):
        """Get file information as a dictionary"""
        if not self.has_file():
            return None
        
        return {
            'url': self.file_url,
            'name': self.file_name,
            'size': self.file_size,
            'type': self.file_type,
            'is_image': self.is_image(),
            'is_document': self.is_document()
        }