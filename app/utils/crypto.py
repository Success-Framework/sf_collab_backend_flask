from cryptography.fernet import Fernet
import os

FERNET_KEY = os.getenv("SMTP_ENCRYPTION_KEY")

if not FERNET_KEY:
    raise RuntimeError("SMTP_ENCRYPTION_KEY not set")

fernet = Fernet(FERNET_KEY)

def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()
