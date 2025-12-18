from datetime import datetime
from app.extensions import db

class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending'
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_requests"
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_requests"
    )


    def __repr__(self):
        return f"<FriendRequest id={self.id} from={self.sender_id} to={self.receiver_id} status={self.status}>"

    def to_dict(self, include_user_info=False):
        """Convert friend request to dictionary"""
        data = {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user_info:
            from app.models.user import User
            sender = User.query.get(self.sender_id)
            receiver = User.query.get(self.receiver_id)
            
            data['sender'] = {
                'id': sender.id,
                'first_name': sender.first_name,
                'last_name': sender.last_name,
                'email': sender.email
            } if sender else None
            
            data['receiver'] = {
                'id': receiver.id,
                'first_name': receiver.first_name,
                'last_name': receiver.last_name,
                'email': receiver.email
            } if receiver else None
        
        return data

    def is_expired(self, expiry_days=30):
        """Check if pending request is expired"""
        if self.status != 'pending':
            return False
        
        expiry_date = self.created_at + datetime.timedelta(days=expiry_days)
        return datetime.utcnow() > expiry_date