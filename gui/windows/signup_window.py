from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import os
from gui.widgets.modern_widgets import ModernButton, ModernLineEdit, LogoWidget, ModernDialog


class SignupWindow(QWidget):
    signup_requested = pyqtSignal(str, str, str, str)
    back_to_login_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(60, 20, 60, 20)

        # Title section with logo
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        logo_label = LogoWidget()
        title_layout.addWidget(logo_label)

        app_title = QLabel("TheVault")
        app_title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        page_title = QLabel("Sign Up")
        page_title.setFont(QFont("Segoe UI", 14))
        page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_title.setObjectName("subtitle")

        title_layout.addWidget(app_title)
        title_layout.addWidget(page_title)

        # Signup form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(0)

        # Error message label
        self.error_label = QLabel("")
        self.error_label.setFont(QFont("Segoe UI", 10))
        self.error_label.setStyleSheet("color: #ff4757;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)

        # Username field
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.username_input = ModernLineEdit("")

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addSpacing(8)

        # Password field
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.password_input = ModernLineEdit("")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(8)

        # Confirm password field
        confirm_label = QLabel("Confirm Password")
        confirm_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.confirm_input = ModernLineEdit("")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.confirm_input)
        form_layout.addSpacing(8)

        # Vault location field
        location_label = QLabel("Vault Location")
        location_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.location_input = ModernLineEdit("")
        self.location_input.setReadOnly(True)
        self.location_input.setText(self.get_default_vault_path())

        # Browse button
        self.browse_btn = ModernButton("Browse", primary=False)
        self.browse_btn.clicked.connect(self.browse_vault_location)

        form_layout.addWidget(location_label)
        form_layout.addWidget(self.location_input)
        form_layout.addWidget(self.browse_btn)
        form_layout.addSpacing(15)

        # Create account button
        self.signup_btn = ModernButton("Create Account", primary=True)
        self.signup_btn.clicked.connect(self.handle_signup)
        form_layout.addWidget(self.signup_btn)

        # Main layout assembly
        layout.addLayout(title_layout)
        layout.addSpacing(10)
        layout.addLayout(form_layout)
        layout.addStretch()

        # Version number
        version_layout = QHBoxLayout()
        version_layout.addStretch()

        from gui.update_manager import get_current_version
        version_label = QLabel(f"v{get_current_version()}")
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setObjectName("versionLabel")

        self.username_input.returnPressed.connect(self.handle_signup)
        self.password_input.returnPressed.connect(self.handle_signup)
        self.confirm_input.returnPressed.connect(self.handle_signup)

        version_layout.addWidget(version_label)
        layout.addLayout(version_layout)

        self.setLayout(layout)

    def get_default_vault_path(self):
        from config import is_dev_environment, get_default_vault_directory

        if is_dev_environment():
            dev_path = get_default_vault_directory()
            if dev_path:
                return dev_path

        # Try OneDrive first
        onedrive_path = os.environ.get('ONEDRIVE')
        if onedrive_path and os.path.exists(onedrive_path):
            return os.path.join(onedrive_path, 'TheVault')

        # Fallback to Documents
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        return os.path.join(documents_path, "TheVault")

    def browse_vault_location(self):
        current_path = self.location_input.text()

        # Open folder selection dialog
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Vault Location",
            os.path.dirname(current_path) if current_path else os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )

        if selected_dir:
            vault_path = os.path.join(selected_dir, "TheVault")
            self.location_input.setText(vault_path)

    def show_password_requirements(self):
        # Create password requirements dialog
        dialog = ModernDialog(self, "Password Requirements")
        dialog.setFixedSize(400, 300)

        # Create layout
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame, QHBoxLayout

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("Password Requirements")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; background: transparent;")
        layout.addWidget(header_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background: rgba(255, 255, 255, 0.2); border: none; max-height: 1px;")
        layout.addWidget(separator)

        layout.addSpacing(10)

        # Requirements info
        info_text = QLabel("Your password must meet the following requirements:")
        info_text.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        info_text.setWordWrap(True)
        layout.addWidget(info_text)

        layout.addSpacing(10)

        # Requirements list
        requirements = [
            "• At least 8 characters long",
            "• Contains at least one uppercase letter (A-Z)",
            "• Contains at least one symbol (!@#$%^&*)",
        ]

        for req in requirements:
            req_label = QLabel(req)
            req_label.setStyleSheet("color: #ffffff; font-size: 11px; padding-left: 10px; background: transparent;")
            layout.addWidget(req_label)

        layout.addSpacing(15)

        # Example section
        example_label = QLabel("Examples of valid passwords:")
        example_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold; background: transparent;")
        layout.addWidget(example_label)

        examples = [
            "• MyPassword123!",
            "• SecureVault$2024",
            "• P@ssw0rd#Safe"
        ]

        for example in examples:
            ex_label = QLabel(example)
            ex_label.setStyleSheet("color: #ffffff; font-size: 10px; padding-left: 10px; font-family: monospace; background: transparent;")
            layout.addWidget(ex_label)

        layout.addStretch()

        # Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = ModernButton("Got It", primary=True)
        ok_btn.clicked.connect(dialog.accept)

        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def handle_signup(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        vault_location = self.location_input.text().strip()

        self.clear_error_message()

        # Basic validation
        if not username or not password or not confirm_password:
            self.set_error_message("Please fill in all fields")
            return

        if len(username) < 3:
            self.set_error_message("Username must be at least 3 characters")
            return

        if password != confirm_password:
            self.set_error_message("Passwords do not match")
            return

        # Check password strength
        from core.vault_manager import is_password_strong
        if not is_password_strong(password):
            self.set_error_message("Password does not meet requirements")
            self.show_password_requirements()
            return

        if not vault_location:
            self.set_error_message("Please select a vault location")
            return

        self.signup_requested.emit(username, password, confirm_password, vault_location)

    def focus_first_input(self):
        self.username_input.setFocus()

    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()

    def set_error_message(self, message):
        if message:
            self.error_label.setText(message)
            self.error_label.show()
        else:
            self.error_label.hide()

    def clear_error_message(self):
        self.error_label.hide()