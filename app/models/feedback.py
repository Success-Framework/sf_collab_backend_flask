from app.extensions import db
from datetime import datetime
from sqlalchemy import Enum

class Feedback(db.Model):
  __tablename__ = "feedback"

  # -------------------------
  # Core identity
  # -------------------------
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  
  # -------------------------
  # Feedback content
  # -------------------------
  content = db.Column(db.Text, nullable=False)
  
  # -------------------------
  # Metadata
  # -------------------------
  created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
  # -------------------------
  # Relationships
  # -------------------------

  
  # -------------------------
  # Serialization
  # -------------------------
  def to_dict(self):
    return {
      "id": self.id,
      "userId": self.user_id,
      "content": self.content,
      "createdAt": self.created_at.isoformat(),
      "updatedAt": self.updated_at.isoformat(),
    }