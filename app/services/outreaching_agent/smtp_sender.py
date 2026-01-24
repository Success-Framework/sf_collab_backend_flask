import smtplib
import ssl
from email.mime.text import MIMEText
from app.utils.crypto import decrypt

class OutreachSMTPSender:
    def __init__(self, account):
        self.account = account
        self.password = decrypt(account.smtp_password_encrypted)

    def send_email(self, to_email, subject, body):
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = f"{self.account.from_name} <{self.account.email_address}>"
        msg["To"] = to_email

        server = smtplib.SMTP(
            self.account.smtp_host,
            self.account.smtp_port,
            timeout=30
        )

        try:
            if self.account.use_tls:
                server.starttls(context=ssl.create_default_context())

            server.login(self.account.smtp_username, self.password)

            server.sendmail(
                self.account.email_address,
                to_email,
                msg.as_string()
            )
        finally:
            server.quit()
