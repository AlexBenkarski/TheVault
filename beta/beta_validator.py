from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os


class BetaKeyValidator:
    def __init__(self):
        self.db = None
        self._init_firebase()

    def _init_firebase(self):
        """Initialize Firebase - reuse existing connection if available"""
        try:
            if firebase_admin._apps:
                self.db = firestore.client()
                return

            # Get Firebase config
            from secrets_encryption import get_firebase_credentials
            firebase_config = get_firebase_credentials()

            if firebase_config:
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                print("✅ Beta validator connected to Firebase")
            else:
                print("❌ Firebase credentials not available for beta validation")

        except Exception as e:
            print(f"❌ Beta Firebase init failed: {e}")

    def is_beta_active(self):
        """Toggle beta requirement here - set to False when beta ends"""
        return True

    def validate_and_activate_key(self, beta_key, username):
        if not self.is_beta_active():
            return True, "", ""  # Beta disabled, allow signup

        if not beta_key or not beta_key.strip():
            return False, "Beta access key is required", ""

        if not self.db:
            return False, "Beta validation service unavailable", ""

        try:
            # Normalize key format
            key = beta_key.strip().upper().replace(" ", "-")

            # Check if key exists in unused_keys
            unused_ref = self.db.collection('unused_keys').document(key)
            unused_doc = unused_ref.get()

            if not unused_doc.exists:
                return False, "Invalid or already used beta key", ""

            # Get original key data
            key_data = unused_doc.to_dict()

            # Add activation info
            key_data.update({
                'used_at': datetime.now().isoformat(),
                'username': username,
                'status': 'used'
            })

            # Move to activated_keys collection
            self.db.collection('activated_keys').document(key).set(key_data)

            # Remove from unused_keys
            unused_ref.delete()

            print(f"✅ Beta key {key} activated for {username}")
            return True, "", key  # Return the key to save in auth file

        except Exception as e:
            print(f"❌ Beta key activation failed: {e}")
            return False, "Beta validation failed - try again", ""

    def save_beta_key_to_auth(self, auth_path, beta_key):
        """Save beta key to user's auth file"""
        if not self.is_beta_active() or not beta_key:
            return

        try:
            # Read existing auth data
            with open(auth_path, 'r') as f:
                auth_data = json.load(f)

            # Add beta key
            auth_data['beta_key'] = beta_key

            # Write back to file
            with open(auth_path, 'w') as f:
                json.dump(auth_data, f, indent=2)

            print(f"✅ Beta key saved to auth file")

        except Exception as e:
            print(f"❌ Failed to save beta key to auth: {e}")

    def check_beta_access_on_login(self, username):
        if not self.is_beta_active():
            return True, ""  # Beta disabled, allow all logins

        try:
            from config import get_auth_path
            auth_path = get_auth_path()

            if not os.path.exists(auth_path):
                return True, ""  # No auth file = not a beta user

            # Read auth file
            with open(auth_path, 'r') as f:
                auth_data = json.load(f)

            # Check if this is a beta user
            beta_key = auth_data.get('beta_key')
            if not beta_key:
                return True, ""  # No beta key = grandfathered user, allow login

            # Check key status in Firebase
            if not self.db:
                print("❌ Firebase unavailable for beta check - allowing login")
                return True, ""  # Don't block login if Firebase is down

            # Check if key is still valid (not revoked)
            activated_ref = self.db.collection('activated_keys').document(beta_key)
            activated_doc = activated_ref.get()

            if not activated_doc.exists:
                # Key doesn't exist in activated_keys - might be revoked
                revoked_ref = self.db.collection('revoked_keys').document(beta_key)
                if revoked_ref.get().exists:
                    return False, "Beta access has been revoked"
                else:
                    # Key missing entirely - something went wrong
                    print(f"❌ Beta key {beta_key} not found in any collection")
                    return True, ""  # Allow login rather than block

            # Check if key is marked as revoked in activated_keys
            key_data = activated_doc.to_dict()
            if key_data.get('status') == 'revoked':
                return False, "Beta access has been revoked"

            # Key is valid and active
            return True, ""

        except Exception as e:
            print(f"❌ Beta access check failed: {e}")
            return True, ""  # Don't block login on errors