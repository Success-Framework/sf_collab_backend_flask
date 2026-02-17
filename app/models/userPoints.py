from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
import uuid
from . import db, UUID, TIMESTAMP


class PointsUser(db.Model):
    __tablename__ = "points_users"


    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=True)  # Optional for now
    created_at = db.Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    #wallet = relationship("UserWallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions = relationship("WalletTransaction", back_populates="user", cascade="all, delete-orphan")
    purchases = relationship('ProductPurchase', back_populates='user', cascade="all, delete-orphan")
    inventory = relationship('UserInventory', back_populates='user', cascade="all, delete-orphan")
    event_token_balances = db.relationship("EventTokenBalance", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"

    """# Set password
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    # Check password
    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # Save user to database
    def save(self):
        db.session.add(self)
        db.session.commit()

    # Delete user from database
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # Find user by email
    @classmethod
    def find_by_email(cls, email: str):
        return cls.query.filter_by(email=email).first()

    # Find user by username
    @classmethod
    def find_by_username(cls, username: str):
        return cls.query.filter_by(username=username).first()"""
