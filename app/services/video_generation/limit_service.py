from datetime import date
from app.extensions import db
from app.models.videoUsage import VideoUsage

DAILY_VIDEO_LIMIT = 3  # V1 limit


def can_generate_video(user_id: int) -> bool:
    """
    Check if user can generate a video today.
    """
    today = date.today()

    usage = VideoUsage.query.filter_by(
        user_id=user_id,
        usage_date=today
    ).first()

    if not usage:
        return True

    return usage.count < DAILY_VIDEO_LIMIT


def increment_video_usage(user_id: int):
    """
    Increment today's video usage for the user.
    """
    today = date.today()

    usage = VideoUsage.query.filter_by(
        user_id=user_id,
        usage_date=today
    ).first()

    if usage:
        usage.count += 1
    else:
        usage = VideoUsage(
            user_id=user_id,
            usage_date=today,
            count=1
        )
        db.session.add(usage)

    db.session.commit()


def remaining_videos(user_id: int) -> int:
    """
    Return remaining video generations for today.
    """
    today = date.today()

    usage = VideoUsage.query.filter_by(
        user_id=user_id,
        usage_date=today
    ).first()

    if not usage:
        return DAILY_VIDEO_LIMIT

    return max(0, DAILY_VIDEO_LIMIT - usage.count)
