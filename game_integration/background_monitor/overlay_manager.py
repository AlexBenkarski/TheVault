from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class VaultOverlay(QWidget):
    finished = pyqtSignal()
    account_selected = pyqtSignal(dict)

    def __init__(self, main_app=None):
        super().__init__()
        self.main_app = main_app
        self.vault_data = None
        self.vault_key = None
        self.init_overlay()

    def init_overlay(self):


        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setFixedSize(420, 550)

        self.setStyleSheet("""
            VaultOverlay {
                background: #2d2d30;
                border: 2px solid #4CAF50;
                border-radius: 15px;
            }
            QLabel {
                background: transparent;
                border: none;
                color: #ffffff;
            }
            QWidget#titleWidget {
                background: transparent;
                border: none;
            }
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                selection-background-color: #4CAF50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background: rgba(255, 255, 255, 0.15);
                padding: 7px 11px;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        self.center_on_screen()

        # Check if vault is already open
        if self.is_vault_already_open():
            print("Vault is already open - skipping authentication")
            self.load_vault_from_main_app()
            self.show_account_list()
        else:
            print("Vault is not open - showing login")
            self.show_vault_login()

    def show_vault_login(self):
        """Show vault password entry with clean styling"""
        self.clear_layout()

        # Title section with logo
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        # Logo
        from gui.widgets.modern_widgets import LogoWidget
        logo_label = LogoWidget()
        title_layout.addWidget(logo_label)

        # App title
        app_title = QLabel("TheVault")
        app_title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title.setStyleSheet("color: #ffffff; background: transparent;")

        # Subtitle
        subtitle = QLabel("Auto-Fill Authentication")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitle")
        subtitle.setStyleSheet("color: #b0b0b0; background: transparent;")

        title_layout.addWidget(app_title)
        title_layout.addWidget(subtitle)


        title_widget = QWidget()
        title_widget.setObjectName("titleWidget")
        title_widget.setLayout(title_layout)
        self.layout.addWidget(title_widget)

        self.layout.addSpacing(15)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter vault password")
        self.password_input.setFixedHeight(40)
        self.password_input.setStyleSheet("""
           QLineEdit {
               background: rgba(255, 255, 255, 0.1);
               border: 1px solid rgba(255, 255, 255, 0.15);
               border-radius: 8px;
               padding: 8px 12px;
               color: #ffffff;
               selection-background-color: #4CAF50;
           }
           QLineEdit:focus {
               border: 2px solid #4CAF50;
               background: rgba(255, 255, 255, 0.15);
               padding: 7px 11px;
           }
           QLineEdit::placeholder {
               color: #888888;
           }
       """)
        self.password_input.returnPressed.connect(self.verify_vault_password)
        self.layout.addWidget(self.password_input)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff4757; font-size: 10px; background: transparent;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        self.layout.addWidget(self.error_label)

        self.layout.addSpacing(10)

        # Unlock button
        unlock_btn = QPushButton("Unlock Vault")
        unlock_btn.setMinimumHeight(45)
        unlock_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        unlock_btn.setStyleSheet("""
           QPushButton {
               border: none;
               border-radius: 12px;
               padding: 12px 24px;
               font-weight: 600;
               text-transform: uppercase;
               letter-spacing: 1px;
               background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                   stop:0 #4CAF50, stop:1 #45a049);
               color: white;
           }
           QPushButton:hover {
               background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                   stop:0 #45a049, stop:1 #3d8b40);
           }
           QPushButton:pressed {
               background: #3d8b40;
           }
       """)
        unlock_btn.clicked.connect(self.verify_vault_password)
        self.layout.addWidget(unlock_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        cancel_btn.setStyleSheet("""
           QPushButton {
               background: rgba(255, 255, 255, 0.1);
               color: #ffffff;
               border: 2px solid rgba(255, 255, 255, 0.25);
               border-radius: 12px;
               padding: 12px 24px;
               font-weight: 600;
               text-transform: uppercase;
               letter-spacing: 1px;
           }
           QPushButton:hover {
               background: rgba(255, 255, 255, 0.15);
               border: 2px solid rgba(255, 255, 255, 0.35);
           }
           QPushButton:pressed {
               background: rgba(255, 255, 255, 0.2);
           }
       """)
        cancel_btn.clicked.connect(self.close_overlay)
        self.layout.addWidget(cancel_btn)

        self.password_input.setFocus()

    def is_vault_already_open(self):
        """Check if main vault app is open and logged in"""
        try:
            if not self.main_app:
                print("DEBUG: No main app reference")
                return False

            print(f"DEBUG: Main app exists: {type(self.main_app)}")

            if not hasattr(self.main_app, 'stacked_widget'):
                print("DEBUG: No stacked widget")
                return False

            current_widget = self.main_app.stacked_widget.currentWidget()
            print(f"DEBUG: Current widget: {type(current_widget)}")

            # Check if vault window exists
            if not hasattr(self.main_app, 'vault_window'):
                print("DEBUG: No vault window attribute")
                return False

            print(f"DEBUG: Vault window: {type(self.main_app.vault_window)}")
            print(f"DEBUG: Current widget == vault window: {current_widget == self.main_app.vault_window}")

            if current_widget != self.main_app.vault_window:
                print("DEBUG: Not currently on vault window")
                return False

            # Check vault data
            vault_window = self.main_app.vault_window
            print(f"DEBUG: Vault window has vault_data attr: {hasattr(vault_window, 'vault_data')}")

            if hasattr(vault_window, 'vault_data'):
                print(f"DEBUG: Vault data: {vault_window.vault_data}")
                print(f"DEBUG: Vault data type: {type(vault_window.vault_data)}")

            print(f"DEBUG: Vault window has vault_key attr: {hasattr(vault_window, 'vault_key')}")

            if hasattr(vault_window, 'vault_key'):
                print(f"DEBUG: Vault key exists: {vault_window.vault_key is not None}")

            has_data = (hasattr(vault_window, 'vault_data') and
                        vault_window.vault_data and
                        vault_window.vault_data.get("data"))

            has_key = (hasattr(vault_window, 'vault_key') and
                       vault_window.vault_key)

            print(f"DEBUG: Final check - has_data: {has_data}, has_key: {has_key}")

            return has_data and has_key

        except Exception as e:
            print(f"DEBUG: Error in vault check: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_vault_from_main_app(self):
        """Load vault data from main app if available"""
        try:
            if self.main_app and hasattr(self.main_app, 'vault_window'):
                vault_window = self.main_app.vault_window
                self.vault_data = vault_window.vault_data.get("data", {})
                self.vault_key = vault_window.vault_key
                print("Successfully loaded vault data from main app")
            else:
                print("Failed to load vault data from main app")
        except Exception as e:
            print(f"Error loading vault data: {e}")

    def verify_vault_password(self):
        """Verify vault password and load accounts"""
        password = self.password_input.text()

        if not password:
            self.show_error("Please enter your vault password")
            return

        try:
            from core.vault_manager import user_verification, load_vault
            from config import get_auth_path
            import json

            auth_path = get_auth_path()
            with open(auth_path, 'r') as f:
                auth_data = json.load(f)
            username = auth_data.get("username")

            vault_key, verified_username = user_verification(username, password)

            if vault_key:
                self.vault_key = vault_key
                self.vault_data = load_vault(vault_key)
                self.show_account_list()
            else:
                self.show_error("Invalid vault password")

        except Exception as e:
            print(f"Vault unlock error: {e}")
            self.show_error("Failed to unlock vault")

    def show_account_list(self):
        """Show list of Valorant accounts with proper styling"""
        self.clear_layout()

        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        # Logo
        from gui.widgets.modern_widgets import LogoWidget
        logo_label = LogoWidget()
        title_layout.addWidget(logo_label)

        # App title
        app_title = QLabel("TheVault")
        app_title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title.setStyleSheet("color: #ffffff; background: transparent;")

        # Subtitle
        subtitle = QLabel("Select Valorant Account")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitle")
        subtitle.setStyleSheet("color: #b0b0b0; background: transparent;")

        title_layout.addWidget(app_title)
        title_layout.addWidget(subtitle)

        # Create title
        title_widget = QWidget()
        title_widget.setObjectName("titleWidget")
        title_widget.setLayout(title_layout)
        self.layout.addWidget(title_widget)

        self.layout.addSpacing(10)

        # Find Valorant accounts
        accounts = self.find_valorant_accounts()

        if not accounts:
            no_accounts = QLabel("No Valorant accounts found")
            no_accounts.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_accounts.setStyleSheet("color: #888888; font-size: 14px; background: transparent;")
            self.layout.addWidget(no_accounts)

            instruction = QLabel("Create accounts in folders named:\n'Valorant', 'valorant', or 'val'")
            instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
            instruction.setStyleSheet("color: #b0b0b0; font-size: 12px; font-style: italic; background: transparent;")
            self.layout.addWidget(instruction)
        else:
            # scrollable area for accounts
            from PyQt6.QtWidgets import QScrollArea

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFixedHeight(220)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background: transparent;
                }
                QScrollArea > QWidget > QWidget {
                    background: transparent;
                }
                QScrollBar:vertical {
                    background: rgba(255, 255, 255, 0.1);
                    width: 12px;
                    border-radius: 6px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background: rgba(255, 255, 255, 0.5);
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0px;
                }
            """)

            # widget to hold account buttons
            accounts_widget = QWidget()
            accounts_widget.setStyleSheet("background: transparent;")
            accounts_layout = QVBoxLayout(accounts_widget)
            accounts_layout.setSpacing(8)
            accounts_layout.setContentsMargins(5, 5, 5, 5)

            # Add account buttons
            for account in accounts:
                account_btn = QPushButton(account['title'])
                account_btn.setFixedHeight(40)
                account_btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(255, 255, 255, 0.08);
                        border: 1px solid rgba(255, 255, 255, 0.15);
                        border-radius: 8px;
                        color: #ffffff;
                        font-weight: bold;
                        font-size: 12px;
                        text-align: left;
                        padding-left: 15px;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.15);
                        border: 1px solid rgba(255, 255, 255, 0.25);
                    }
                    QPushButton:pressed {
                        background: rgba(255, 255, 255, 0.2);
                    }
                """)
                account_btn.clicked.connect(lambda checked, acc=account: self.select_account(acc))
                accounts_layout.addWidget(account_btn)

            accounts_layout.addStretch()

            scroll_area.setWidget(accounts_widget)
            self.layout.addWidget(scroll_area)

        self.layout.addSpacing(25)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 2px solid rgba(255, 255, 255, 0.25);
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.35);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        cancel_btn.clicked.connect(self.close_overlay)
        self.layout.addWidget(cancel_btn)

    def find_valorant_accounts(self):
        """Find accounts only in Valorant-related folders"""
        accounts = []
        valorant_folders = ['valorant', 'Valorant', 'val']

        for folder_name, folder_data in self.vault_data.items():
            if folder_name not in valorant_folders:
                continue

            entries = folder_data.get("entries", [])

            for entry in entries:
                username = None
                password = None
                title = None

                # Find username
                for field in ['Username', 'username', 'User', 'user', 'Email', 'email']:
                    if field in entry and entry[field]:
                        username = entry[field]
                        break

                # Find password
                for field in ['Password', 'password', 'Pass', 'pass']:
                    if field in entry and entry[field]:
                        password = entry[field]
                        break

                # Find title
                for field in ['Title', 'title', 'Name', 'name']:
                    if field in entry and entry[field]:
                        title = entry[field]
                        break

                # Use username as fallback if no title
                if not title:
                    title = username

                if username and password and title:
                    accounts.append({
                        'username': username,
                        'password': password,
                        'title': title,
                        'folder': folder_name
                    })

        return accounts

    def select_account(self, account):
        """Fill selected account into Riot Client"""
        print(f"Selected account: {account['title']}")

        try:
            import pyautogui
            import time

            self.hide()
            time.sleep(0.5)

            pyautogui.typewrite(account['username'])
            pyautogui.press('tab')
            pyautogui.typewrite(account['password'])
            pyautogui.press('enter')

            print("Account filled successfully!")

            from gui.analytics_manager import track_valorant_autofill_success
            track_valorant_autofill_success()

            self.close_overlay()


        except Exception as e:
            print(f"Fill error: {e}")
            from gui.analytics_manager import track_valorant_autofill_error
            track_valorant_autofill_error("autofill_failed")
            self.show_error("Failed to fill account")

    def show_error(self, message):
        if hasattr(self, 'error_label'):
            self.error_label.setText(message)
            self.error_label.show()

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def center_on_screen(self):
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def show_overlay(self):
        from gui.analytics_manager import track_valorant_autofill_triggered
        track_valorant_autofill_triggered()
        self.show()
        self.raise_()
        self.activateWindow()

    def close_overlay(self):
        from gui.analytics_manager import track_valorant_autofill_cancelled
        track_valorant_autofill_cancelled()

        self.hide()
        self.finished.emit()