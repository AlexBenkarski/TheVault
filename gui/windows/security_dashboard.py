# gui/windows/security_dashboard.py
"""
Security Dashboard with Google Drive backup integration
Fixed to inherit from QWidget and handle tabs properly
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

from gui.widgets.modern_widgets import ModernButton
from gui.widgets.svg_icons import SvgIcon, Icons
from PyQt6.QtCore import QSize
import webbrowser
import threading


class DuplicatePasswordWidget(QWidget):
    """Widget for displaying duplicate password information"""

    def __init__(self, password, accounts):
        super().__init__()
        self.password = password
        self.accounts = accounts
        self.show_password = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Top row - password and eye button
        top_layout = QHBoxLayout()

        self.password_label = QLabel(f'"••••••••" used in {len(self.accounts)} accounts:')
        self.password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.password_label.setStyleSheet("color: #ff4757; background: transparent;")

        # Eye button
        self.eye_btn = QPushButton()
        self.eye_btn.setFixedSize(24, 24)
        self.update_eye_button()
        self.eye_btn.clicked.connect(self.toggle_password_visibility)

        top_layout.addWidget(self.password_label)
        top_layout.addStretch()
        top_layout.addWidget(self.eye_btn)

        # Accounts list
        accounts_widget = QWidget()
        accounts_layout = QVBoxLayout(accounts_widget)
        accounts_layout.setContentsMargins(0, 0, 0, 0)
        accounts_layout.setSpacing(2)

        for account in self.accounts:
            account_label = QLabel(f"• {account}")
            account_label.setFont(QFont("Segoe UI", 9))
            account_label.setStyleSheet("color: #ff4757; background: transparent;")
            accounts_layout.addWidget(account_label)

        layout.addLayout(top_layout)
        layout.addWidget(accounts_widget)

    def update_eye_button(self):
        if self.show_password:
            icon = SvgIcon.create_icon(Icons.EYE_OFF, QSize(16, 16), "#ffffff")
            self.eye_btn.setToolTip("Hide password")
        else:
            icon = SvgIcon.create_icon(Icons.EYE, QSize(16, 16), "#ffffff")
            self.eye_btn.setToolTip("Show password")

        self.eye_btn.setIcon(icon)
        self.eye_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
            }
        """)

    def toggle_password_visibility(self):
        self.show_password = not self.show_password
        password_text = self.password if self.show_password else "••••••••"
        count = len(self.accounts)
        self.password_label.setText(f'"{password_text}" used in {count} accounts:')
        self.update_eye_button()


class SecurityDashboard(QWidget):
    """Main security dashboard widget"""

    def __init__(self):
        super().__init__()
        self.vault_data = None
        self.show_passwords = False
        self.gdrive_backup = None
        self.init_ui()

    def init_ui(self):
        """Initialize the security dashboard UI"""
        self.setStyleSheet("""
            SecurityDashboard {
                background-color: #2d2d30;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header section
        self.create_header_section(main_layout)

        # Create 3-tab layout
        self.create_tab_sections(main_layout)

        # Initialize Google Drive backup
        self.init_google_drive()

    def init_google_drive(self):
        """Initialize Google Drive backup manager"""
        try:
            from core.google_drive_backup import get_google_drive_backup
            self.gdrive_backup = get_google_drive_backup()

            # Update backup status
            QTimer.singleShot(1000, self.update_backup_status)
        except Exception as e:
            print(f"Error initializing Google Drive: {e}")

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

        # Header with toggle
        header_layout = QHBoxLayout()

        title = QLabel("Password Security")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")

        # Global password visibility toggle
        self.global_eye_btn = QPushButton()
        self.global_eye_btn.setFixedHeight(32)
        self.global_eye_btn.setFixedWidth(100)
        self.update_global_eye_button()
        self.global_eye_btn.clicked.connect(self.toggle_all_passwords)
        self.global_eye_btn.setStyleSheet("""
            QPushButton {
                background: rgba(76, 175, 80, 0.1);
                border: 1px solid rgba(76, 175, 80, 0.3);
                border-radius: 6px;
                color: #4CAF50;
                font-size: 11px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: rgba(76, 175, 80, 0.2);
            }
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.global_eye_btn)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }
        """)

        # Content widget for scroll area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)

        scroll_area.setWidget(self.content_widget)

        layout.addLayout(header_layout)
        layout.addWidget(scroll_area)

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

        # Premium badge - remove since whole security dashboard is premium
        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Backup status section
        status_widget = self.create_backup_status_widget()

        # Connection section
        connection_widget = self.create_connection_widget()

        # Action buttons
        actions_widget = self.create_backup_actions_widget()

        layout.addLayout(header_layout)
        layout.addWidget(status_widget)
        layout.addWidget(connection_widget)
        layout.addWidget(actions_widget)
        layout.addStretch()

        return tab_widget

    def create_backup_status_widget(self):
        """Create backup status display"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Connection status with SVG icon
        self.connection_status_label = QLabel("Checking connection...")
        self.connection_status_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.connection_status_label.setStyleSheet("color: #ffffff;")

        # Last backup info
        self.last_backup_label = QLabel("Last backup: Unknown")
        self.last_backup_label.setFont(QFont("Segoe UI", 10))
        self.last_backup_label.setStyleSheet("color: #888888;")

        # Backup count
        self.backup_count_label = QLabel("Backup files: 0")
        self.backup_count_label.setFont(QFont("Segoe UI", 10))
        self.backup_count_label.setStyleSheet("color: #888888;")

        layout.addWidget(self.connection_status_label)
        layout.addWidget(self.last_backup_label)
        layout.addWidget(self.backup_count_label)

        return widget

    def create_connection_widget(self):
        """Create Google Drive connection controls"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: rgba(76, 175, 80, 0.08);
                border: none;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        connection_title = QLabel("Connection")
        connection_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        connection_title.setStyleSheet("color: #ffffff;")

        # Info text
        info_text = QLabel(
            "Securely connect to Google Drive for automatic vault backups. Your vault stays encrypted - we never see your passwords!")
        info_text.setFont(QFont("Segoe UI", 9))
        info_text.setStyleSheet("color: #888888;")
        info_text.setWordWrap(True)

        layout.addWidget(connection_title)
        layout.addWidget(info_text)

        return widget

    def create_backup_actions_widget(self):
        """Create backup action buttons"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # Connect/Disconnect button
        self.connect_btn = ModernButton("Connect to Google Drive")
        self.connect_btn.setFixedHeight(36)
        self.connect_btn.clicked.connect(self.handle_connection_toggle)

        # Backup now button
        self.backup_now_btn = ModernButton("Backup Now")
        self.backup_now_btn.setFixedHeight(36)
        self.backup_now_btn.clicked.connect(self.backup_vault_now)
        self.backup_now_btn.setEnabled(False)  # Disabled until connected

        # Disconnect button (initially hidden)
        self.disconnect_btn = ModernButton("Disconnect")
        self.disconnect_btn.setFixedHeight(36)
        self.disconnect_btn.clicked.connect(self.disconnect_google_drive)
        self.disconnect_btn.setStyleSheet("""
            ModernButton {
                background: rgba(255, 71, 87, 0.1);
                border: 1px solid rgba(255, 71, 87, 0.3);
                color: #ff4757;
            }
            ModernButton:hover {
                background: rgba(255, 71, 87, 0.2);
            }
        """)
        self.disconnect_btn.hide()

        layout.addWidget(self.connect_btn)
        layout.addWidget(self.backup_now_btn)
        layout.addWidget(self.disconnect_btn)

        return widget

    def update_global_eye_button(self):
        """Update the global eye button icon and text"""
        if self.show_passwords:
            icon = SvgIcon.create_icon(Icons.EYE_OFF, QSize(16, 16), "#4CAF50")
            self.global_eye_btn.setText(" Hide All")
        else:
            icon = SvgIcon.create_icon(Icons.EYE, QSize(16, 16), "#4CAF50")
            self.global_eye_btn.setText(" Show All")

        self.global_eye_btn.setIcon(icon)

    def toggle_all_passwords(self):
        """Toggle visibility of all passwords"""
        self.show_passwords = not self.show_passwords
        self.update_global_eye_button()

        # Update all duplicate password widgets
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if isinstance(widget, DuplicatePasswordWidget):
                widget.show_password = self.show_passwords
                widget.toggle_password_visibility()

    def set_vault_data(self, vault_data):
        """Set vault data and analyze security"""
        self.vault_data = vault_data
        self.analyze_password_security()
        self.calculate_security_score()

    def analyze_password_security(self):
        """Analyze vault passwords for security issues"""
        if not self.vault_data:
            return

        # Clear existing content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Find duplicate passwords
        password_accounts = {}

        for folder_name, folder_data in self.vault_data.items():
            if "entries" in folder_data:
                for entry in folder_data["entries"]:
                    if "Password" in entry:
                        password = entry["Password"]
                        account_name = entry.get("Account", entry.get("Username", "Unknown"))

                        if password in password_accounts:
                            password_accounts[password].append(f"{folder_name}: {account_name}")
                        else:
                            password_accounts[password] = [f"{folder_name}: {account_name}"]

        # Create widgets for duplicate passwords
        duplicates_found = False
        for password, accounts in password_accounts.items():
            if len(accounts) > 1:  # Duplicate found
                duplicates_found = True
                duplicate_widget = DuplicatePasswordWidget(password, accounts)
                duplicate_widget.setStyleSheet("""
                    DuplicatePasswordWidget {
                        background: rgba(255, 71, 87, 0.1);
                        border: 1px solid rgba(255, 71, 87, 0.2);
                        border-radius: 8px;
                        margin: 2px;
                    }
                """)
                self.content_layout.addWidget(duplicate_widget)

        if not duplicates_found:
            no_duplicates_label = QLabel("No duplicate passwords found!")
            no_duplicates_label.setFont(QFont("Segoe UI", 12))
            no_duplicates_label.setStyleSheet("color: #4CAF50; padding: 20px;")
            no_duplicates_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_duplicates_label)

        self.content_layout.addStretch()

    def calculate_security_score(self):
        """Calculate and update security score"""
        if not self.vault_data:
            return

        score = 100
        total_passwords = 0
        weak_passwords = 0
        duplicate_passwords = 0

        password_counts = {}

        for folder_data in self.vault_data.values():
            if "entries" in folder_data:
                for entry in folder_data["entries"]:
                    if "Password" in entry:
                        password = entry["Password"]
                        total_passwords += 1

                        # Check password strength
                        if len(password) < 8:
                            weak_passwords += 1
                        elif not any(c.isupper() for c in password):
                            weak_passwords += 1
                        elif not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                            weak_passwords += 1

                        # Count duplicates
                        password_counts[password] = password_counts.get(password, 0) + 1

        # Count actual duplicate passwords
        for count in password_counts.values():
            if count > 1:
                duplicate_passwords += count

        # Calculate score deductions
        if total_passwords > 0:
            weak_penalty = (weak_passwords / total_passwords) * 30
            duplicate_penalty = (duplicate_passwords / total_passwords) * 40
            score = max(0, score - weak_penalty - duplicate_penalty)

        # Update score display
        self.security_score_label.setText(str(int(score)))

        # Color coding
        if score >= 80:
            color = "#4CAF50"  # Green
        elif score >= 60:
            color = "#ffaa00"  # Orange
        else:
            color = "#ff4757"  # Red

        self.security_score_label.setStyleSheet(f"color: {color};")

    def handle_connection_toggle(self):
        """Handle connect/disconnect button click"""
        if not self.gdrive_backup:
            self.show_error("Google Drive backup not available")
            return

        if self.gdrive_backup.is_authenticated():
            # Already connected, show disconnect option
            self.disconnect_google_drive()
        else:
            # Not connected, start OAuth flow
            self.connect_to_google_drive()

    def connect_to_google_drive(self):
        """Start Google Drive OAuth connection"""
        try:
            if not self.gdrive_backup.client_id:
                # Show setup instructions for developers
                msg = QMessageBox(self)
                msg.setWindowTitle("Google Drive Setup Required")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText("Google Drive backup is not yet configured.")
                msg.setInformativeText("""To enable Google Drive backups:

1. Create a Google Cloud Project
2. Enable the Google Drive API  
3. Create OAuth 2.0 credentials
4. Add credentials to secrets.json:
   {
     "google_drive": {
       "client_id": "your-client-id.apps.googleusercontent.com",
       "client_secret": "your-client-secret"
     }
   }

This is a one-time setup.""")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                return

            # Show OAuth flow dialog
            msg = QMessageBox(self)
            msg.setWindowTitle("Connect to Google Drive")
            msg.setText("Opening Google Drive authorization...")
            msg.setInformativeText(
                "Your browser will open for secure authentication.\nThis window will close automatically when complete.")
            msg.setStandardButtons(QMessageBox.StandardButton.Cancel)
            msg.show()

            # Start OAuth flow in background thread
            def run_oauth():
                try:
                    success = self.gdrive_backup.run_oauth_flow()

                    # Update UI on main thread
                    QTimer.singleShot(0, lambda: self.oauth_completed(success, msg))

                except Exception as e:
                    QTimer.singleShot(0, lambda: self.oauth_completed(False, msg, str(e)))

            threading.Thread(target=run_oauth, daemon=True).start()

            # Handle cancel
            def on_cancel():
                msg.close()
                self.show_error("Google Drive connection cancelled")

            msg.rejected.connect(on_cancel)

        except Exception as e:
            self.show_error(f"Connection error: {str(e)}")

    def oauth_completed(self, success, dialog, error=None):
        """Handle OAuth flow completion"""
        dialog.close()

        if success:
            self.show_success(
                "Successfully connected to Google Drive!\n\nYour vault backups are now protected in the cloud.")
            self.update_backup_status()
        else:
            error_msg = f"Failed to connect to Google Drive"
            if error:
                error_msg += f"\n\nError: {error}"
            self.show_error(error_msg)

    def disconnect_google_drive(self):
        """Disconnect from Google Drive"""
        try:
            self.gdrive_backup.disconnect()
            self.show_success("Disconnected from Google Drive")
            self.update_backup_status()
        except Exception as e:
            self.show_error(f"Disconnect error: {str(e)}")

    def backup_vault_now(self):
        """Perform manual vault backup"""
        if not self.gdrive_backup or not self.gdrive_backup.is_authenticated():
            self.show_error("Not connected to Google Drive")
            return

        try:
            from core.vault_manager import get_vault_path
            vault_path = get_vault_path()

            # Show progress
            self.backup_now_btn.setText("Backing up...")
            self.backup_now_btn.setEnabled(False)

            # Perform backup in thread to avoid blocking UI
            def do_backup():
                success, message = self.gdrive_backup.upload_vault_backup(vault_path)

                # Update UI on main thread
                QTimer.singleShot(0, lambda: self.backup_completed(success, message))

            threading.Thread(target=do_backup, daemon=True).start()

        except Exception as e:
            self.show_error(f"Backup error: {str(e)}")
            self.backup_now_btn.setText("Backup Now")
            self.backup_now_btn.setEnabled(True)

    def backup_completed(self, success, message):
        """Handle backup completion"""
        self.backup_now_btn.setText("Backup Now")
        self.backup_now_btn.setEnabled(True)

        if success:
            self.show_success(message)
            self.update_backup_status()
        else:
            self.show_error(f"Backup failed: {message}")

    def update_backup_status(self):
        """Update Google Drive backup status"""
        if not self.gdrive_backup:
            return

        try:
            status = self.gdrive_backup.get_backup_status()

            if status["connected"]:
                self.connection_status_label.setText("Connected to Google Drive")
                self.connection_status_label.setStyleSheet("color: #4CAF50;")

                self.connect_btn.setText("Connected")
                self.connect_btn.setEnabled(False)
                self.backup_now_btn.setEnabled(True)
                self.disconnect_btn.show()

                # Update backup info
                if status["last_backup"]:
                    self.last_backup_label.setText(f"Last backup: {status['last_backup']}")
                    self.last_backup_label.setStyleSheet("color: #4CAF50;")
                else:
                    self.last_backup_label.setText("Last backup: Never")
                    self.last_backup_label.setStyleSheet("color: #ffaa00;")

                self.backup_count_label.setText(f"Backup files: {status['backup_count']}")

            else:
                self.connection_status_label.setText("Not connected")
                self.connection_status_label.setStyleSheet("color: #ff4757;")

                self.connect_btn.setText("Connect to Google Drive")
                self.connect_btn.setEnabled(True)
                self.backup_now_btn.setEnabled(False)
                self.disconnect_btn.hide()

                self.last_backup_label.setText("Connect to Google Drive for automatic backups")
                self.last_backup_label.setStyleSheet("color: #888888;")

                self.backup_count_label.setText("No backup protection")

            if status.get("error"):
                self.show_error(f"Backup status error: {status['error']}")

        except Exception as e:
            print(f"Error updating backup status: {e}")

    def show_success(self, message):
        """Show success message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText(message)
        msg.exec()

    def show_error(self, message):
        """Show error message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec()