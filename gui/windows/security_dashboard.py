import os
import re
import time
import webbrowser
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QFrame, QScrollArea, QDialog, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
from gui.widgets.modern_widgets import ModernDialog, ModernButton, ModernSmallButton

try:
    from gui.widgets.svg_icons import SvgIcon, Icons  # Note: svg_icons not svg_icon
except ImportError:
    try:
        from gui.widgets.svg_icon import SvgIcon, Icons  # Fallback to your actual module name
    except ImportError:
        # Create dummy classes if neither exists
        class SvgIcon:
            @staticmethod
            def create_icon(*args, **kwargs): return None
        class Icons:
            EYE = "eye"
            EYE_OFF = "eye_off"

# Google Drive API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow, InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from google.auth.transport.requests import Request
    import json

    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    print("Google Drive API not available. Install: pip install google-api-python-client google-auth-oauthlib")


class SecurityDashboard(ModernDialog):
    def __init__(self, vault_data=None, parent=None):
        super().__init__(parent, "Security Dashboard")
        self.vault_data = vault_data
        self.show_passwords = False

        # Google Drive backup settings
        self.google_drive_service = None
        self.google_credentials = None
        self.last_backup_time = None

        self.init_ui()
        self.load_google_drive_credentials()

        # Auto-refresh every 30 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_security_data)
        self.refresh_timer.start(30000)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header section with security score
        self.create_header_section(main_layout)

        # Tab layout
        self.create_tab_sections(main_layout)

    def create_header_section(self, main_layout):
        """Create the header with overall security score"""
        header_layout = QHBoxLayout()

        # Left side - Title and subtitle
        left_layout = QVBoxLayout()

        title = QLabel("Security Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #4CAF50; margin-bottom: 5px;")
        left_layout.addWidget(title)

        subtitle = QLabel("Keep your vault secure with proactive monitoring")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: #888888;")
        left_layout.addWidget(subtitle)

        header_layout.addLayout(left_layout)
        header_layout.addStretch()

        # Right side - Security score
        score_layout = QVBoxLayout()
        score_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.security_score_label = QLabel("85")
        self.security_score_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self.security_score_label.setStyleSheet("color: #4CAF50;")
        self.security_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(self.security_score_label)

        score_label = QLabel("Security Score")
        score_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        score_label.setStyleSheet("color: #ffffff;")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_layout.addWidget(score_label)

        header_layout.addLayout(score_layout)
        main_layout.addLayout(header_layout)

    def create_tab_sections(self, main_layout):
        """Create the 3 vertical tab sections"""
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(15)

        # Tab 1: Password Security
        password_tab = self.create_password_security_tab()
        password_tab.setFixedWidth(400)
        tabs_layout.addWidget(password_tab)

        # Tab 2: Data Breach Detection (placeholder)
        breach_tab = self.create_breach_detection_tab()
        breach_tab.setFixedWidth(400)
        tabs_layout.addWidget(breach_tab)

        # Tab 3: Google Drive Backup
        backup_tab = self.create_backup_tab()
        backup_tab.setFixedWidth(400)
        tabs_layout.addWidget(backup_tab)

        main_layout.addLayout(tabs_layout)

    def create_password_security_tab(self):
        """Create the password security tab with real content"""
        tab_widget = QFrame()
        tab_widget.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.03);
                border: none;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Password Security")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")

        # Global show/hide passwords button
        button_layout = QHBoxLayout()
        self.global_eye_btn = ModernSmallButton(" Show All")
        self.global_eye_btn.setFixedHeight(28)
        self.global_eye_btn.clicked.connect(self.toggle_global_password_visibility)
        self.update_global_eye_button()

        button_layout.addWidget(self.global_eye_btn)
        button_layout.addStretch()

        # Security content
        content_widget = self.create_security_content()

        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addWidget(content_widget)

        return tab_widget

    def create_breach_detection_tab(self):
        """Create breach detection tab (placeholder)"""
        tab_widget = QFrame()
        tab_widget.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.03);
                border: none;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Data Breach Detection")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")

        placeholder = QLabel("Coming Soon!\n\nHaveIBeenPwned integration")
        placeholder.setFont(QFont("Segoe UI", 12))
        placeholder.setStyleSheet("color: #888888;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(placeholder)
        layout.addStretch()

        return tab_widget

    def create_backup_tab(self):
        """Create Google Drive backup tab"""
        tab_widget = QFrame()
        tab_widget.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.03);
                border: none;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Google Drive Backup")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")

        # Backup status section
        status_widget = self.create_backup_status_widget()

        # Backup settings section
        settings_widget = self.create_backup_settings_widget()

        # Action buttons
        actions_widget = self.create_backup_actions_widget()

        layout.addWidget(title)
        layout.addWidget(status_widget)
        layout.addWidget(settings_widget)
        layout.addWidget(actions_widget)
        layout.addStretch()

        return tab_widget

    def create_backup_status_widget(self):
        """Create backup status display"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: rgba(76, 175, 80, 0.08);
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # Google Drive connection status
        self.gdrive_status_label = QLabel("🔍 Checking Google Drive connection...")
        self.gdrive_status_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.gdrive_status_label.setStyleSheet("color: #ffffff; background: transparent;")

        # Vault backup info
        self.vault_backup_label = QLabel("Vault backup status: Checking...")
        self.vault_backup_label.setFont(QFont("Segoe UI", 10))
        self.vault_backup_label.setStyleSheet("color: #888888; background: transparent;")

        # Last backup time
        self.last_backup_label = QLabel("Last backup: Unknown")
        self.last_backup_label.setFont(QFont("Segoe UI", 10))
        self.last_backup_label.setStyleSheet("color: #888888; background: transparent;")

        layout.addWidget(self.gdrive_status_label)
        layout.addWidget(self.vault_backup_label)
        layout.addWidget(self.last_backup_label)

        return widget

    def create_backup_settings_widget(self):
        """Create backup settings controls"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        settings_title = QLabel("Backup Settings")
        settings_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        settings_title.setStyleSheet("color: #ffffff; background: transparent;")

        # Google Drive backup status
        backup_status_widget = QWidget()
        backup_status_layout = QHBoxLayout(backup_status_widget)
        backup_status_layout.setContentsMargins(0, 0, 0, 0)

        backup_status_label = QLabel("Auto-backup on save")
        backup_status_label.setFont(QFont("Segoe UI", 10))
        backup_status_label.setStyleSheet("color: #ffffff; background: transparent;")

        self.backup_status_indicator = QLabel("Unknown")
        self.backup_status_indicator.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.backup_status_indicator.setStyleSheet("color: #ffaa00; background: transparent;")

        backup_status_layout.addWidget(backup_status_label)
        backup_status_layout.addStretch()
        backup_status_layout.addWidget(self.backup_status_indicator)

        # Premium feature info
        premium_info = QLabel(
            "Premium Feature: Your vault is automatically backed up to Google Drive after every save. Zero-knowledge encryption keeps your data private.")
        premium_info.setFont(QFont("Segoe UI", 9))
        premium_info.setStyleSheet("color: #888888; background: transparent;")
        premium_info.setWordWrap(True)

        layout.addWidget(settings_title)
        layout.addWidget(backup_status_widget)
        layout.addWidget(premium_info)

        return widget

    def create_backup_actions_widget(self):
        """Create backup action buttons"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        if not GOOGLE_DRIVE_AVAILABLE:
            # Show API not available message
            error_label = QLabel(
                "⚠️ Google Drive API not installed\nInstall: pip install google-api-python-client google-auth-oauthlib")
            error_label.setStyleSheet("color: #ff9500; background: transparent;")
            error_label.setWordWrap(True)
            layout.addWidget(error_label)
            return widget

        # Setup Google Drive button (if not connected)
        self.setup_gdrive_btn = ModernButton("Connect Google Drive")
        self.setup_gdrive_btn.setFixedHeight(36)
        self.setup_gdrive_btn.clicked.connect(self.setup_google_drive_backup)

        # Backup now button
        self.backup_now_btn = ModernButton("Backup Now")
        self.backup_now_btn.setFixedHeight(36)
        self.backup_now_btn.clicked.connect(self.manual_backup_to_gdrive)

        # Check backup status button
        self.check_backup_btn = ModernButton("Check Backup Status")
        self.check_backup_btn.setFixedHeight(36)
        self.check_backup_btn.clicked.connect(self.check_backup_status)

        # View backups button
        self.view_backups_btn = ModernButton("View Backup History")
        self.view_backups_btn.setFixedHeight(36)
        self.view_backups_btn.clicked.connect(self.view_backup_history)

        layout.addWidget(self.setup_gdrive_btn)
        layout.addWidget(self.backup_now_btn)
        layout.addWidget(self.check_backup_btn)
        layout.addWidget(self.view_backups_btn)

        return widget

    # Google Drive Integration Methods

    def load_google_drive_credentials(self):
        """Load saved Google Drive credentials"""
        try:
            creds_file = os.path.join(os.path.expanduser("~"), ".vault", "gdrive_creds.json")
            if os.path.exists(creds_file):
                self.google_credentials = Credentials.from_authorized_user_file(creds_file)

                # Refresh credentials if needed
                if self.google_credentials.expired and self.google_credentials.refresh_token:
                    self.google_credentials.refresh(Request())
                    self.save_google_drive_credentials()

                # Build service
                if self.google_credentials.valid:
                    self.google_drive_service = build('drive', 'v3', credentials=self.google_credentials)
                    print("✅ Google Drive credentials loaded successfully")

            self.update_backup_status()

        except Exception as e:
            print(f"Error loading Google Drive credentials: {e}")
            self.google_credentials = None
            self.google_drive_service = None
            self.update_backup_status()

    def save_google_drive_credentials(self):
        """Save Google Drive credentials securely"""
        try:
            creds_dir = os.path.join(os.path.expanduser("~"), ".vault")
            os.makedirs(creds_dir, exist_ok=True)

            creds_file = os.path.join(creds_dir, "gdrive_creds.json")
            with open(creds_file, 'w') as f:
                f.write(self.google_credentials.to_json())

            print("✅ Google Drive credentials saved")

        except Exception as e:
            print(f"Error saving Google Drive credentials: {e}")

    def setup_google_drive_backup(self):
        """Setup Google Drive backup with OAuth"""
        if not GOOGLE_DRIVE_AVAILABLE:
            QMessageBox.warning(self, "API Not Available",
                                "Google Drive API not installed.\n\nInstall with:\npip install google-api-python-client google-auth-oauthlib")
            return

        try:
            # Google OAuth configuration for Vault
            CLIENT_CONFIG = {
                "installed": {
                    "client_id": "your-vault-client-id.apps.googleusercontent.com",
                    "client_secret": "your-client-secret",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:8080"]
                }
            }

            SCOPES = ['https://www.googleapis.com/auth/drive.file']

            # Create OAuth flow
            flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)

            # Show setup dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Connect Google Drive")
            dialog.setFixedSize(500, 300)

            layout = QVBoxLayout(dialog)

            title = QLabel("🔒 Premium Backup Protection")
            title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            description = QLabel(
                "Automatically backup your vault to Google Drive after every save.\n\n"
                "✅ Your vault stays encrypted - Google can't see your passwords\n"
                "✅ Automatic versioning and backup history\n"
                "✅ Works on any device with your Google account\n"
                "✅ Immediate backup confirmation\n\n"
                "Click 'Authorize' to open Google's permission page in your browser."
            )
            description.setWordWrap(True)
            description.setStyleSheet("color: #888888;")

            button_layout = QHBoxLayout()

            auth_btn = ModernButton("Authorize Google Drive")
            auth_btn.clicked.connect(lambda: self.complete_oauth_flow(flow, dialog))

            cancel_btn = ModernButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)

            button_layout.addWidget(cancel_btn)
            button_layout.addWidget(auth_btn)

            layout.addWidget(title)
            layout.addWidget(description)
            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Setup Error", f"Failed to setup Google Drive backup:\n{str(e)}")

    def complete_oauth_flow(self, flow, dialog):
        """Complete OAuth flow and save credentials"""
        try:
            # Run local server to handle OAuth callback
            self.google_credentials = flow.run_local_server(port=8080)

            # Save credentials
            self.save_google_drive_credentials()

            # Build service
            self.google_drive_service = build('drive', 'v3', credentials=self.google_credentials)

            # Create Vault folder in Google Drive
            self.create_vault_folder()

            dialog.accept()

            # Update UI
            self.update_backup_status()

            QMessageBox.information(self, "Success",
                                    "✅ Google Drive backup enabled!\n\n"
                                    "Your vault will now be automatically backed up after every save.")

        except Exception as e:
            QMessageBox.critical(self, "Authorization Error",
                                 f"Failed to authorize Google Drive:\n{str(e)}")

    def create_vault_folder(self):
        """Create Vault folder in Google Drive (tries both 'Vault' and 'TheVault')"""
        try:
            if not self.google_drive_service:
                return None

            # Check if 'Vault' folder exists first (new name)
            query = "name='Vault' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.google_drive_service.files().list(q=query).execute()

            if results.get('files'):
                folder_id = results['files'][0]['id']
                print(f"✅ Vault folder found: {folder_id}")
                return folder_id

            # Check if 'TheVault' folder exists (legacy name)
            query = "name='TheVault' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.google_drive_service.files().list(q=query).execute()

            if results.get('files'):
                folder_id = results['files'][0]['id']
                print(f"✅ TheVault folder found (legacy): {folder_id}")
                return folder_id

            # Create new 'Vault' folder
            folder_metadata = {
                'name': 'Vault',
                'mimeType': 'application/vnd.google-apps.folder'
            }

            folder = self.google_drive_service.files().create(body=folder_metadata).execute()
            folder_id = folder.get('id')

            print(f"✅ Vault folder created: {folder_id}")
            return folder_id

        except Exception as e:
            print(f"Error creating Vault folder: {e}")
            return None

    def backup_vault_to_google_drive(self, vault_file_path):
        """Backup vault file to Google Drive"""
        try:
            if not self.google_drive_service:
                return {"success": False, "message": "Google Drive not connected"}

            if not os.path.exists(vault_file_path):
                return {"success": False, "message": "Vault file not found"}

            print(f"Starting Google Drive backup: {vault_file_path}")

            # Get or create Vault folder
            folder_id = self.create_vault_folder()
            if not folder_id:
                return {"success": False, "message": "Failed to access Google Drive folder"}

            # Check if vault.enc already exists
            query = f"name='vault.enc' and parents in '{folder_id}' and trashed=false"
            results = self.google_drive_service.files().list(q=query).execute()

            # Prepare upload
            media = MediaFileUpload(vault_file_path, resumable=True)

            if results.get('files'):
                # Update existing file
                file_id = results['files'][0]['id']
                updated_file = self.google_drive_service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()

                status_message = "✅ Vault updated in Google Drive"
                print(f"✅ Vault updated: {updated_file.get('id')}")

            else:
                # Create new file
                file_metadata = {
                    'name': 'vault.enc',
                    'parents': [folder_id]
                }

                created_file = self.google_drive_service.files().create(
                    body=file_metadata,
                    media_body=media
                ).execute()

                status_message = "✅ Vault backed up to Google Drive"
                print(f"✅ Vault created: {created_file.get('id')}")

            # Update backup time
            self.last_backup_time = datetime.now()
            self.update_backup_status()

            return {"success": True, "message": status_message}

        except Exception as e:
            error_msg = f"Google Drive backup failed: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg}

    def manual_backup_to_gdrive(self):
        """Manual backup trigger"""
        try:
            if not self.google_drive_service:
                QMessageBox.warning(self, "Not Connected",
                                    "Google Drive not connected. Click 'Connect Google Drive' first.")
                return

            # Get vault file path
            vault_path = self.get_vault_file_path()
            if not vault_path:
                QMessageBox.warning(self, "Vault Not Found",
                                    "Cannot find vault file to backup.")
                return

            # Show progress
            self.show_backup_progress("🔄 Backing up to Google Drive...")

            # Perform backup
            result = self.backup_vault_to_google_drive(vault_path)

            if result["success"]:
                QMessageBox.information(self, "Backup Success", result["message"])
            else:
                QMessageBox.critical(self, "Backup Failed", result["message"])

        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Backup failed:\n{str(e)}")

    def check_backup_status(self):
        """Check current backup status"""
        print("Checking Google Drive backup status...")
        self.update_backup_status()

    def view_backup_history(self):
        """Show backup history from Google Drive"""
        try:
            if not self.google_drive_service:
                QMessageBox.warning(self, "Not Connected",
                                    "Google Drive not connected.")
                return

            # Get Vault folder
            folder_id = self.create_vault_folder()
            if not folder_id:
                QMessageBox.warning(self, "Folder Not Found",
                                    "Vault folder not found in Google Drive.")
                return

            # Get file revisions
            query = f"name='vault.enc' and parents in '{folder_id}' and trashed=false"
            results = self.google_drive_service.files().list(q=query).execute()

            if not results.get('files'):
                QMessageBox.information(self, "No Backups",
                                        "No vault backups found in Google Drive.")
                return

            file_id = results['files'][0]['id']

            # Get revision history
            revisions = self.google_drive_service.revisions().list(fileId=file_id).execute()

            # Show history dialog
            self.show_backup_history_dialog(revisions.get('revisions', []))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get backup history:\n{str(e)}")

    def show_backup_history_dialog(self, revisions):
        """Show backup history in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Backup History")
        dialog.setFixedSize(600, 400)

        layout = QVBoxLayout(dialog)

        title = QLabel("📁 Google Drive Backup History")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))

        history_text = QTextEdit()
        history_text.setReadOnly(True)

        history_content = ""
        for i, revision in enumerate(reversed(revisions)):
            modified_time = revision.get('modifiedTime', 'Unknown')
            try:
                # Parse ISO timestamp
                dt = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = modified_time

            history_content += f"Version {len(revisions) - i}: {time_str}\n"

        history_text.setPlainText(history_content)

        close_btn = ModernButton("Close")
        close_btn.clicked.connect(dialog.accept)

        layout.addWidget(title)
        layout.addWidget(history_text)
        layout.addWidget(close_btn)

        dialog.exec()

    def update_backup_status(self):
        """Update Google Drive backup status display"""
        try:
            print("Updating Google Drive backup status...")

            if not GOOGLE_DRIVE_AVAILABLE:
                self.gdrive_status_label.setText("❌ Google Drive API not installed")
                self.gdrive_status_label.setStyleSheet("color: #ff4757; background: transparent;")
                self.vault_backup_label.setText("Install Google Drive API to enable backups")
                self.last_backup_label.setText("API installation required")
                self.backup_status_indicator.setText("❌ Not Available")
                self.backup_status_indicator.setStyleSheet("color: #ff4757; background: transparent;")

                # Update buttons
                self.setup_gdrive_btn.setEnabled(False)
                self.backup_now_btn.setEnabled(False)
                return

            if not self.google_drive_service or not self.google_credentials:
                self.gdrive_status_label.setText("⚠️ Google Drive not connected")
                self.gdrive_status_label.setStyleSheet("color: #ff9500; background: transparent;")
                self.vault_backup_label.setText("Connect Google Drive to enable automatic backups")
                self.last_backup_label.setText("No backup protection")
                self.backup_status_indicator.setText("❌ Not Connected")
                self.backup_status_indicator.setStyleSheet("color: #ff4757; background: transparent;")

                # Update buttons
                self.setup_gdrive_btn.setVisible(True)
                self.backup_now_btn.setEnabled(False)
                return

            # Google Drive connected - check backup status
            self.gdrive_status_label.setText("✅ Google Drive connected")
            self.gdrive_status_label.setStyleSheet("color: #4CAF50; background: transparent;")

            # Check if vault file exists in Google Drive
            folder_id = self.create_vault_folder()
            if folder_id:
                query = f"name='vault.enc' and parents in '{folder_id}' and trashed=false"
                results = self.google_drive_service.files().list(q=query).execute()

                if results.get('files'):
                    file_info = results['files'][0]
                    modified_time = file_info.get('modifiedTime', '')

                    try:
                        # Parse modification time
                        dt = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                        time_ago = datetime.now(dt.tzinfo) - dt

                        if time_ago.total_seconds() < 300:  # 5 minutes
                            status = "✅ Recently backed up"
                            time_str = "Just now"
                            color = "#4CAF50"
                        elif time_ago.total_seconds() < 3600:  # 1 hour
                            status = "✅ Backed up recently"
                            time_str = f"{int(time_ago.total_seconds() // 60)} minutes ago"
                            color = "#4CAF50"
                        elif time_ago.days < 1:
                            status = "✅ Backed up today"
                            time_str = dt.strftime('%H:%M today')
                            color = "#4CAF50"
                        else:
                            status = "⚠️ Backup is outdated"
                            time_str = dt.strftime('%m/%d/%Y')
                            color = "#ff9500"

                    except:
                        status = "✅ Vault found in Google Drive"
                        time_str = "Unknown time"
                        color = "#4CAF50"

                    self.vault_backup_label.setText(status)
                    self.vault_backup_label.setStyleSheet(f"color: {color}; background: transparent;")
                    self.last_backup_label.setText(f"Last backup: {time_str}")
                    self.backup_status_indicator.setText("✅ Protected")
                    self.backup_status_indicator.setStyleSheet("color: #4CAF50; background: transparent;")

                else:
                    self.vault_backup_label.setText("⚠️ No vault backup found")
                    self.vault_backup_label.setStyleSheet("color: #ff9500; background: transparent;")
                    self.last_backup_label.setText("Click 'Backup Now' to create first backup")
                    self.backup_status_indicator.setText("⚠️ No Backup")
                    self.backup_status_indicator.setStyleSheet("color: #ff9500; background: transparent;")

            # Update buttons
            self.setup_gdrive_btn.setVisible(False)
            self.backup_now_btn.setEnabled(True)

            print("Google Drive backup status updated")

        except Exception as e:
            print(f"Error updating backup status: {e}")

            # Safe fallback
            self.gdrive_status_label.setText("❌ Backup status error")
            self.gdrive_status_label.setStyleSheet("color: #ff4757; background: transparent;")
            self.vault_backup_label.setText("Error checking backup status")
            self.last_backup_label.setText("Try reconnecting Google Drive")
            self.backup_status_indicator.setText("Error")
            self.backup_status_indicator.setStyleSheet("color: #ff4757; background: transparent;")

    def show_backup_progress(self, message):
        """Show backup progress temporarily"""
        try:
            original_text = self.gdrive_status_label.text()
            self.gdrive_status_label.setText(message)
            self.gdrive_status_label.setStyleSheet("color: #ff9500; background: transparent;")

            # Restore original text after 5 seconds
            def restore_text():
                self.gdrive_status_label.setText(original_text)
                self.update_backup_status()

            QTimer.singleShot(5000, restore_text)

        except Exception as e:
            print(f"Error showing backup progress: {e}")

    def get_vault_file_path(self):
        """Get the current vault file path"""
        try:
            # Try to get vault path from config
            from config import get_vault_path
            return get_vault_path()
        except:
            # Fallback: look in common locations
            possible_paths = [
                os.path.join(os.path.expanduser("~"), "Documents", "Vault", "vault.enc"),
                os.path.join(os.path.expanduser("~"), "Documents", "TheVault", "vault.enc"),  # Legacy
                os.path.join(os.path.expanduser("~"), "Vault", "vault.enc"),
                os.path.join(os.path.expanduser("~"), "TheVault", "vault.enc"),  # Legacy
                os.path.join(".", "vault.enc"),
                os.path.join("dev_vault_data", "vault.enc")  # Dev environment
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    return path
            return None

    # Password Security Analysis Methods (unchanged from original)

    def create_security_content(self):
        """Create scrollable security analysis content"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(12)

        if self.vault_data:
            self.analyze_and_display_security(content_layout)
        else:
            self.show_no_vault_message(content_layout)

        scroll_area.setWidget(content_widget)
        return scroll_area

    def analyze_and_display_security(self, layout):
        """Analyze vault security and display results"""
        vault_folders = self.vault_data.get("folders", {})

        # Analyze passwords
        weak_passwords = self.analyze_weak_passwords(vault_folders)
        duplicate_passwords = self.analyze_duplicate_passwords(vault_folders)

        # Update security score
        total_passwords = sum(len(folder.get("entries", [])) for folder in vault_folders.values())
        weak_count = len(weak_passwords)
        duplicate_count = len(duplicate_passwords)

        if total_passwords > 0:
            score = max(0, 100 - (weak_count * 10) - (duplicate_count * 15))
        else:
            score = 85

        self.security_score_label.setText(str(score))

        # Color code the score
        if score >= 80:
            color = "#4CAF50"
        elif score >= 60:
            color = "#ff9500"
        else:
            color = "#ff4757"
        self.security_score_label.setStyleSheet(f"color: {color};")

        # Display weak passwords
        if weak_passwords:
            weak_section = self.create_weak_passwords_section(weak_passwords)
            layout.addWidget(weak_section)

        # Display duplicate passwords
        if duplicate_passwords:
            duplicate_section = self.create_duplicate_passwords_section(duplicate_passwords)
            layout.addWidget(duplicate_section)

        # Good security message
        if not weak_passwords and not duplicate_passwords:
            good_security = QLabel("✅ Great job! No security issues found.")
            good_security.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            good_security.setStyleSheet("color: #4CAF50; padding: 20px;")
            good_security.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(good_security)

    def show_no_vault_message(self, layout):
        """Show message when no vault is loaded"""
        message = QLabel("Load a vault to see security analysis")
        message.setFont(QFont("Segoe UI", 12))
        message.setStyleSheet("color: #888888; padding: 40px;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

    def analyze_weak_passwords(self, vault_folders):
        """Analyze and return weak passwords"""
        weak_passwords = []

        for folder_name, folder_data in vault_folders.items():
            entries = folder_data.get("entries", [])
            for entry in entries:
                for field in ['Password', 'password']:
                    if field in entry:
                        password = entry[field]
                        if password and self.is_weak_password(password):
                            account_info = self.get_account_info(entry, folder_name)
                            issues = self.get_password_issues(password)
                            weak_passwords.append({
                                'account': account_info,
                                'password': password,
                                'issues': issues
                            })
                        break

        return weak_passwords

    def analyze_duplicate_passwords(self, vault_folders):
        """Analyze and return duplicate passwords with account lists"""
        password_usage = {}

        # Collect all passwords and their usage
        for folder_name, folder_data in vault_folders.items():
            entries = folder_data.get("entries", [])
            for entry in entries:
                for field in ['Password', 'password']:
                    if field in entry:
                        password = entry[field]
                        if password:
                            account_info = self.get_account_info(entry, folder_name)
                            if password not in password_usage:
                                password_usage[password] = []
                            password_usage[password].append(account_info)
                        break

        # Filter duplicates
        duplicates = []
        for password, accounts in password_usage.items():
            if len(accounts) > 1:
                duplicates.append({
                    'password': password,
                    'accounts': accounts
                })

        return duplicates

    def is_weak_password(self, password):
        """Check if password is weak"""
        if len(password) < 8:
            return True

        # Check for common patterns
        import re
        if not re.search(r"[A-Z]", password):
            return True
        if not re.search(r"[a-z]", password):
            return True
        if not re.search(r"\d", password):
            return True
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return True

        return False

    def get_password_issues(self, password):
        """Get list of issues with a password"""
        issues = []

        if len(password) < 8:
            issues.append("Less than 8 characters")

        import re
        if not re.search(r"[A-Z]", password):
            issues.append("No uppercase letters")

        if not re.search(r"[a-z]", password):
            issues.append("No lowercase letters")

        if not re.search(r"\d", password):
            issues.append("No numbers")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            issues.append("No special characters")

        return issues

    def get_account_info(self, entry, folder_name):
        """Get readable account information from entry"""
        # Try to get account name from various fields
        for field in ['Title', 'title', 'Account', 'account', 'Website', 'website', 'URL', 'url']:
            if field in entry and entry[field]:
                return f"{entry[field]} ({folder_name})"

        # Try username as fallback
        for field in ['Username', 'username', 'Email', 'email']:
            if field in entry and entry[field]:
                return f"{entry[field]} ({folder_name})"

        return f"Unnamed Account ({folder_name})"

    def create_weak_passwords_section(self, weak_passwords):
        """Create UI section for weak passwords"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: rgba(255, 71, 87, 0.1);
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(section)
        layout.setSpacing(8)

        # Header
        header = QLabel(f"⚠️ Weak Passwords ({len(weak_passwords)})")
        header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #ff4757; background: transparent;")
        layout.addWidget(header)

        # List weak passwords
        for weak_pass in weak_passwords[:10]:  # Limit to 10 for UI
            account_widget = self.create_password_issue_widget(
                weak_pass['account'],
                weak_pass['password'],
                ", ".join(weak_pass['issues'])
            )
            layout.addWidget(account_widget)

        if len(weak_passwords) > 10:
            more_label = QLabel(f"... and {len(weak_passwords) - 10} more")
            more_label.setStyleSheet("color: #888888; background: transparent;")
            layout.addWidget(more_label)

        return section

    def create_duplicate_passwords_section(self, duplicate_passwords):
        """Create UI section for duplicate passwords"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: rgba(255, 149, 0, 0.1);
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(section)
        layout.setSpacing(8)

        # Header
        header = QLabel(f"🔄 Duplicate Passwords ({len(duplicate_passwords)})")
        header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #ff9500; background: transparent;")
        layout.addWidget(header)

        # List duplicates
        for duplicate in duplicate_passwords[:5]:  # Limit to 5 for UI
            accounts_text = ", ".join(duplicate['accounts'])
            duplicate_widget = self.create_password_issue_widget(
                f"Used by {len(duplicate['accounts'])} accounts",
                duplicate['password'],
                accounts_text
            )
            layout.addWidget(duplicate_widget)

        if len(duplicate_passwords) > 5:
            more_label = QLabel(f"... and {len(duplicate_passwords) - 5} more")
            more_label.setStyleSheet("color: #888888; background: transparent;")
            layout.addWidget(more_label)

        return section

    def create_password_issue_widget(self, title, password, details):
        """Create widget for displaying password issues"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(4)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; background: transparent;")
        layout.addWidget(title_label)

        # Password (with show/hide)
        password_layout = QHBoxLayout()

        password_label = QLabel("•" * len(password) if not self.show_passwords else password)
        password_label.setFont(QFont("Consolas", 10))
        password_label.setStyleSheet("color: #ffaa00; background: transparent;")

        eye_btn = ModernSmallButton()
        eye_btn.setFixedSize(24, 24)
        eye_btn.clicked.connect(lambda: self.toggle_individual_password(password_label, password))
        self.update_eye_button(eye_btn, self.show_passwords)

        password_layout.addWidget(password_label)
        password_layout.addWidget(eye_btn)
        password_layout.addStretch()

        # Details
        details_label = QLabel(details)
        details_label.setFont(QFont("Segoe UI", 9))
        details_label.setStyleSheet("color: #888888; background: transparent;")
        details_label.setWordWrap(True)
        layout.addWidget(details_label)

        layout.addLayout(password_layout)

        return widget

    def toggle_individual_password(self, label, password):
        """Toggle individual password visibility"""
        current_text = label.text()
        if "•" in current_text:
            label.setText(password)
        else:
            label.setText("•" * len(password))

    def toggle_global_password_visibility(self):
        """Toggle global password visibility"""
        self.show_passwords = not self.show_passwords
        self.update_global_eye_button()
        self.refresh_security_data()

    def update_global_eye_button(self):
        """Update the global eye button icon and text"""
        if self.show_passwords:
            icon = SvgIcon.create_icon(Icons.EYE_OFF, QSize(16, 16), "#4CAF50")
            self.global_eye_btn.setText(" Hide All")
        else:
            icon = SvgIcon.create_icon(Icons.EYE, QSize(16, 16), "#4CAF50")
            self.global_eye_btn.setText(" Show All")

        self.global_eye_btn.setIcon(icon)

    def update_eye_button(self, button, show_password):
        """Update individual eye button"""
        if show_password:
            icon = SvgIcon.create_icon(Icons.EYE_OFF, QSize(12, 12), "#888888")
        else:
            icon = SvgIcon.create_icon(Icons.EYE, QSize(12, 12), "#888888")
        button.setIcon(icon)

    def refresh_security_data(self):
        """Refresh the security analysis"""
        if hasattr(self, 'vault_data') and self.vault_data:
            # Clear and rebuild content
            main_layout = self.layout()
            # Rebuild tab sections
            self.create_tab_sections(main_layout)

    def closeEvent(self, event):
        """Handle dialog close"""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        event.accept()

    # Auto-backup integration hook (to be called from vault save operations)
    def auto_backup_vault(self, vault_file_path):
        """Automatically backup vault after save (premium feature)"""
        try:
            if self.google_drive_service and os.path.exists(vault_file_path):
                print("🔄 Auto-backup triggered after vault save...")
                result = self.backup_vault_to_google_drive(vault_file_path)

                if result["success"]:
                    print("✅ Auto-backup completed successfully")
                    self.show_backup_progress("✅ Auto-backup completed")
                else:
                    print(f"❌ Auto-backup failed: {result['message']}")
                    self.show_backup_progress("❌ Auto-backup failed")

        except Exception as e:
            print(f"Auto-backup error: {e}")