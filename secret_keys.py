import secrets

secret_key = secrets.token_hex(32)
jwt_secret_key = secrets.token_hex(64)

print("SECRET_KEY =", secret_key)
print("JWT_SECRET_KEY =", jwt_secret_key)
