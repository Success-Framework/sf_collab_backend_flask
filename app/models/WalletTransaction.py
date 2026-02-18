from datetime import datetime
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db

transaction_type = db.Column(db.String(20), nullable=False)
currency_type = db.Column(db.String(20), nullable=False)



class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('user_wallets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    transaction_type = db.Column(db.String(20), nullable=False)   # "earn", "spend", ...
    currency_type = db.Column(db.String(20), nullable=False)      # "sf_coins", "premium_gems", ...

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    amount = db.Column(db.Integer, nullable=False)
    balance_before = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    xp_amount = db.Column(db.Integer, default=0)
    exchange_rate = db.Column(db.Float, default=0)
    reference_type = db.Column(db.Text, nullable=True)  # purchase, product, etc.
    reference_id = db.Column(db.String(255), nullable=True)  # ID of related entity
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    wallet = relationship("UserWallet", back_populates="transactions")
    user = relationship("User", back_populates="wallet_transactions")
    
    @staticmethod
    def record_transaction(wallet_id, user_id, transaction_type, currency_type, amount,
                           balance_before, balance_after, reference_type=None,
                           reference_id=None, description=None):
        transaction = WalletTransaction(
            wallet_id=wallet_id,
            user_id=user_id,
            transaction_type=transaction_type,
            currency_type=currency_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'wallet_id': str(self.wallet_id),
            'user_id': str(self.user_id),
            'transaction_type': self.transaction_type,
            'currency_type': self.currency_type,
            'amount': self.amount,
            'balance_before': self.balance_before,
            'balance_after': self.balance_after,
            'xp_amount': self.xp_amount,
            'exchange_rate': self.exchange_rate,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<WalletTransaction {self.id} {self.transaction_type} {self.amount} {self.currency_type}>'