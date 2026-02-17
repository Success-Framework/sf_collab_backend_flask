from sqlalchemy import Float, Boolean
from datetime import datetime
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db
from sqlalchemy import JSON


class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(50), nullable=False)
    to_currency = db.Column(db.String(50), nullable=False)
    base_rate = db.Column(Float, nullable=False)
    current_rate = db.Column(Float, nullable=False)
    min_amount = db.Column(Integer, default=1)
    max_amount = db.Column(Integer, default=100000)
    demand_factor = db.Column(Float, default=1.0)
    time_factor = db.Column(Float, default=1.0)
    user_tier_factor = db.Column(Float, default=1.0)
    is_active = db.Column(Boolean, default=True)
    effective_from = db.Column(db.DateTime, nullable=True)
    effective_to = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'base_rate': self.base_rate,
            'current_rate': self.current_rate,
            'min_amount': self.min_amount,
            'max_amount': self.max_amount,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_rate(cls, from_currency, to_currency):
        """Get current exchange rate between two currencies"""
        now = datetime.utcnow()
        rate = cls.query.filter(
            cls.from_currency == from_currency,
            cls.to_currency == to_currency,
            cls.is_active == True,
            (cls.effective_from == None) | (cls.effective_from <= now),
            (cls.effective_to == None) | (cls.effective_to >= now)
        ).first()
        return rate
    
    def __repr__(self):
        return f'<ExchangeRate {self.from_currency}->{self.to_currency} rate={self.current_rate}>'