import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend


BUILD_KEY_STRING = "VaultDesktop2025SecureSecretsKey!"
BUILD_KEY = BUILD_KEY_STRING.encode('utf-8')[:32].ljust(32, b'\0')


def encrypt_firebase_file(input_path="vaultfirebase.json", output_path="vaultfirebase.enc"):
    """Encrypt Firebase credentials for production build"""
    return encrypt_secrets_file(input_path, output_path)


def get_firebase_credentials():
    try:
        import sys
        import os
        import json

        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
            firebase_enc_path = os.path.join(bundle_dir, 'vaultfirebase.enc')

            if os.path.exists(firebase_enc_path):
                with open(firebase_enc_path, 'r', encoding='utf-8') as f:
                    encrypted_data = f.read()

                firebase_data = decrypt_secrets_data(encrypted_data)
                if firebase_data:
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                        json.dump(firebase_data, tmp)
                        return tmp.name

        if os.path.exists("vaultfirebase.json"):
            return "vaultfirebase.json"

        return None

    except Exception as e:
        print(f"Error loading Firebase credentials: {e}")
        return None


def encrypt_secrets_file(input_path, output_path):
    """Encrypt secrets.json for production build"""
    try:
        # Read plaintext secrets
        with open(input_path, 'r', encoding='utf-8') as f:
            secrets_data = json.load(f)

        # Convert to JSON string
        json_data = json.dumps(secrets_data).encode('utf-8')

        # Generate random IV
        iv = os.urandom(16)

        # Pad data to AES block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        # Encrypt with AES
        cipher = Cipher(algorithms.AES(BUILD_KEY), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Combine IV + ciphertext and base64 encode
        encrypted_data = base64.b64encode(iv + ciphertext).decode('utf-8')

        # Write encrypted file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(encrypted_data)

        print(f"Secrets encrypted: {input_path} → {output_path}")
        return True

    except Exception as e:
        print(f"Secrets encryption failed: {e}")
        return False


def decrypt_secrets_data(encrypted_data):
    """Decrypt secrets at runtime"""
    try:
        # Decode base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))

        # Extract IV and ciphertext
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]

        # Decrypt with AES
        cipher = Cipher(algorithms.AES(BUILD_KEY), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        json_data = unpadder.update(padded_data) + unpadder.finalize()

        # Parse JSON
        return json.loads(json_data.decode('utf-8'))

    except Exception as e:
        print(f"❌ Secrets decryption failed: {e}")
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python secrets_encryption.py <input_secrets.json> <output_secrets.enc>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if encrypt_secrets_file(input_file, output_file):
        print("Secrets encryption complete!")
    else:
        print("Secrets encryption failed!")
        sys.exit(1)