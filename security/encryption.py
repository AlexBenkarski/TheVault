import json
import base64
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from config import get_current_vault_path

VAULT_PATH = get_current_vault_path()


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=900_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))  # Raw 32-byte key


def encrypt_vault(data: dict, key: bytes) -> bytes:
    backend = default_backend()
    iv = os.urandom(16)

    json_data = json.dumps(data).encode('utf-8')

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(json_data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return iv + ciphertext


def decrypt_vault(token: bytes, key: bytes) -> dict:
    backend = default_backend()
    iv = token[:16]
    ciphertext = token[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return json.loads(data.decode('utf-8'))


def ensure_vault_exists(key: bytes, vault_path: str = VAULT_PATH):
    if not os.path.exists(vault_path):
        empty_data = {}
        encrypted_data = encrypt_vault(empty_data, key)
        with open(vault_path, "wb") as f:
            f.write(encrypted_data)



def encrypt_password_with_recovery_key(password: str, recovery_key: str) -> str:
    backend = default_backend()

    recovery_salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=recovery_salt,
        iterations=900_000,
        backend=backend
    )
    key = kdf.derive(recovery_key.encode('utf-8'))

    iv = os.urandom(16)

    password_data = password.encode('utf-8')
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(password_data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_data = recovery_salt + iv + ciphertext
    return base64.b64encode(encrypted_data).decode('utf-8')


def decrypt_password_with_recovery_key(encrypted_password: str, recovery_key: str) -> str:
    backend = default_backend()

    try:
        encrypted_data = base64.b64decode(encrypted_password.encode('utf-8'))

        recovery_salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=recovery_salt,
            iterations=900_000,
            backend=backend
        )
        key = kdf.derive(recovery_key.encode('utf-8'))

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        password_data = unpadder.update(padded_data) + unpadder.finalize()

        return password_data.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decrypt password with recovery key: {e}")
