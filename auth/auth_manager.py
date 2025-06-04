import bcrypt
import secrets
import string
import base64
import hashlib


def hash_new_password(password):
    salt = bcrypt.gensalt(14)
    new_hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return new_hashed_password


def verify_login(input_password, stored_hashed_password, input_username, stored_username):
    input_password_encode = input_password.encode('utf-8')
    stored_hashed_password_encode = stored_hashed_password.encode('utf-8')

    if input_username == stored_username:
        if bcrypt.checkpw(input_password_encode, stored_hashed_password_encode):
            return True
        else:
            return False
    else:
        return False


def verify_password(input_password, stored_hashed_password):
    if not stored_hashed_password or not input_password:
        print("Verification error: Missing password input or stored hash.")
        return False

    try:
        input_password_encode = input_password.encode('utf-8')
        stored_hashed_password_encode = stored_hashed_password.encode('utf-8')

        return bcrypt.checkpw(input_password_encode, stored_hashed_password_encode)
    except ValueError as e:
        print("Verification error:", e)
        return False



def generate_recovery_key():
    chars = string.ascii_uppercase + string.digits
    segments = ["".join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
    return "-".join(segments)


def derive_recovery_key_hash(recovery_key: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        recovery_key.encode('utf-8'),
        salt,
        900_000
    )
    return base64.b64encode(dk).decode('utf-8')


def derive_key_from_recovery(recovery_key: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        'sha256',
        recovery_key.encode('utf-8'),
        salt,
        900_000,
        dklen=32
    )


def verify_recovery_key(input_key: str, stored_hash: str, salt: bytes) -> bool:
    try:
        derived_hash = derive_recovery_key_hash(input_key, salt)
        return secrets.compare_digest(derived_hash, stored_hash)
    except Exception as e:
        print("Recovery key verification error:", e)
        return False
