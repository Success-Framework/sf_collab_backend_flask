from cryptography.fernet import Fernet
from app.config import Config

def _get_fernet():
    key = Config.SMTP_ENCRYPTION_KEY
    if not key:
        raise RuntimeError("SMTP_ENCRYPTION_KEY not set")
    return Fernet(key.encode())

def encrypt(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()

def decrypt(value: str) -> str:
    return _get_fernet().decrypt(value.encode()).decode()
