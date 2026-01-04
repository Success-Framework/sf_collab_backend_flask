from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.extensions import db

# filepath: /Users/ivandavidgomezsilva/Documents/Ivan/Trabajos/SFORGER/SForger_data/SFRepos/sf_collab_backend_flask/app/models/userRole.py

class UserRole(db.Model):
  __tablename__ = 'user_roles'
  
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  role = db.Column(db.String(50), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  
  __table_args__ = (
    db.UniqueConstraint('user_id', 'role', name='unique_user_role'),
  )
  
  def __repr__(self):
    return f'<UserRole user_id={self.user_id} role={self.role}>'

  @property
  def is_influencer(self):
    return self.role == 'influencer'
  
  @property
  def is_admin(self):
    return self.role == 'admin'
  
  @property
  def is_builder(self):
    return self.role == 'builder'
  
  @property
  def is_founder(self):
    return self.role == 'founder'
  @property
  def is_investor(self):
    return self.role == 'investor'