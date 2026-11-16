import os
import hashlib, secrets

clear = "cls" if os.name == "nt" else "clear"

def hash_password(password: str):
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"{salt}${key}"

def verify_password(plain_password: str, stored_hash:str):
    try:
        salt, expected_key = stored_hash.split("$", 1)
        current_key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return secrets.compare_digest(current_key, expected_key)
    except(ValueError, AttributeError):
        return False