from app.extensions import db
from datetime import datetime

class Error(db.Model):
  __tablename__ = 'errors'
  
  id = db.Column(db.Integer, primary_key=True)
  error_message = db.Column(db.String(500), nullable=False)
  error_from_backend = db.Column(db.Text, nullable=True)
  stack = db.Column(db.Text)
  page = db.Column(db.String(255))
  component = db.Column(db.String(255))
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  
  def __repr__(self):
    return f'<Error {self.id}: {self.error_message}>'
  def to_dict(self):
    return {
      'id': self.id,
      'errorMessage': self.error_message,
      'errorFromBackend': self.error_from_backend,
      'stack': self.stack,
      'page': self.page,
      'component': self.component,
      'timestamp': self.timestamp.isoformat(),
      'createdAt': self.created_at.isoformat()  
    }