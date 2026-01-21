from cryptography.fernet import Fernet
import os

FERNET_KEY = os.getenv("SMTP_ENCRYPTION_KEY")

if not FERNET_KEY:
    raise RuntimeError("SMTP_ENCRYPTION_KEY not set")

fernet = Fernet(FERNET_KEY)


def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
