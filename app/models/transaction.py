from app.extensions import db

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    plan_id = db.Column(db.String(255), nullable=True)
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True, unique=True)
    stripe_checkout_session_id = db.Column(db.String(255), nullable=True, unique=True)
    type = db.Column(db.String(255), default="subscription")
    donation_message = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Integer)
    currency = db.Column(db.String(255))
    status = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship("User", back_populates="transactions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "stripe_payment_intent_id": self.stripe_payment_intent_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "donation_message": self.donation_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }