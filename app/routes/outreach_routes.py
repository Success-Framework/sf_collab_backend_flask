from flask import Blueprint
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.outreach_email_account import OutreachEmailAccount
from app.utils.crypto import encrypt
from app.services.outreaching_agent.smtp_sender import OutreachSMTPSender
from app.models.outreach_campaign import OutreachCampaign
from app.models.outreach_contact import OutreachContact
from app.models.outreach_draft import OutreachDraft
from app.services.outreaching_agent.draft_generator import generate_outreach_draft
from app.models.user import User
from app.models.outreach_sendjobs import OutreachSendJob
from app.services.outreaching_agent.send_job_creator import create_send_jobs
from app.services.outreaching_agent.auto_sender import run_auto_sender




outreach_bp = Blueprint("outreach", __name__)

@outreach_bp.route("/email-accounts", methods=["POST"])
@jwt_required()
def add_email_account():
    user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = [
        "emailAddress",
        "fromName",
        "smtpHost",
        "smtpPort",
        "smtpUsername",
        "smtpPassword"
    ]

    for field in required_fields:
        if field not in data:
            return {"success": False, "error": f"{field} is required"}, 400

    account = OutreachEmailAccount(
        user_id=user_id,
        email_address=data["emailAddress"],
        from_name=data["fromName"],
        smtp_host=data["smtpHost"],
        smtp_port=data["smtpPort"],
        smtp_username=data["smtpUsername"],
        smtp_password_encrypted=encrypt(data["smtpPassword"]),
        use_tls=data.get("useTls", True),
        daily_limit=data.get("dailyLimit", 200),
        hourly_limit=data.get("hourlyLimit", 40),
    )

    db.session.add(account)
    db.session.commit()

    return {
        "success": True,
        "data": account.to_dict()
    }, 201


@outreach_bp.route("/email-accounts", methods=["GET"])
@jwt_required()
def list_email_accounts():
    user_id = get_jwt_identity()

    accounts = OutreachEmailAccount.query.filter_by(
        user_id=user_id,
        is_active=True
    ).all()

    return {
        "success": True,
        "data": [a.to_dict() for a in accounts]
    }

@outreach_bp.route("/email-accounts/<int:account_id>/test", methods=["POST"])
@jwt_required()
def test_email_account(account_id):
    user_id = get_jwt_identity()

    account = OutreachEmailAccount.query.filter_by(
        id=account_id,
        user_id=user_id
    ).first_or_404()

    sender = OutreachSMTPSender(account)

    try:
        sender.send_test_email(account.email_address)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }, 400

    return {"success": True}


@outreach_bp.route("/campaigns", methods=["POST"])
@jwt_required()
def create_campaign():
    user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = ["name", "targetType", "description", "emailAccountId"]
    for field in required_fields:
        if field not in data:
            return {"success": False, "error": f"{field} is required"}, 400

    # Verify email account ownership
    email_account = OutreachEmailAccount.query.filter_by(
        id=data["emailAccountId"],
        user_id=user_id,
        is_active=True
    ).first()

    if not email_account:
        return {"success": False, "error": "Invalid email account"}, 403

    campaign = OutreachCampaign(
        user_id=user_id,
        email_account_id=email_account.id,
        name=data["name"],
        target_type=data["targetType"],
        description=data["description"],
        industry=data.get("industry"),
        location=data.get("location"),
        max_emails=data.get("maxEmails")
    )

    db.session.add(campaign)
    db.session.commit()

    return {
        "success": True,
        "data": campaign.id
    }, 201


@outreach_bp.route("/campaigns", methods=["GET"])
@jwt_required()
def list_campaigns():
    user_id = get_jwt_identity()

    campaigns = OutreachCampaign.query.filter_by(
        user_id=user_id
    ).order_by(OutreachCampaign.created_at.desc()).all()

    return {
        "success": True,
        "data": [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "targetType": c.target_type,
                "createdAt": c.created_at.isoformat()
            }
            for c in campaigns
        ]
    }

@outreach_bp.route("/campaigns/<int:campaign_id>/contacts", methods=["POST"])
@jwt_required()
def add_contacts(campaign_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not isinstance(data, list):
        return {"success": False, "error": "Expected a list of contacts"}, 400

    campaign = OutreachCampaign.query.filter_by(
        id=campaign_id,
        user_id=user_id
    ).first_or_404()

    created = 0
    skipped = 0

    for contact in data:
        email = contact.get("email")
        if not email:
            continue

        exists = OutreachContact.query.filter_by(
            campaign_id=campaign.id,
            email=email
        ).first()

        if exists:
            skipped += 1
            continue

        c = OutreachContact(
            campaign_id=campaign.id,
            company_name=contact.get("companyName"),
            email=email,
            source=contact.get("source", "manual")
        )
        db.session.add(c)
        created += 1

    db.session.commit()

    return {
        "success": True,
        "created": created,
        "skipped": skipped
    }


@outreach_bp.route("/campaigns/<int:campaign_id>/draft", methods=["POST"])
@jwt_required()
def generate_draft(campaign_id):
    user_id = get_jwt_identity()

    campaign = OutreachCampaign.query.filter_by(
        id=campaign_id,
        user_id=user_id
    ).first_or_404()

    existing = OutreachDraft.query.filter_by(
        campaign_id=campaign.id
    ).first()

    if existing:
        return {
            "success": True,
            "data": {
                "subject": existing.subject,
                "body": existing.body,
                "status": existing.status
            }
        }

    user = User.query.get(user_id)

    subject, body = generate_outreach_draft(campaign, user)

    draft = OutreachDraft(
        campaign_id=campaign.id,
        subject=subject,
        body=body,
        status="approved"
    )

    db.session.add(draft)
    db.session.commit()

    return {
        "success": True,
        "data": {
            "subject": subject,
            "body": body,
            "status": draft.status
        }
    }

@outreach_bp.route("/drafts/<int:draft_id>", methods=["PATCH"])
@jwt_required()
def update_draft(draft_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    draft = OutreachDraft.query.join(
        OutreachCampaign,
        OutreachDraft.campaign_id == OutreachCampaign.id
    ).filter(
        OutreachDraft.id == draft_id,
        OutreachCampaign.user_id == user_id
    ).first_or_404()

    if "subject" in data:
        draft.subject = data["subject"]
    if "body" in data:
        draft.body = data["body"]

    draft.status = "approved"

    db.session.commit()

    return {"success": True}


@outreach_bp.route("/campaigns/<int:campaign_id>/send", methods=["POST"])
@jwt_required()
def send_campaign(campaign_id):
    user_id = get_jwt_identity()

    campaign = OutreachCampaign.query.filter_by(
        id=campaign_id,
        user_id=user_id
    ).first_or_404()

    draft = OutreachDraft.query.filter_by(
        campaign_id=campaign.id,
        status="approved"
    ).first()

    if not draft:
        return {
            "success": False,
            "error": "Draft not approved"
        }, 400

    created = create_send_jobs(campaign, draft)

    campaign.status = "sending"
    db.session.commit()

    # AUTO SEND (controlled)
    run_auto_sender(campaign.id)

    return {
        "success": True,
        "jobsCreated": created
    }


@outreach_bp.route("/campaigns/<int:campaign_id>/send-status", methods=["GET"])
@jwt_required()
def campaign_send_status(campaign_id):
    user_id = get_jwt_identity()

    campaign = OutreachCampaign.query.filter_by(
        id=campaign_id,
        user_id=user_id
    ).first_or_404()

    total = OutreachSendJob.query.filter_by(
        campaign_id=campaign.id
    ).count()

    sent = OutreachSendJob.query.filter_by(
        campaign_id=campaign.id,
        status="sent"
    ).count()

    failed = OutreachSendJob.query.filter_by(
        campaign_id=campaign.id,
        status="failed"
    ).count()

    return {
        "success": True,
        "status": campaign.status,
        "total": total,
        "sent": sent,
        "failed": failed
    }
