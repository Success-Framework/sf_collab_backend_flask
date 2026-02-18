from datetime import datetime
from sqlalchemy.orm import relationship
from app.extensions import db



class EventTokenBalance(db.Model):
    __tablename__ = "event_token_balances"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("user_wallets.id"), nullable=False)

    event_key = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="event_token_balances")
    wallet = relationship("UserWallet", back_populates="event_token_balances")

    
    # Relationships
    user = relationship("User", back_populates="event_token_balances")
    wallet = relationship("UserWallet", back_populates="event_token_balances")

    def add_event_tokens(self, amount):
        if self.is_expired():
            raise ValueError("Cannot add tokens to an expired balance")

        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        self.earned_total += amount
        db.session.commit()

    def spend_event_tokens(self, amount):
        if self.is_expired():
            raise ValueError("Cannot spend expired tokens")
        if amount > self.balance:
            raise ValueError("Insufficient event tokens")
        self.balance -= amount
        self.spent_total += amount
        db.session.commit()

    def is_expired(self):
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'wallet_id': str(self.wallet_id),
            'event_id': self.event_id,
            'event_name': self.event_name,
            'balance': self.balance,
            'earned_total': self.earned_total,
            'spent_total': self.spent_total,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }

    def __repr__(self):
        return f'<EventTokenBalance {self.id} event={self.event_id} balance={self.balance}>'