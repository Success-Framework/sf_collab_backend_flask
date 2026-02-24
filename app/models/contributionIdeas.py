from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum, JSON
from .Enums import ResourceStatus, Privacy

# filepath: /Users/ivandavidgomezsilva/Documents/Ivan/Trabajos/SFORGER/SForger_data/SFRepos/sf_collab_backend_flask/app/models/contributionIdeas.py

class ContributionIdea(db.Model):
  __tablename__ = 'contribution_ideas'
  
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text, nullable=False)
  impact = db.Column(db.String(50), nullable=False)  # small, medium, large
  area = db.Column(db.String(100), nullable=False)  # product, design, backend, frontend, etc.
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  status = db.Column(db.String(50), nullable=False) # pending, approved, rejected
  created_at = db.Column(db.DateTime, default=datetime.utcnow)  
  
  user = db.relationship('User', back_populates='contribution_ideas', foreign_keys=[user_id])
  def to_dict(self):
    data = {
      'id': self.id,
      'title': self.title,
      'description': self.description,
      'impact': self.impact,
      'area': self.area,
      'status': self.status,
      'user_id': self.user_id,
      'createdAt': self.created_at.isoformat(),
      'user': {
        'id': self.user.id,
        'first_name': self.user.first_name,
        'last_name': self.user.last_name,
        'profile_picture': self.user.profile_picture
      } if self.user else None
    }
    
    return data