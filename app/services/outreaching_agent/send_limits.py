from datetime import datetime, timedelta
from app.models.outreach_sendjobs import OutreachSendJob

def can_send_email(email_account_id, hourly_limit, daily_limit):
    now = datetime.utcnow()

    hourly_count = OutreachSendJob.query.filter(
        OutreachSendJob.email_account_id == email_account_id,
        OutreachSendJob.sent_at >= now - timedelta(hours=1)
    ).count()

    if hourly_count >= hourly_limit:
        return False, "Hourly limit reached"

    daily_count = OutreachSendJob.query.filter(
        OutreachSendJob.email_account_id == email_account_id,
        OutreachSendJob.sent_at >= now - timedelta(days=1)
    ).count()

    if daily_count >= daily_limit:
        return False, "Daily limit reached"

    return True, None
