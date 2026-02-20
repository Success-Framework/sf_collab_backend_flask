from datetime import datetime
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db


class UserWallet(db.Model):
    __tablename__ = 'user_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_earning_reset = db.Column(db.DateTime, default=datetime.utcnow)

    sf_coins = db.Column(Integer, default=0)
    premium_gems = db.Column(Integer, default=0)
    event_tokens = db.Column(Integer, default=0)
    credits = db.Column(Integer, default=0)
    total_coins_earned = db.Column(Integer, default=0)
    total_coins_spent = db.Column(Integer, default=0)
    daily_earnings = db.Column(Integer, default=0)
    daily_earning_limit = db.Column(Integer, default=1000)

    
    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship(
        "WalletTransaction",
        back_populates="wallet",
        cascade="all, delete-orphan"
    )
    event_token_balances = relationship("EventTokenBalance", back_populates="wallet")
    
    def check_and_reset_daily(self):
        """Check if daily earnings need to be reset (new day)"""
        now = datetime.utcnow()
        if self.last_earning_reset:
            if self.last_earning_reset.date() < now.date():
                self.daily_earnings = 0
                self.last_earning_reset = now
                db.session.commit()
    
    def earn_sf_coins(self, amount, description="Earned SF Coins"):
        """Earn SF Coins (subject to daily limit)"""
        from app.models.WalletTransaction import WalletTransaction
        
        self.check_and_reset_daily()
        
        if self.daily_earnings + amount > self.daily_earning_limit:
            raise ValueError("Daily earning limit exceeded")
        
        balance_before = self.sf_coins
        self.daily_earnings += amount
        self.total_coins_earned += amount
        self.sf_coins += amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="earn",
            currency_type="sf_coins",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.sf_coins,
            description=description
        )
        
        return self.sf_coins
    
    def spend_sf_coins(self, amount, description="Spent SF Coins"):
        """Spend SF Coins"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount > self.sf_coins:
            raise ValueError("Insufficient SF Coins")
        
        balance_before = self.sf_coins
        self.total_coins_spent += amount
        self.sf_coins -= amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="spend",
            currency_type="sf_coins",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.sf_coins,
            description=description
        )
        
        return self.sf_coins
    
    def add_premium_gems(self, amount, description="Added Premium Gems"):
        """Add Premium Gems (purchased currency)"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        balance_before = self.premium_gems
        self.premium_gems += amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="earn",
            currency_type="premium_gems",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.premium_gems,
            description=description
        )
        
        return self.premium_gems
    
    def spend_premium_gems(self, amount, description="Spent Premium Gems"):
        """Spend Premium Gems"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount > self.premium_gems:
            raise ValueError("Insufficient Premium Gems")
        
        balance_before = self.premium_gems
        self.premium_gems -= amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="spend",
            currency_type="premium_gems",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.premium_gems,
            description=description
        )
        
        return self.premium_gems
    
    def add_event_tokens(self, amount, description="Added Event Tokens"):
        """Add Event Tokens"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        balance_before = self.event_tokens
        self.event_tokens += amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="earn",
            currency_type="event_tokens",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.event_tokens,
            description=description
        )
        
        return self.event_tokens
    
    def spend_event_tokens(self, amount, description="Spent Event Tokens"):
        """Spend Event Tokens"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount > self.event_tokens:
            raise ValueError("Insufficient Event Tokens")
        
        balance_before = self.event_tokens
        self.event_tokens -= amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="spend",
            currency_type="event_tokens",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.event_tokens,
            description=description
        )
        
        return self.event_tokens
    
    def refund_sf_coins(self, amount, description="SF Coins Refunded"):
        """Refund SF Coins"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        balance_before = self.sf_coins
        self.sf_coins += amount
        self.total_coins_spent -= amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="refund",
            currency_type="sf_coins",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.sf_coins,
            description=description
        )
        
        return self.sf_coins

    def refund_premium_gems(self, amount, description="Premium Gems Refunded"):
        """Refund Premium Gems"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        balance_before = self.premium_gems
        self.premium_gems += amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="refund",
            currency_type="premium_gems",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.premium_gems,
            description=description
        )
    
        return self.premium_gems
    
    def award_bonus(self, amount, currency_type="sf_coins", description="Bonus Awarded"):
        """Award bonus (bypasses daily limit)"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Bonus amount must be positive")
        
        if currency_type == "sf_coins":
            balance_before = self.sf_coins
            self.sf_coins += amount
            self.total_coins_earned += amount
            balance_after = self.sf_coins
        elif currency_type == "premium_gems":
            balance_before = self.premium_gems
            self.premium_gems += amount
            balance_after = self.premium_gems
        elif currency_type == "event_tokens":
            balance_before = self.event_tokens
            self.event_tokens += amount
            balance_after = self.event_tokens
        elif currency_type == "credits":
            balance_before = self.credits
            self.credits += amount
            balance_after = self.credits
        else:
            raise ValueError(f"Invalid currency type: {currency_type}")
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="bonus",
            currency_type=currency_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description
        )
        
        return balance_after
    
    def add_credits(self, amount, description="Purchased Credits"):
        """Add Real Money Credits (purchased currency from Stripe)"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        balance_before = self.credits or 0
        self.credits = balance_before + amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="earn",
            currency_type="credits",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.credits,
            description=description
        )
        
        return self.credits

    def spend_credits(self, amount, description="Spent Credits"):
        """Spend Real Money Credits"""
        from app.models.WalletTransaction import WalletTransaction
        
        if amount > (self.credits or 0):
            raise ValueError("Insufficient Credits")
            
        balance_before = self.credits or 0
        self.credits = balance_before - amount
        
        WalletTransaction.record_transaction(
            wallet_id=self.id,
            user_id=self.user_id,
            transaction_type="spend",
            currency_type="credits",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.credits,
            description=description
        )
        
        return self.credits

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'sf_coins': self.sf_coins,
            'premium_gems': self.premium_gems,
            'event_tokens': self.event_tokens,
            'credits': self.credits,
            'total_coins_earned': self.total_coins_earned,
            'total_coins_spent': self.total_coins_spent,
            'daily_earnings': self.daily_earnings,
            'daily_earning_limit': self.daily_earning_limit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserWallet user_id={self.user_id} sf_coins={self.sf_coins} premium_gems={self.premium_gems} credits={self.credits}>'