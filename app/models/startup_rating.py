from datetime import datetime
from app.extensions import db

class StartupRating(db.Model):
    __tablename__ = 'startup_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    startup_id = db.Column(db.Integer, db.ForeignKey('startups.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1.0 to 5.0
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('startup_ratings', lazy='dynamic'))
    startup = db.relationship('Startup', back_populates='ratings')

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'startup_id', name='unique_user_startup_rating'),
    )
