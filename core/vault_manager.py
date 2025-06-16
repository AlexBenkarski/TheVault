import base64
import json
import os
import re
from auth.auth_manager import verify_recovery_key, verify_login, derive_recovery_key_hash, generate_recovery_key, hash_new_password
from config import get_vault_path, get_auth_path
from security.encryption import decrypt_vault, encrypt_vault, derive_key, decrypt_password_with_recovery_key, encrypt_password_with_recovery_key
try:
    from dev_tools.dev_manager import DEV_MODE_ACTIVE, get_mock_credentials, get_mock_credentials, get_current_mock_data
except ImportError:
    DEV_MODE_ACTIVE = False
    get_mock_credentials = lambda: (None, None)
    get_current_mock_data = lambda: {}


def load_vault(key: bytes):
    import time

    decrypt_start = time.time()

    vault_path = get_vault_path()
    with open(vault_path, "rb") as f:
        token = f.read()

    data = decrypt_vault(token, key)
    data = {k.decode('utf-8') if isinstance(k, bytes) else k: v for k, v in data.items()}

    # Track decrypt time
    decrypt_time = (time.time() - decrypt_start) * 1000  # ms
    try:
        from gui.analytics_manager import update_metric
        update_metric("performance.vault_decrypt_time_ms", decrypt_time)
    except:
        pass

    return data


def save_vault(data: dict, key: bytes):
    import time
    save_start = time.time()

    vault_path = get_vault_path()
    token = encrypt_vault(data, key)
    with open(vault_path, "wb") as f:
        f.write(token)

    # Track save performance
    save_time = (time.time() - save_start) * 1000
    print(f"DEBUG: Save took {save_time:.3f}ms")

    try:
        from gui.analytics_manager import update_metric
        update_metric("performance.avg_save_time_ms", save_time)
        print(f"DEBUG: Updated avg_save_time_ms to {save_time}")
    except Exception as e:
        print(f"DEBUG: Analytics save failed: {e}")



def is_password_strong(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def handle_first_setup(input_username, input_password, vault_directory=None):

    # Determine paths to use
    if vault_directory:
        auth_path = os.path.join(vault_directory, "auth", "credentials.enc")
        vault_path = os.path.join(vault_directory, "vault.enc")
    else:
        auth_path = get_auth_path()
        vault_path = get_vault_path()

    # Validate paths exist
    if not auth_path or not vault_path:
        return False, "Could not determine vault paths. Please select a vault directory."

    # Create directories if they don't exist
    try:
        auth_dir = os.path.dirname(auth_path)
        if not os.path.exists(auth_dir):
            os.makedirs(auth_dir, exist_ok=True)

        vault_dir = os.path.dirname(vault_path)
        if not os.path.exists(vault_dir):
            os.makedirs(vault_dir, exist_ok=True)
    except Exception as e:
        return False, f"Error creating directories: {e}"

    # Validate password strength
    if not is_password_strong(input_password):
        return False, "Password is not strong enough"

    username = input_username
    password = input_password

    try:
        hashed_password = hash_new_password(password)
        vault_salt = base64.b64encode(os.urandom(16)).decode('utf-8')

        # Recovery key setup
        recovery_key = generate_recovery_key()
        recovery_salt = os.urandom(16)
        recovery_hash = derive_recovery_key_hash(recovery_key, recovery_salt)

        encrypted_password = encrypt_password_with_recovery_key(password, recovery_key)

        # Write auth file with encrypted password
        with open(auth_path, 'w') as f:
            json.dump({
                "username": username,
                "password": hashed_password.decode('utf-8'),
                "vault_salt": vault_salt,
                "recovery_salt": base64.b64encode(recovery_salt).decode('utf-8'),
                "recovery_hash": recovery_hash,
                "encrypted_password": encrypted_password
            }, f, indent=2)

        # Create and encrypt empty vault
        key = derive_key(password, base64.b64decode(vault_salt))
        empty_vault = {}
        encrypted_vault = encrypt_vault(empty_vault, key)

        # Write vault file
        with open(vault_path, 'wb') as f:
            f.write(encrypted_vault)

        print("Encrypted vault initialized")
        print("Account created successfully. Please restart and log in.")
        return True, recovery_key

    except Exception as e:
        # Clean up partial files if something went wrong
        try:
            if os.path.exists(auth_path):
                os.remove(auth_path)
            if os.path.exists(vault_path):
                os.remove(vault_path)
        except:
            pass

        return False, f"Error creating account: {e}"


def recover_password(input_recovery_key, new_password, confirm_password):

    try:
        # Validate inputs
        if not input_recovery_key or not input_recovery_key.strip():
            return False, "Recovery key cannot be empty.", None

        if not new_password or not confirm_password:
            return False, "Password fields cannot be empty.", None

        if new_password != confirm_password:
            return False, "Passwords do not match.", None

        if not is_password_strong(new_password):
            return False, "Password must be at least 8 characters long and include at least one uppercase letter and one symbol.", None

        # Load auth data
        auth_path = get_auth_path()
        if not os.path.exists(auth_path):
            return False, "Authentication file not found.", None

        with open(auth_path, 'r') as f:
            auth_data = json.load(f)

        # Check if recovery data exists
        if "recovery_salt" not in auth_data or "recovery_hash" not in auth_data:
            return False, "No recovery key found for this vault.", None

        if "encrypted_password" not in auth_data:
            return False, "This vault was created before password recovery was supported.", None

        # Verify recovery key
        recovery_salt = base64.b64decode(auth_data["recovery_salt"])
        stored_hash = auth_data["recovery_hash"]

        if not verify_recovery_key(input_recovery_key.strip().upper(), stored_hash, recovery_salt):
            return False, "Invalid recovery key.", None

        # Recovery key is valid - decrypt the old password
        try:
            old_password = decrypt_password_with_recovery_key(auth_data["encrypted_password"],
                                                              input_recovery_key.strip().upper())
        except ValueError as e:
            return False, f"Failed to decrypt stored password: {str(e)}", None

        # Hash new password
        new_hashed = hash_new_password(new_password)
        auth_data["password"] = new_hashed.decode('utf-8')

        # Generate new recovery key
        new_recovery_key = generate_recovery_key()
        new_recovery_salt = os.urandom(16)
        new_recovery_hash = derive_recovery_key_hash(new_recovery_key, new_recovery_salt)

        # Encrypt new password with new recovery key
        new_encrypted_password = encrypt_password_with_recovery_key(new_password, new_recovery_key)

        # Update auth data
        auth_data["recovery_salt"] = base64.b64encode(new_recovery_salt).decode('utf-8')
        auth_data["recovery_hash"] = new_recovery_hash
        auth_data["encrypted_password"] = new_encrypted_password

        # Save updated auth data
        with open(auth_path, 'w') as f:
            json.dump(auth_data, f)

        # Re-encrypt vault with new password
        vault_path = get_vault_path()
        if os.path.exists(vault_path):
            try:
                # Read encrypted vault data
                with open(vault_path, 'rb') as f:
                    encrypted_vault_data = f.read()

                # Decrypt vault with old password
                vault_salt = base64.b64decode(auth_data["vault_salt"])
                old_vault_key = derive_key(old_password, vault_salt)
                vault_data = decrypt_vault(encrypted_vault_data, old_vault_key)

                # Re-encrypt vault with new password
                new_vault_key = derive_key(new_password, vault_salt)
                new_encrypted_vault = encrypt_vault(vault_data, new_vault_key)

                # Save re-encrypted vault
                with open(vault_path, 'wb') as f:
                    f.write(new_encrypted_vault)

            except Exception as e:
                return False, f"Password reset successful but vault re-encryption failed: {str(e)}", None

        return True, "Password reset successful. Your vault data has been preserved. Please save your new recovery key.", new_recovery_key

    except FileNotFoundError:
        return False, "Authentication file not found.", None
    except json.JSONDecodeError:
        return False, "Authentication file is corrupted.", None
    except Exception as e:
        return False, f"An error occurred during recovery: {str(e)}", None


def user_verification(input_username, input_password):
    if DEV_MODE_ACTIVE:
        return get_mock_credentials
    auth_path = get_auth_path()

    try:
        with open(auth_path, 'r') as f:
            auth_data = json.load(f)
    except FileNotFoundError:
        print(f"Auth file not found at: {auth_path}")
        return None, None

    stored_username = auth_data.get("username")
    stored_hashed_password = auth_data.get("password")

    if verify_login(input_password, stored_hashed_password, input_username, stored_username):
        print("Login successful.")
        vault_salt = base64.b64decode(auth_data["vault_salt"])
        key = derive_key(input_password, vault_salt)
        return key, stored_username

    print("Login failed.")
    return None, None



def add_folder(key: bytes, new_folder_name, new_folder_fields):
    data = load_vault(key)

    if new_folder_name in data:
        return

    else:
        # Handle both string and list inputs
        if isinstance(new_folder_fields, list):
            schema = new_folder_fields
        else:
            schema = [field.strip() for field in new_folder_fields.split(",")]

        data[new_folder_name] = {
            "schema": schema,
            "entries": []
        }

        save_vault(data, key)
