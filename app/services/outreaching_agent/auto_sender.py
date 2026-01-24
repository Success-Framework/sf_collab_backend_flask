import time
import random
from datetime import datetime
from app.extensions import db
from app.models.outreach_sendjobs import OutreachSendJob
from app.models.outreach_contact import OutreachContact
from app.models.outreach_draft import OutreachDraft
from app.models.outreach_email_account import OutreachEmailAccount
from app.services.outreaching_agent.smtp_sender import OutreachSMTPSender
from app.services.outreaching_agent.send_limits import can_send_email
from app.utils.crypto import decrypt

def run_auto_sender(campaign_id):
    jobs = OutreachSendJob.query.filter_by(
        campaign_id=campaign_id,
        status="queued"
    ).order_by(OutreachSendJob.created_at.asc()).all()

    for job in jobs:
        email_account = OutreachEmailAccount.query.get(job.email_account_id)

        can_send, reason = can_send_email(
            email_account.id,
            email_account.hourly_limit,
            email_account.daily_limit
        )

        if not can_send:
            break  # stop sending safely

        contact = OutreachContact.query.get(job.contact_id)
        draft = OutreachDraft.query.get(job.draft_id)

        sender = OutreachSMTPSender(email_account)

        try:
            job.status = "sending"
            db.session.commit()

            sender.send_email(
                to_email=contact.email,
                subject=draft.subject,
                body=draft.body
            )

            job.status = "sent"
            job.sent_at = datetime.utcnow()
            db.session.commit()

            # polite delay (anti-spam)
            time.sleep(random.uniform(8, 15))

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.attempts += 1
            db.session.commit()
