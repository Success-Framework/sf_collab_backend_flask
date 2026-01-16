from datetime import datetime
from app.extensions import db
from sqlalchemy.ext.mutable import MutableDict, MutableList
class ContributionPoll(db.Model):
  __tablename__ = 'contribution_polls'
  
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text, nullable=False)
  options = db.Column(db.JSON, nullable=False)  # List of options
  points = db.Column(db.Integer, nullable=False)
  ends_in_days = db.Column(db.Integer, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  votes = db.Column(
        MutableDict.as_mutable(db.JSON),
        default=dict,
        nullable=False
    )

  users_voted = db.Column(
        MutableList.as_mutable(db.JSON),
        default=list,
        nullable=False
    )
  @staticmethod
  def autodelete_polls():
    """Delete polls that have ended"""
    now = datetime.utcnow()
    expired_polls = ContributionPoll.query.filter(
      ContributionPoll.created_at + db.func.cast(ContributionPoll.ends_in_days, db.Interval) < now
    ).all()
    
    for poll in expired_polls:
      db.session.delete(poll)
    
    db.session.commit()

  def get_total_votes(self, votes_dict = None):
    """Calculate total votes for the poll"""
    if votes_dict is None:
      votes_dict = self.votes
    return sum(votes_dict.values())
  def to_dict(self):
    return {
      'id': self.id,
      'title': self.title,
      'description': self.description,
      'options': self.options,
      'votes': self.votes,
      'usersVoted': self.users_voted,
      'points': self.points,
      'endsInDays': self.ends_in_days,
      'createdAt': self.created_at.isoformat()
    }