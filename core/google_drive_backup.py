# core/google_drive_backup.py
"""
Google Drive backup manager for vault files
Uses OAuth 2.0 for secure authentication
"""

import os
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any


class GoogleDriveBackup:
    """Manages Google Drive backups with OAuth authentication"""

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None

        # Load user tokens if they exist
        self._load_credentials()

    @property
    def client_id(self):
        """Get client ID (app-level credential)"""
        client_id, _ = self._get_client_credentials()
        return client_id

    @property
    def client_secret(self):
        """Get client secret (app-level credential)"""
        _, client_secret = self._get_client_credentials()
        return client_secret

    def _load_credentials(self):
        """Load stored OAuth credentials"""
        try:
            # Load tokens from user config (user-specific)
            from core.vault_manager import get_app_directory
            config_path = os.path.join(get_app_directory(), "gdrive_tokens.json")

            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    tokens = json.load(f)
                    self.access_token = tokens.get("access_token")
                    self.refresh_token = tokens.get("refresh_token")

                    # Parse expiry time
                    expires_str = tokens.get("expires_at")
                    if expires_str:
                        self.token_expires = datetime.fromisoformat(expires_str)

        except Exception as e:
            print(f"Error loading Google Drive credentials: {e}")

    def _get_client_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """Get OAuth client credentials - these are app-level, not user-specific"""
        # These are Vault's Google API credentials (same for all users)

        # Load from your secrets.json (recommended approach)
        try:
            from gui.update_manager import CACHED_SECRETS
            if CACHED_SECRETS and "google_drive" in CACHED_SECRETS:
                creds = CACHED_SECRETS["google_drive"]
                client_id = creds.get("client_id")
                client_secret = creds.get("client_secret")

                if client_id and client_secret:
                    return client_id, client_secret
        except:
            pass

        # Fallback for development (replace with your actual credentials)
        print("Warning: Google Drive credentials not found in secrets.json")
        return None, None

    def _save_tokens(self):
        """Save OAuth tokens to file"""
        try:
            from core.vault_manager import get_app_directory
            config_path = os.path.join(get_app_directory(), "gdrive_tokens.json")

            tokens = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expires_at": self.token_expires.isoformat() if self.token_expires else None
            }

            with open(config_path, 'w') as f:
                json.dump(tokens, f, indent=2)

        except Exception as e:
            print(f"Error saving Google Drive tokens: {e}")

    def is_authenticated(self) -> bool:
        """Check if we have valid authentication"""
        if not self.access_token or not self.refresh_token:
            return False

        # Check if token is expired
        if self.token_expires and datetime.now() >= self.token_expires:
            return self._refresh_access_token()

        return True

    def get_auth_url(self, port: int = 8080) -> Optional[str]:
        """Get OAuth authorization URL"""
        if not self.client_id:
            return None

        import urllib.parse

        params = {
            "client_id": self.client_id,
            "redirect_uri": f"http://localhost:{port}/oauth/callback",
            "scope": "https://www.googleapis.com/auth/drive.file",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }

        auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)
        return auth_url

    def run_oauth_flow(self, port: int = 8080) -> bool:
        """Run complete OAuth flow with callback server"""
        try:
            import webbrowser
            import socket
            import threading
            import urllib.parse
            from http.server import HTTPServer, BaseHTTPRequestHandler

            auth_url = self.get_auth_url(port)
            if not auth_url:
                return False

            # Simple callback handler
            class CallbackHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    parsed_url = urllib.parse.urlparse(self.path)
                    query_params = urllib.parse.parse_qs(parsed_url.query)

                    if 'code' in query_params:
                        self.server.auth_code = query_params['code'][0]
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        success_html = """
                        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h2 style="color: #4CAF50;">✓ Authorization Successful!</h2>
                        <p>You can now close this window and return to Vault.</p>
                        </body></html>
                        """
                        self.wfile.write(success_html.encode())
                    else:
                        self.send_response(400)
                        self.end_headers()

                def log_message(self, format, *args):
                    pass  # Suppress logs

            # Check if port is available
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
            except OSError:
                print(f"Port {port} is in use")
                return False

            # Start server
            server = HTTPServer(('localhost', port), CallbackHandler)
            server.auth_code = None

            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()

            # Open browser
            print(f"Opening browser to: {auth_url}")
            webbrowser.open(auth_url)

            # Wait for callback (max 2 minutes)
            import time
            timeout = 120
            start_time = time.time()

            while time.time() - start_time < timeout:
                if hasattr(server, 'auth_code') and server.auth_code:
                    auth_code = server.auth_code
                    server.shutdown()
                    server.server_close()

                    # Exchange code for tokens
                    return self.exchange_code_for_tokens(auth_code, port)

                time.sleep(0.1)

            # Timeout
            server.shutdown()
            server.server_close()
            print("OAuth flow timed out")
            return False

        except Exception as e:
            print(f"OAuth flow error: {e}")
            return False

    def exchange_code_for_tokens(self, auth_code: str, port: int = 8080) -> bool:
        """Exchange authorization code for access/refresh tokens"""
        try:
            import requests

            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": auth_code,
                "grant_type": "authorization_code",
                "redirect_uri": f"http://localhost:{port}/oauth/callback"
            }

            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens["access_token"]
                self.refresh_token = tokens["refresh_token"]

                # Calculate expiry time
                expires_in = tokens.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)

                self._save_tokens()
                return True

        except Exception as e:
            print(f"Error exchanging authorization code: {e}")

        return False

    def _refresh_access_token(self) -> bool:
        """Refresh expired access token"""
        try:
            import requests

            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }

            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data=data,
                timeout=10
            )

            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens["access_token"]

                # Update expiry time
                expires_in = tokens.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)

                self._save_tokens()
                return True

        except Exception as e:
            print(f"Error refreshing access token: {e}")

        return False

    def upload_vault_backup(self, vault_path: str) -> Tuple[bool, str]:
        """Upload vault file to Google Drive"""
        if not self.is_authenticated():
            return False, "Not authenticated with Google Drive"

        if not os.path.exists(vault_path):
            return False, "Vault file not found"

        try:
            import requests

            # Read vault file
            with open(vault_path, 'rb') as f:
                vault_data = f.read()

            # Prepare metadata
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vault_backup_{timestamp}.enc"

            metadata = {
                "name": filename,
                "parents": [self._get_or_create_vault_folder()]
            }

            # Upload file
            files = {
                'data': ('metadata', json.dumps(metadata), 'application/json; charset=UTF-8'),
                'file': (filename, vault_data, 'application/octet-stream')
            }

            headers = {"Authorization": f"Bearer {self.access_token}"}

            response = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                headers=headers,
                files=files,
                timeout=30
            )

            if response.status_code == 200:
                # Update last backup time
                self._update_last_backup_time()
                return True, f"Backup uploaded successfully as {filename}"
            else:
                return False, f"Upload failed: {response.status_code}"

        except Exception as e:
            return False, f"Upload error: {str(e)}"

    def _get_or_create_vault_folder(self) -> str:
        """Get or create the Vault Backups folder in Google Drive"""
        try:
            import requests

            headers = {"Authorization": f"Bearer {self.access_token}"}

            # Search for existing folder
            search_params = {
                "q": "name='Vault Backups' and mimeType='application/vnd.google-apps.folder'",
                "fields": "files(id, name)"
            }

            response = requests.get(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                params=search_params,
                timeout=10
            )

            if response.status_code == 200:
                files = response.json().get("files", [])
                if files:
                    return files[0]["id"]

            # Create new folder
            folder_metadata = {
                "name": "Vault Backups",
                "mimeType": "application/vnd.google-apps.folder"
            }

            response = requests.post(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                json=folder_metadata,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()["id"]

        except Exception as e:
            print(f"Error managing vault folder: {e}")

        return "root"  # Fallback to root folder

    def get_backup_status(self) -> Dict[str, Any]:
        """Get current backup status information"""
        status = {
            "connected": self.is_authenticated(),
            "last_backup": self._get_last_backup_time(),
            "backup_count": 0,
            "error": None
        }

        if status["connected"]:
            try:
                status["backup_count"] = self._get_backup_count()
            except Exception as e:
                status["error"] = str(e)

        return status

    def _get_backup_count(self) -> int:
        """Get number of backup files in Google Drive"""
        try:
            import requests

            headers = {"Authorization": f"Bearer {self.access_token}"}
            folder_id = self._get_or_create_vault_folder()

            search_params = {
                "q": f"'{folder_id}' in parents and name contains 'vault_backup_'",
                "fields": "files(id)"
            }

            response = requests.get(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                params=search_params,
                timeout=10
            )

            if response.status_code == 200:
                return len(response.json().get("files", []))

        except Exception as e:
            print(f"Error getting backup count: {e}")

        return 0

    def _update_last_backup_time(self):
        """Update the last backup timestamp"""
        try:
            timestamp_file = os.path.join(self._get_app_directory(), "last_gdrive_backup.txt")

            with open(timestamp_file, 'w') as f:
                f.write(datetime.now().isoformat())

        except Exception as e:
            print(f"Error updating backup timestamp: {e}")

    def _get_last_backup_time(self) -> Optional[str]:
        """Get the last backup timestamp"""
        try:
            timestamp_file = os.path.join(self._get_app_directory(), "last_gdrive_backup.txt")

            if os.path.exists(timestamp_file):
                with open(timestamp_file, 'r') as f:
                    timestamp_str = f.read().strip()
                    timestamp = datetime.fromisoformat(timestamp_str)
                    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

        except Exception as e:
            print(f"Error reading backup timestamp: {e}")

        return None

    def disconnect(self):
        """Remove stored authentication"""
        try:
            config_path = os.path.join(self._get_app_directory(), "gdrive_tokens.json")

            if os.path.exists(config_path):
                os.remove(config_path)

            self.access_token = None
            self.refresh_token = None
            self.token_expires = None

        except Exception as e:
            print(f"Error disconnecting Google Drive: {e}")


# Helper function for easy import
def get_google_drive_backup():
    """Get singleton instance of Google Drive backup manager"""
    if not hasattr(get_google_drive_backup, '_instance'):
        get_google_drive_backup._instance = GoogleDriveBackup()
    return get_google_drive_backup._instance