from datetime import datetime
from app.extensions import db
from app.models.wallet import UserWallet, WalletTransaction, TransactionType, CurrencyType, ExchangeRate
from app.models.user import User

class DailyLimitExceeded(Exception):
    """Raised when a user has hit their daily earning limit"""
    def __init__(self, limit, earned_today, requested):
        self.limit = limit
        self.earned_today = earned_today
        self.requested = requested
        remaining = max(0, limit - earned_today)
        super().__init__(
            f"Daily earning limit reached. "
            f"Limit: {limit}, Earned today: {earned_today}, "
            f"Requested: {requested}, Remaining: {remaining}"
        )

class WalletService:
    @staticmethod
    def get_wallet(user_id):
        """Get or create a wallet for the user"""
        wallet = UserWallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            wallet = UserWallet(user_id=user_id)
            db.session.add(wallet)
            db.session.commit()
        return wallet

    @staticmethod
    def _reset_daily_limit_if_needed(wallet):
        """Reset daily earning counter if a new day has started"""
        now = datetime.utcnow()
        if wallet.last_earning_reset is None or wallet.last_earning_reset.date() < now.date():
            wallet.daily_coins_earned = 0
            wallet.last_earning_reset = now

    @staticmethod
    def add_funds(user_id, amount, currency_type, transaction_type, reference_type=None, reference_id=None, description=None):
        """Add funds to user wallet with daily earning limit enforcement for SF Coins"""
        wallet = WalletService.get_wallet(user_id)
        
        # Enforce daily earning limit for SF Coins
        if currency_type == "sf_coins" and amount > 0:
            WalletService._reset_daily_limit_if_needed(wallet)
            
            remaining = wallet.daily_earning_limit - wallet.daily_coins_earned
            if remaining <= 0:
                raise DailyLimitExceeded(
                    wallet.daily_earning_limit, wallet.daily_coins_earned, amount
                )
            
            # Cap the amount to what's remaining
            if amount > remaining:
                amount = remaining
        
        balance_before = getattr(wallet, currency_type)
        balance_after = balance_before + amount
        
        # Update wallet balance
        setattr(wallet, currency_type, balance_after)
        
        # Update stats if adding coins
        if currency_type == "sf_coins" and amount > 0:
            wallet.total_coins_earned += amount
            wallet.daily_coins_earned += amount
            
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=transaction_type,
            currency_type=currency_type,
            amount=amount,
            reference_type=reference_type,
            reference_id=str(reference_id) if reference_id else None,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description
        )
        
        db.session.add(transaction)
        db.session.commit()
        return wallet

    @staticmethod
    def deduct_funds(user_id, amount, currency_type, transaction_type, reference_type=None, reference_id=None, description=None):
        """Deduct funds from user wallet"""
        wallet = WalletService.get_wallet(user_id)
        
        balance_before = getattr(wallet, currency_type)
        if balance_before < amount:
            raise ValueError(f"Insufficient {currency_type} balance")
            
        balance_after = balance_before - amount
        
        # Update wallet balance
        setattr(wallet, currency_type, balance_after)
        
        # Update stats
        if currency_type == CurrencyType.SF_COINS:
            wallet.total_coins_spent += amount

        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=transaction_type,
            currency_type=currency_type,
            amount=-amount, # Negative for deduction
            reference_type=reference_type,
            reference_id=str(reference_id) if reference_id else None,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description
        )
        
        db.session.add(transaction)
        db.session.commit()
        return wallet

    @staticmethod
    def exchange_currency(user_id, from_currency, to_currency, amount):
        """Exchange one currency for another based on active rates"""
        rate = ExchangeRate.query.filter_by(
            from_currency=from_currency, 
            to_currency=to_currency, 
            is_active=True
        ).first()
        
        if not rate:
            raise ValueError("Exchange rate not found or inactive")
            
        # Calculate resulting amount
        to_amount = int(amount * rate.rate)
        
        # Deduct from source
        WalletService.deduct_funds(
            user_id, amount, from_currency, 
            TransactionType.EXCHANGE, 
            description=f"Exchanged for {to_currency}"
        )
        
        # Add to destination
        wallet = WalletService.add_funds(
            user_id, to_amount, to_currency, 
            TransactionType.EXCHANGE, 
            description=f"Exchanged from {from_currency}"
        )
        
        return wallet
