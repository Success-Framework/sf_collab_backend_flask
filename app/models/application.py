from app.extensions import db
from sqlalchemy import String, Boolean, Text

class ApplicationJob(db.Model):
  """
  ApplicationJob Model
  Represents a job or influencer application submitted through the SForger platform.
  Stores applicant information and additional metadata for both job co-builder applications
  and influencer partnership applications.
  Attributes:
    id (int): Primary key identifier for the application record.
    name (str): Full name or brand name of the applicant (max 100 characters, required).
    email (str): Email address of the applicant (max 255 characters, required).
    country (str): Country or timezone information of the applicant (max 100 characters, optional).
    application_type (str): Type of application - either 'influencer' or 'job' (max 50 characters, required).
    created_at (datetime): Timestamp when the application was created (auto-set to current time).
    data (str): JSON-formatted string containing additional application data such as:
      - For job applications: area, skills, availability, earlyCoBuilder status, motivation, portfolio
      - For influencer applications: platform, profileLink, followers, niche, contribution, audienceFit, earlyPartner status
      (optional, stored as text/JSON format).
  Usage:
    Used to persist both job co-builder applications (developers, designers, content creators, etc.)
    and influencer/partner applications submitted through the SForger ecosystem.
  """
  __tablename__ = 'application_jobs'
  
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
  name = db.Column(String(100), nullable=False)
  email = db.Column(String(255), nullable=False)

  country = db.Column(String(100), nullable=True)
  application_type = db.Column(String(50), nullable=False)  # 'influencer' or 'job'
  created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
  data = db.Column(db.JSON, nullable=True)  # JSON or other format to store additional data
  
  def __repr__(self):
    return f'<ApplicationJob name={self.name}, email={self.email}>'
    application_type = db.Column(String(50), nullable=False)  # 'influencer' or 'job'
    data = db.Column(Text, nullable=True)  # JSON or other format to store additional data
  
  def to_dict(self):
    return {
      'id': self.id,
      'user_id': self.user_id,
      'name': self.name,
      'email': self.email,
      'country': self.country,
      'application_type': self.application_type,
      'created_at': self.created_at.isoformat(),
      'data': self.data
    }