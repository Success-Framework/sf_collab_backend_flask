from datetime import datetime
from sqlalchemy.orm import relationship
from app.extensions import db


class EventTokenBalance(db.Model):
    """
    Tracks per-event token balances for a user's wallet.
    Each row represents one user's token balance for one specific event.
    """
    __tablename__ = "event_token_balances"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("user_wallets.id"), nullable=False)

    # Which event these tokens belong to
    event_key = db.Column(db.String(255), nullable=False)   # machine-readable key, e.g. "hackathon_2025"
    event_name = db.Column(db.String(255), nullable=True)   # human-readable name

    # Balances
    balance = db.Column(db.Integer, default=0)
    earned_total = db.Column(db.Integer, default=0)
    spent_total = db.Column(db.Integer, default=0)

    # Expiry (optional — null means tokens never expire)
    expires_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="event_token_balances")
    wallet = relationship("UserWallet", back_populates="event_token_balances")

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def add_event_tokens(self, amount: int):
        if self.is_expired():
            raise ValueError("Cannot add tokens to an expired balance")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        self.balance += amount
        self.earned_total += amount
        db.session.commit()

    def spend_event_tokens(self, amount: int):
        if self.is_expired():
            raise ValueError("Cannot spend expired tokens")
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient event tokens")

        self.balance -= amount
        self.spent_total += amount
        db.session.commit()

    def is_expired(self) -> bool:
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'wallet_id': str(self.wallet_id),
            'event_key': self.event_key,
            'event_name': self.event_name,
            'balance': self.balance,
            'earned_total': self.earned_total,
            'spent_total': self.spent_total,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<EventTokenBalance id={self.id} event={self.event_key} balance={self.balance}>'