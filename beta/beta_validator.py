import requests
import json
from datetime import datetime


class BetaKeyValidator:
    def __init__(self):
        # Oracle server URL
        self.api_base = "http://141.148.36.8"

    def is_beta_active(self):
        """Toggle beta requirement - set False when beta ends"""
        return True

    def validate_and_activate_key(self, beta_key, username):
        """Validate beta key with Oracle server"""
        if not self.is_beta_active():
            return True, "", ""

        if not beta_key or not beta_key.strip():
            return False, "Beta access key is required", ""

        try:
            # Send validation request to Oracle server
            response = requests.post(
                f"{self.api_base}/validate_key",
                json={
                    "beta_key": beta_key.strip(),
                    "username": username
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data["valid"]:
                    print(f"✅ Beta key validated by Oracle server")
                    return True, "", beta_key.strip().upper()
                else:
                    return False, data["message"], ""
            else:
                return False, "Beta validation service error", ""

        except requests.exceptions.RequestException as e:
            print(f"❌ Oracle server connection failed: {e}")
            return False, "Beta validation service unavailable", ""
        except Exception as e:
            print(f"❌ Beta validation error: {e}")
            return False, "Beta validation failed", ""

    def save_beta_key_to_auth(self, auth_path, beta_key):
        """Save beta key to user's auth file"""
        if not self.is_beta_active() or not beta_key:
            return

        try:
            with open(auth_path, 'r') as f:
                auth_data = json.load(f)

            auth_data['beta_key'] = beta_key

            with open(auth_path, 'w') as f:
                json.dump(auth_data, f, indent=2)

            print(f"✅ Beta key saved to auth file")

        except Exception as e:
            print(f"❌ Failed to save beta key: {e}")

    def check_beta_access_on_login(self, username):
        """Check beta access on login - simplified for Oracle"""
        if not self.is_beta_active():
            return True, ""

        try:
            from config import get_auth_path
            import os

            auth_path = get_auth_path()
            if not os.path.exists(auth_path):
                return True, ""  # No auth file = grandfathered

            with open(auth_path, 'r') as f:
                auth_data = json.load(f)

            beta_key = auth_data.get('beta_key')
            if not beta_key:
                return True, ""  # No beta key = grandfathered

            # Quick validation with Oracle server
            response = requests.post(
                f"{self.api_base}/validate_key",
                json={"beta_key": beta_key, "username": username},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if not data["valid"] and "revoked" in data["message"]:
                    return False, "Beta access has been revoked"

            return True, ""  # Allow login on errors

        except Exception as e:
            print(f"❌ Beta check failed: {e}")
            return True, ""  # Don't block on errors