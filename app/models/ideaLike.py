from datetime import datetime
from app.extensions import db

class IdeaLike(db.Model):
  __tablename__ = 'idea_likes'
  
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
  idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  
  liker = db.relationship('User', back_populates='idea_likes', foreign_keys=[user_id])
  liked_idea = db.relationship('Idea', back_populates='idea_likes', foreign_keys=[idea_id])
  
  def count(self):
    return IdeaLike.query.filter_by(idea_id=self.idea_id).count()
  def to_dict(self):
    return {
      'id': self.id,
      'user_id': self.user_id,
      'idea_id': self.idea_id,
      'created_at': self.created_at.isoformat(),
      'user': {
        'id': self.liker.id,
        'firstName': self.liker.first_name,
        'lastName': self.liker.last_name
      } if self.liker else None
    }