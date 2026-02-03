from app.extensions import db
from datetime import date

class VideoUsage(db.Model):
    __tablename__ = "video_usage"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    usage_date = db.Column(db.Date, nullable=False, default=date.today)
    count = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint("user_id", "usage_date", name="uq_user_video_day"),
    )
