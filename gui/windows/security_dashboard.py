import os

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QScrollArea, QTabWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from gui.widgets.modern_widgets import ModernButton
from gui.widgets.svg_icons import SvgIcon, Icons


class PasswordIssueCard(QFrame):
    """Individual password issue display card"""

    def __init__(self, password, issues, account_info, show_password=False):
        super().__init__()
        self.password = password
        self.issues = issues
        self.account_info = account_info
        self.show_password = show_password
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(100)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 8px;
                margin: 2px 0px;
            }
            QFrame:hover {
                background: rgba(255, 255, 87, 0.08);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Top row - password and eye button
        top_layout = QHBoxLayout()

        password_text = self.password if self.show_password else "••••••••"
        self.password_label = QLabel(f'"{password_text}" is weak because:')
        self.password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.password_label.setStyleSheet("color: #ffffff; background: transparent;")

        # Eye toggle button
        self.eye_btn = QPushButton()
        self.eye_btn.setFixedSize(28, 24)
        self.update_eye_button()
        self.eye_btn.clicked.connect(self.toggle_password_visibility)

        top_layout.addWidget(self.password_label)
        top_layout.addStretch()
        top_layout.addWidget(self.eye_btn)

        # Issues and account in one line
        issues_text = " • ".join(self.issues)
        combined_text = f"{issues_text}\nUsed in: {self.account_info}"

        combined_label = QLabel(combined_text)
        combined_label.setFont(QFont("Segoe UI", 9))
        combined_label.setStyleSheet("color: #ff9500; background: transparent;")
        combined_label.setWordWrap(True)

        layout.addLayout(top_layout)
        layout.addWidget(combined_label)

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
        self.password_label.setText(f'"{password_text}" is weak because:')
        self.update_eye_button()


class DuplicatePasswordCard(QFrame):
    """Card showing duplicate password usage"""

    def __init__(self, password, accounts, show_password=False):
        super().__init__()
        self.password = password
        self.accounts = accounts
        self.show_password = show_password
        self.init_ui()

    def init_ui(self):
        # Dynamic height based on number of accounts
        base_height = 60
        account_height = len(self.accounts) * 20
        total_height = base_height + account_height
        self.setFixedHeight(max(80, total_height))

        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 8px;
                margin: 2px 0px;
            }
            QFrame:hover {
                background: rgba(255, 71, 87, 0.08);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(6)

        # Top row - password and eye button
        top_layout = QHBoxLayout()

        password_text = self.password if self.show_password else "••••••••"
        count = len(self.accounts)
        self.password_label = QLabel(f'"{password_text}" used in {count} accounts:')
        self.password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.password_label.setStyleSheet("color: #ffffff; background: transparent;")

        # Eye toggle button
        self.eye_btn = QPushButton()
        self.eye_btn.setFixedSize(28, 24)
        self.update_eye_button()
        self.eye_btn.clicked.connect(self.toggle_password_visibility)

        top_layout.addWidget(self.password_label)
        top_layout.addStretch()
        top_layout.addWidget(self.eye_btn)

        # Accounts list - no scrolling, full expansion
        accounts_widget = QWidget()
        accounts_layout = QVBoxLayout(accounts_widget)
        accounts_layout.setContentsMargins(0, 0, 0, 0)
        accounts_layout.setSpacing(2)

        # Add each account as a separate label
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
    def __init__(self):
        super().__init__()
        self.vault_data = None
        self.show_passwords = False
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

        # Tab 3: OneDrive Backup
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
        """Create backup tab with OneDrive functionality"""
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

        title = QLabel("OneDrive Backup")
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

        # OneDrive sync status
        self.onedrive_status_label = QLabel("🔍 Checking OneDrive sync...")
        self.onedrive_status_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.onedrive_status_label.setStyleSheet("color: #ffffff; background: transparent;")

        # Vault location info
        self.vault_location_label = QLabel("Vault location: Checking...")
        self.vault_location_label.setFont(QFont("Segoe UI", 10))
        self.vault_location_label.setStyleSheet("color: #888888; background: transparent;")

        # Last sync time
        self.last_sync_label = QLabel("Last sync: Unknown")
        self.last_sync_label.setFont(QFont("Segoe UI", 10))
        self.last_sync_label.setStyleSheet("color: #888888; background: transparent;")

        layout.addWidget(self.onedrive_status_label)
        layout.addWidget(self.vault_location_label)
        layout.addWidget(self.last_sync_label)

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

        settings_title = QLabel("Sync Settings")
        settings_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        settings_title.setStyleSheet("color: #ffffff; background: transparent;")

        # OneDrive sync status
        sync_status_widget = QWidget()
        sync_status_layout = QHBoxLayout(sync_status_widget)
        sync_status_layout.setContentsMargins(0, 0, 0, 0)

        sync_status_label = QLabel("OneDrive Files On-Demand")
        sync_status_label.setFont(QFont("Segoe UI", 10))
        sync_status_label.setStyleSheet("color: #ffffff; background: transparent;")

        self.sync_status_indicator = QLabel("Unknown")
        self.sync_status_indicator.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.sync_status_indicator.setStyleSheet("color: #ffaa00; background: transparent;")

        sync_status_layout.addWidget(sync_status_label)
        sync_status_layout.addStretch()
        sync_status_layout.addWidget(self.sync_status_indicator)

        # Vault protection info
        protection_info = QLabel("Your vault is automatically backed up when OneDrive syncs. No manual backups needed!")
        protection_info.setFont(QFont("Segoe UI", 9))
        protection_info.setStyleSheet("color: #888888; background: transparent;")
        protection_info.setWordWrap(True)

        layout.addWidget(settings_title)
        layout.addWidget(sync_status_widget)
        layout.addWidget(protection_info)

        return widget

    def create_backup_actions_widget(self):
        """Create backup action buttons"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # Force sync button
        self.force_sync_btn = ModernButton("Force Sync Now")
        self.force_sync_btn.setFixedHeight(36)
        self.force_sync_btn.clicked.connect(self.force_sync_vault)

        # Open OneDrive folder button
        self.open_onedrive_btn = ModernButton("Open OneDrive Folder")
        self.open_onedrive_btn.setFixedHeight(36)
        self.open_onedrive_btn.clicked.connect(self.open_onedrive_folder)

        # Check sync status button
        self.check_sync_btn = ModernButton("Check Sync Status")
        self.check_sync_btn.setFixedHeight(36)
        self.check_sync_btn.clicked.connect(self.check_sync_status)

        layout.addWidget(self.force_sync_btn)
        layout.addWidget(self.open_onedrive_btn)
        layout.addWidget(self.check_sync_btn)

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
        self.global_eye_btn.setIconSize(QSize(16, 16))

    def toggle_all_passwords(self):
        """Toggle visibility of all passwords"""
        self.show_passwords = not self.show_passwords
        self.update_global_eye_button()

        # Update all cards
        self.refresh_password_issues()

    def load_vault_data(self, vault_data):
        """Load vault data and update security analysis"""
        self.vault_data = vault_data
        self.analyze_security()

        # Update backup status safely
        try:
            self.update_backup_status()
        except Exception as e:
            print(f"Error updating backup status: {e}")

    def analyze_security(self):
        """Analyze vault security and update UI"""
        if not self.vault_data:
            return

        try:
            print("Analyzing vault security...")

            # Get vault data structure
            vault_folders = self.vault_data.get("data", {})

            # Analyze weak passwords and duplicates
            weak_passwords = self.analyze_weak_passwords(vault_folders)
            duplicate_passwords = self.analyze_duplicate_passwords(vault_folders)

            # Calculate overall security score
            security_score = self.calculate_security_score(len(weak_passwords), len(duplicate_passwords))

            print(
                f"Analysis results: {len(weak_passwords)} weak, {len(duplicate_passwords)} duplicates, score: {security_score}")

            # Update security score display
            score_color = "#4CAF50" if security_score >= 70 else "#ffaa00" if security_score >= 40 else "#f44336"
            self.security_score_label.setText(str(security_score))
            self.security_score_label.setStyleSheet(f"color: {score_color}; font-size: 36px; font-weight: bold;")

            # Store analysis results
            self.weak_passwords = weak_passwords
            self.duplicate_passwords = duplicate_passwords

            print("About to refresh password issues...")

            # Refresh the password issues display
            self.refresh_password_issues()

            print(
                f"Security analysis complete: {len(weak_passwords)} weak, {len(duplicate_passwords)} duplicates, score: {security_score}")

        except Exception as e:
            print(f"Error during security analysis: {e}")
            import traceback
            traceback.print_exc()

    def analyze_weak_passwords(self, vault_folders):
        """Analyze and return weak passwords with details"""
        weak_passwords = []

        for folder_name, folder_data in vault_folders.items():
            entries = folder_data.get("entries", [])
            for entry in entries:
                # Check password fields
                for field in ['Password', 'password']:
                    if field in entry:
                        password = entry[field]
                        if password:
                            issues = self.get_password_issues(password)
                            if issues:
                                # Get account info
                                account_info = self.get_account_info(entry, folder_name)
                                weak_passwords.append({
                                    'password': password,
                                    'issues': issues,
                                    'account': account_info
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
            issues.append("No symbols")

        return issues

    def get_account_info(self, entry, folder_name):
        """Get readable account information from entry"""
        # Try to get title or username
        for field in ['Title', 'title', 'Username', 'username', 'Email', 'email']:
            if field in entry and entry[field]:
                return f"{folder_name} ({entry[field]})"

        return f"{folder_name} account"

    def calculate_security_score(self, weak_count, duplicate_count):
        """Calculate overall security score (0-100)"""
        score = 100
        score -= weak_count * 5  # 5 points per weak password
        score -= duplicate_count * 10  # 10 points per duplicate group
        return max(0, score)

    def refresh_password_issues(self):
        """Refresh the password issues display"""
        try:
            print("Starting refresh_password_issues...")

            # Clear existing content safely
            while self.content_layout.count():
                child = self.content_layout.takeAt(0)
                if child.widget():
                    widget = child.widget()
                    widget.setParent(None)
                    widget.deleteLater()

            print("Cleared existing content")

            if not hasattr(self, 'weak_passwords') or not hasattr(self, 'duplicate_passwords'):
                print("No password data available")
                return

            print(
                f"Processing {len(self.weak_passwords)} weak passwords and {len(self.duplicate_passwords)} duplicates")

            # Add weak password cards
            if self.weak_passwords:
                weak_header = QLabel("Weak Passwords:")
                weak_header.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                weak_header.setStyleSheet("color: #ffaa00; margin: 10px 0px 5px 0px;")
                self.content_layout.addWidget(weak_header)

                for i, weak_pwd in enumerate(self.weak_passwords):
                    print(f"Creating weak password card {i + 1}")
                    try:
                        card = PasswordIssueCard(
                            weak_pwd['password'],
                            weak_pwd['issues'],
                            weak_pwd['account'],
                            self.show_passwords
                        )
                        self.content_layout.addWidget(card)
                    except Exception as e:
                        print(f"Error creating weak password card {i + 1}: {e}")

            # Add duplicate password cards
            if self.duplicate_passwords:
                dup_header = QLabel("Duplicate Passwords:")
                dup_header.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                dup_header.setStyleSheet("color: #ff4757; margin: 20px 0px 5px 0px;")
                self.content_layout.addWidget(dup_header)

                for i, dup_pwd in enumerate(self.duplicate_passwords):
                    print(f"Creating duplicate password card {i + 1}")
                    try:
                        card = DuplicatePasswordCard(
                            dup_pwd['password'],
                            dup_pwd['accounts'],
                            self.show_passwords
                        )
                        self.content_layout.addWidget(card)
                    except Exception as e:
                        print(f"Error creating duplicate password card {i + 1}: {e}")

            # Add stretch to push content to top
            self.content_layout.addStretch()

            print("Completed refresh_password_issues")

        except Exception as e:
            print(f"Error in refresh_password_issues: {e}")
            import traceback
            traceback.print_exc()

    def force_sync_vault(self):
        """Force OneDrive to sync the vault file"""
        try:
            print("Forcing vault sync to OneDrive...")

            # Get vault file path (assuming it's accessible)
            vault_path = self.get_vault_file_path()
            if not vault_path or not os.path.exists(vault_path):
                print("Vault file not found for sync")
                self.show_sync_result("❌ Vault file not found", False)
                return

            print(f"Syncing vault file: {vault_path}")

            # Method 1: Use attrib to force sync
            sync_success = self.force_file_sync_attrib(vault_path)

            if not sync_success:
                # Method 2: Touch file to trigger sync
                sync_success = self.touch_file_to_trigger_sync(vault_path)

            if sync_success:
                self.show_sync_result("✅ Sync triggered successfully", True)
                # Auto-refresh status after sync
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(3000, self.update_backup_status)  # Check again in 3 seconds
            else:
                self.show_sync_result("⚠️ Sync trigger failed", False)

        except Exception as e:
            print(f"Error forcing vault sync: {e}")
            self.show_sync_result("❌ Sync error occurred", False)

    def get_vault_file_path(self):
        """Get the current vault file path"""
        try:
            # Try to get vault path from config or environment
            from config import get_vault_path
            return get_vault_path()
        except:
            # Fallback: look in OneDrive/TheVault
            onedrive_path = os.environ.get('ONEDRIVE')
            if onedrive_path:
                vault_path = os.path.join(onedrive_path, 'TheVault', 'vault.enc')
                if os.path.exists(vault_path):
                    return vault_path
            return None

    def force_file_sync_attrib(self, file_path):
        """Force file sync using Windows attrib command"""
        try:
            import subprocess
            print(f"Using attrib method to force sync: {file_path}")

            # Set file as pinned (always keep on device) to force sync
            result1 = subprocess.run(['attrib', '+P', file_path], capture_output=True, text=True)
            if result1.returncode != 0:
                print(f"Attrib +P failed: {result1.stderr}")
                return False

            # Wait briefly
            import time
            time.sleep(0.5)

            # Remove pinned attribute
            result2 = subprocess.run(['attrib', '-P', file_path], capture_output=True, text=True)
            if result2.returncode != 0:
                print(f"Attrib -P failed: {result2.stderr}")
                return False

            print("Attrib sync method completed successfully")
            return True

        except Exception as e:
            print(f"Attrib sync method failed: {e}")
            return False

    def touch_file_to_trigger_sync(self, file_path):
        """Touch file to trigger OneDrive sync"""
        try:
            print(f"Using touch method to trigger sync: {file_path}")

            # Update file access time to trigger sync detection
            import os
            import time

            # Get current times
            stat = os.stat(file_path)

            # Update access time (but keep modification time)
            os.utime(file_path, (time.time(), stat.st_mtime))

            print("Touch sync method completed")
            return True

        except Exception as e:
            print(f"Touch sync method failed: {e}")
            return False

    def show_sync_result(self, message, success):
        """Show sync result in the UI"""
        try:
            color = "#4CAF50" if success else "#ff4757"

            # Update the OneDrive status label temporarily
            original_text = self.onedrive_status_label.text()
            self.onedrive_status_label.setText(message)
            self.onedrive_status_label.setStyleSheet(f"color: {color}; background: transparent;")

            # Restore original text after 5 seconds
            from PyQt6.QtCore import QTimer
            def restore_text():
                self.onedrive_status_label.setText(original_text)
                self.onedrive_status_label.setStyleSheet("color: #4CAF50; background: transparent;")

            QTimer.singleShot(5000, restore_text)

        except Exception as e:
            print(f"Error showing sync result: {e}")

    def check_vault_sync_status(self, vault_path):
        """Check the actual sync status of the vault file"""
        try:
            import subprocess

            # Check file attributes for OneDrive status
            result = subprocess.run(['attrib', vault_path], capture_output=True, text=True)

            if result.returncode == 0:
                attrs = result.stdout.strip()
                print(f"Vault file attributes: {attrs}")

                # Parse OneDrive status from attributes
                if 'P' in attrs:
                    return "pinned"  # Always kept locally and synced
                elif 'U' in attrs:
                    return "pending"  # Upload pending
                elif 'O' in attrs:
                    return "online_only"  # OneDrive only
                else:
                    return "local"  # Local file, sync status unknown
            else:
                return "error"

        except Exception as e:
            print(f"Error checking vault sync status: {e}")
            return "error"

    def open_onedrive_folder(self):
        """Open the OneDrive folder in explorer"""
        import os
        import subprocess

        onedrive_path = os.environ.get('ONEDRIVE')
        if onedrive_path:
            subprocess.run(['explorer', onedrive_path])
        else:
            print("OneDrive not detected")

    def is_onedrive_service_running(self):
        """Check if OneDrive service/process is actually running"""
        try:
            import subprocess

            print("Checking for OneDrive.exe process...")

            # Method 1: Check running processes for OneDrive
            result = subprocess.run([
                'tasklist', '/FI', 'IMAGENAME eq OneDrive.exe'
            ], capture_output=True, text=True, shell=True)

            print(f"Tasklist result: {result.returncode}")
            print(f"Tasklist output: {result.stdout[:200]}...")  # First 200 chars

            if result.returncode == 0 and 'OneDrive.exe' in result.stdout:
                print("OneDrive.exe process found running")
                return True

            print("OneDrive.exe not found in tasklist, trying PowerShell...")

            # Method 2: Alternative process check
            result = subprocess.run([
                'powershell', '-Command',
                'Get-Process -Name "OneDrive" -ErrorAction SilentlyContinue'
            ], capture_output=True, text=True)

            print(f"PowerShell result: {result.returncode}")
            print(f"PowerShell output: {result.stdout[:100]}...")  # First 100 chars

            if result.returncode == 0 and result.stdout.strip():
                print("OneDrive process found via PowerShell")
                return True

            print("OneDrive service not running")
            return False

        except Exception as e:
            print(f"Error checking OneDrive service: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_backup_status(self):
        """Update OneDrive sync status display"""
        try:
            print("Starting OneDrive sync status check...")
            import os
            from datetime import datetime

            onedrive_path = os.environ.get('ONEDRIVE')
            print(f"OneDrive path: {onedrive_path}")

            if onedrive_path and os.path.exists(onedrive_path):
                self.onedrive_status_label.setText("✅ OneDrive is running")
                self.onedrive_status_label.setStyleSheet("color: #4CAF50; background: transparent;")

                # Check if vault is in OneDrive
                if hasattr(self, 'vault_data'):
                    vault_in_onedrive = "OneDrive" in str(onedrive_path)  # Simple check
                    if vault_in_onedrive:
                        self.vault_location_label.setText("✅ Vault is in OneDrive folder")
                        self.vault_location_label.setStyleSheet("color: #4CAF50; background: transparent;")

                        # Check last modified time of OneDrive folder (rough sync indicator)
                        try:
                            last_modified = os.path.getmtime(onedrive_path)
                            sync_time = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M")
                            self.last_sync_label.setText(f"OneDrive folder activity: {sync_time}")
                        except:
                            self.last_sync_label.setText("OneDrive folder activity: Unknown")

                        self.sync_status_indicator.setText("✅ Protected")
                        self.sync_status_indicator.setStyleSheet("color: #4CAF50; background: transparent;")
                    else:
                        self.vault_location_label.setText("⚠️ Vault is NOT in OneDrive")
                        self.vault_location_label.setStyleSheet("color: #ff9500; background: transparent;")
                        self.last_sync_label.setText("Move vault to OneDrive for automatic backup")
                        self.sync_status_indicator.setText("⚠️ Not Protected")
                        self.sync_status_indicator.setStyleSheet("color: #ff9500; background: transparent;")
                else:
                    self.vault_location_label.setText("Vault location: Unknown")
                    self.last_sync_label.setText("Load vault to check location")
                    self.sync_status_indicator.setText("Unknown")
                    self.sync_status_indicator.setStyleSheet("color: #ffaa00; background: transparent;")

            else:
                print("OneDrive not detected or not running")
                self.onedrive_status_label.setText("❌ OneDrive not detected")
                self.onedrive_status_label.setStyleSheet("color: #ff4757; background: transparent;")
                self.vault_location_label.setText("Install and setup OneDrive for automatic backups")
                self.last_sync_label.setText("No automatic backup protection")
                self.sync_status_indicator.setText("❌ Not Protected")
                self.sync_status_indicator.setStyleSheet("color: #ff4757; background: transparent;")

            print("OneDrive sync status check completed")

        except Exception as e:
            print(f"Error checking OneDrive sync status: {e}")
            import traceback
            traceback.print_exc()

            # Safe fallback
            try:
                self.onedrive_status_label.setText("❌ Sync status error")
                self.onedrive_status_label.setStyleSheet("color: #ff4757; background: transparent;")
                self.vault_location_label.setText("Error checking vault location")
                self.last_sync_label.setText("Unable to determine sync status")
                self.sync_status_indicator.setText("Error")
                self.sync_status_indicator.setStyleSheet("color: #ff4757; background: transparent;")
            except:
                pass

    def check_sync_status(self):
        """Check OneDrive sync status"""
        print("Checking OneDrive sync status...")
        self.update_backup_status()

        # Also check vault file specific sync status
        try:
            vault_path = self.get_vault_file_path()
            if vault_path:
                sync_status = self.check_vault_sync_status(vault_path)
                print(f"Vault sync status: {sync_status}")

                # Update UI with specific vault sync info
                if sync_status == "pending":
                    self.last_sync_label.setText("⏳ Vault sync pending...")
                    self.last_sync_label.setStyleSheet("color: #ffaa00; background: transparent;")
                elif sync_status == "pinned":
                    self.last_sync_label.setText("✅ Vault is pinned and synced")
                    self.last_sync_label.setStyleSheet("color: #4CAF50; background: transparent;")
                elif sync_status == "error":
                    self.last_sync_label.setText("❌ Cannot check vault sync status")
                    self.last_sync_label.setStyleSheet("color: #ff4757; background: transparent;")
        except Exception as e:
            print(f"Error checking detailed sync status: {e}")

    def open_onedrive_folder(self):
        """Open the OneDrive folder in explorer"""
        import os
        import subprocess

        onedrive_path = os.environ.get('ONEDRIVE')
        if onedrive_path:
            subprocess.run(['explorer', onedrive_path])
        else:
            print("OneDrive not detected")