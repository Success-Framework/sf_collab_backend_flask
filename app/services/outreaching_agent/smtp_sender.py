import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.outreach.email_account import EmailAccount
from app.models.outreach.suppression import SuppressionList
from app.extensions import db
from datetime import datetime
import traceback


class SMTPSender:
    def __init__(self, email_account: EmailAccount):
        self.email_account = email_account

    def send_email(self, to_email: str, subject: str, body: str, unsubscribe_url: str):
        """
        Send a single email using user's SMTP account
        """

        # 🔒 Suppression safety check
        if SuppressionList.query.filter_by(email=to_email).first():
            return {
                "success": False,
                "error": "Email is suppressed"
            }

        msg = MIMEMultipart()
        msg["From"] = f"{self.email_account.from_name} <{self.email_account.email_address}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        full_body = f"""
{body}

---

If you don’t want to receive emails like this, unsubscribe here:
{unsubscribe_url}
"""

        msg.attach(MIMEText(full_body, "plain"))

        try:
            context = ssl.create_default_context()

            with smtplib.SMTP(
                self.email_account.smtp_host,
                self.email_account.smtp_port,
                timeout=30
            ) as server:

                if self.email_account.use_tls:
                    server.starttls(context=context)

                server.login(
                    self.email_account.smtp_username,
                    self.email_account.smtp_password_encrypted  # decrypted before save
                )

                server.sendmail(
                    self.email_account.email_address,
                    to_email,
                    msg.as_string()
                )

            return {"success": True}

        except Exception as e:
            print("SMTP SEND ERROR")
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e)
            }
