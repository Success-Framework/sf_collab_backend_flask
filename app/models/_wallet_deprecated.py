from datetime import datetime
from app.extensions import db
from enum import Enum

class TransactionType(str, Enum):
    EXCHANGE = "exchange"
    PURCHASE = "purchase"
    REWARD = "reward"
    REFUND = "refund"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"

class CurrencyType(str, Enum):
    SF_COINS = "sf_coins"
    PREMIUM_GEMS = "premium_gems"
    EVENT_TOKENS = "event_tokens"
    XP = "xp"

class UserWallet(db.Model):
    __tablename__ = 'user_wallets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Balances
    sf_coins = db.Column(db.Integer, default=0)
    premium_gems = db.Column(db.Integer, default=0)
    event_tokens = db.Column(db.Integer, default=0)
    
    # Lifetime Stats
    total_coins_earned = db.Column(db.Integer, default=0)
    total_coins_spent = db.Column(db.Integer, default=0)
    
    # Limits
    daily_earning_limit = db.Column(db.Integer, default=500) # Default limit
    daily_coins_earned = db.Column(db.Integer, default=0)
    last_earning_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='wallet')
    transactions = db.relationship('WalletTransaction', back_populates='wallet', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sf_coins': self.sf_coins,
            'premium_gems': self.premium_gems,
            'event_tokens': self.event_tokens,
            'total_coins_earned': self.total_coins_earned,
            'total_coins_spent': self.total_coins_spent,
            'daily_earning_limit': self.daily_earning_limit,
            'daily_coins_earned': self.daily_coins_earned,
            'last_earning_reset': self.last_earning_reset.isoformat() if self.last_earning_reset else None,
            'transactions': [t.to_dict() for t in self.transactions.order_by(WalletTransaction.created_at.desc()).limit(5)]
        }

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('user_wallets.id'), nullable=False)
    
    transaction_type = db.Column(db.String(50), nullable=False) # Enum as string for flexibility
    currency_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False) # Positive (credit) or Negative (debit)
    
    reference_type = db.Column(db.String(50), nullable=True) # e.g., "achievement", "product"
    reference_id = db.Column(db.String(255), nullable=True) # ID of the related item
    
    balance_before = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallet = db.relationship('UserWallet', back_populates='transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.transaction_type,
            'currency': self.currency_type,
            'amount': self.amount,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'balance_after': self.balance_after,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'

    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(50), nullable=False)
    to_currency = db.Column(db.String(50), nullable=False)
    rate = db.Column(db.Float, nullable=False) # Multiplier
    
    min_amount = db.Column(db.Integer, default=0)
    max_amount = db.Column(db.Integer, nullable=True)
    
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_to = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'from': self.from_currency,
            'to': self.to_currency,
            'rate': self.rate,
            'min': self.min_amount,
            'max': self.max_amount
        }
