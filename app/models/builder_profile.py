from datetime import datetime
from app.extensions import db


class BuilderProfile(db.Model):
    __tablename__ = "builder_profile"

    id = db.Column(db.Integer, primary_key=True)

    # 🔗 Relationship to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    user = db.relationship("User", backref=db.backref("builder_profile", uselist=False))

    # 🧠 Core Matchmaking Fields
    bio = db.Column(db.Text, nullable=True)

    # Store as JSON arrays → flexible & scalable
    skills = db.Column(db.JSON, default=[])
    sector_interests = db.Column(db.JSON, default=[])

    experience_level = db.Column(db.String(50), nullable=True)
    collaboration_intent = db.Column(db.String(100), nullable=True)

    # Example: AVAILABLE, OPEN, NOT_AVAILABLE
    availability = db.Column(db.String(50), default="AVAILABLE")

    # 🔥 Important for scoring
    execution_score = db.Column(db.Integer, default=50)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bio": self.bio,
            "skills": self.skills or [],
            "sector_interests": self.sector_interests or [],
            "experience_level": self.experience_level,
            "collaboration_intent": self.collaboration_intent,
            "availability": self.availability,
            "execution_score": self.execution_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }