

from datetime import datetime
from app.extensions import db


from datetime import datetime
from app.extensions import db

class FriendRequest(db.Model):
    __tablename__ = "friend_request"

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    status = db.Column(db.String(20), default="pending", nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_friend_requests",
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_friend_requests",
    )

    __table_args__ = (
        db.UniqueConstraint("sender_id", "receiver_id", name="unique_friend_request"),
        db.CheckConstraint("sender_id != receiver_id", name="no_self_request"),
    )

    def __repr__(self):
        return f"<FriendRequest {self.id}: {self.sender_id} -> {self.receiver_id} ({self.status})>"

    
    def to_dict(self, include_user_info=False):
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            if self.sender:
                data['sender'] = {
                    'id': self.sender.id,
                    'first_name': self.sender.first_name,
                    'last_name': self.sender.last_name,
                    'email': self.sender.email,
                }
            if self.receiver:
                data['receiver'] = {
                    'id': self.receiver.id,
                    'first_name': self.receiver.first_name,
                    'last_name': self.receiver.last_name,
                    'email': self.receiver.email,
                }
        
        return data

print("Loaded FriendRequest model from:", __file__)

