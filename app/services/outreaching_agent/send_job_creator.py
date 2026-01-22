from app.models.outreach_sendjobs import OutreachSendJob
from app.models.outreach_contact import OutreachContact
from app.extensions import db

def create_send_jobs(campaign, draft):
    contacts = OutreachContact.query.filter_by(
        campaign_id=campaign.id
    ).all()

    created = 0

    for contact in contacts:
        exists = OutreachSendJob.query.filter_by(
            campaign_id=campaign.id,
            contact_id=contact.id
        ).first()

        if exists:
            continue

        job = OutreachSendJob(
            campaign_id=campaign.id,
            contact_id=contact.id,
            draft_id=draft.id,
            email_account_id=campaign.email_account_id
        )
        db.session.add(job)
        created += 1

    db.session.commit()
    return created
