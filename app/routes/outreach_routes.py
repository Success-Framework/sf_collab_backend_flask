from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.outreaching_agent.smtp_sender import SMTPSender
from app.models.outreach_email_account import EmailAccount
from app.utils.crypto import decrypt

@outreach_bp.route("/email-accounts/<int:account_id>/test", methods=["POST"])
@jwt_required()
def test_smtp(account_id):
    user_id = get_jwt_identity()

    account = EmailAccount.query.filter_by(
        id=account_id, user_id=user_id
    ).first_or_404()

    account.smtp_password_encrypted = decrypt(account.smtp_password_encrypted)

    sender = SMTPSender(account)

    result = sender.send_email(
        to_email=account.email_address,
        subject="SMTP Test – SFCollab Outreach",
        body="This is a test email to verify your SMTP settings.",
        unsubscribe_url="https://sfcollab.com/unsubscribe"
    )

    if not result["success"]:
        return {"success": False, "error": result["error"]}, 400

    return {"success": True}
