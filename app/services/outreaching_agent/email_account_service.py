from app.models.outreach.email_account import EmailAccount
from app.utils.crypto import encrypt, decrypt
from app.extensions import db


class EmailAccountService:

    @staticmethod
    def create_email_account(user_id: int, data: dict):
        account = EmailAccount(
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
        return account

    @staticmethod
    def get_decrypted_password(account: EmailAccount) -> str:
        return decrypt(account.smtp_password_encrypted)
