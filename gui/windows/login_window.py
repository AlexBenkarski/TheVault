from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont
from gui.widgets.modern_widgets import ModernButton, ModernLineEdit, LogoWidget


class LoginWindow(QWidget):
    login_requested = pyqtSignal(str, str)
    forgot_password_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = QSettings("TheVault", "LoginPreferences")
        self.init_ui()
        self.load_remembered_username()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(60, 40, 60, 20)

        # Title section with logo
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        logo_label = LogoWidget()
        title_layout.addWidget(logo_label)

        app_title = QLabel("TheVault")
        app_title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Sign In")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setObjectName("subtitle")

        title_layout.addWidget(app_title)
        title_layout.addWidget(subtitle)

        # Login form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(5)

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

        # Password field
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.password_input = ModernLineEdit("")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Remember username checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setFont(QFont("Segoe UI", 10))
        self.remember_checkbox.setObjectName("rememberCheckbox")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.1);
            }
            QCheckBox::indicator:hover {
                border: 2px solid rgba(255, 255, 255, 0.5);
                background: rgba(255, 255, 255, 0.15);
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4CAF50;
                background: #4CAF50;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iNyIgdmlld0JveD0iMCAwIDEwIDciIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDMuNUwzLjUgNkw5IDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
        """)

        # Buttons
        self.login_btn = ModernButton("Login", primary=True)
        self.login_btn.clicked.connect(self.handle_login)

        self.forgot_password_btn = ModernButton("Forgot Password?", primary=False)
        self.forgot_password_btn.clicked.connect(self.handle_forgot_password)

        # Add form elements
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_checkbox)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.login_btn)
        form_layout.addSpacing(5)
        form_layout.addWidget(self.forgot_password_btn)

        # Main layout assembly
        layout.addLayout(title_layout)
        layout.addSpacing(15)
        layout.addLayout(form_layout)
        layout.addStretch()

        # Version number
        version_layout = QHBoxLayout()
        version_layout.addStretch()

        from gui.update_manager import get_current_version
        version_label = QLabel(f"v{get_current_version()}")
        version_label.setFont(QFont("Segoe UI", 9))
        version_label.setObjectName("versionLabel")

        version_layout.addWidget(version_label)
        layout.addLayout(version_layout)

        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            return

        # Handle remember username
        if self.remember_checkbox.isChecked():
            self.settings.setValue("remembered_username", username)
            self.settings.setValue("remember_me", True)
        else:
            self.settings.remove("remembered_username")
            self.settings.setValue("remember_me", False)

        self.login_requested.emit(username, password)

    def handle_forgot_password(self):
        self.forgot_password_requested.emit()

    def focus_first_input(self):
        self.username_input.setFocus()

    def clear_inputs(self):
        if not self.remember_checkbox.isChecked():
            self.username_input.clear()
        self.password_input.clear()

    def load_remembered_username(self):
        remember_me = self.settings.value("remember_me", False, type=bool)
        if remember_me:
            remembered_username = self.settings.value("remembered_username", "", type=str)
            if remembered_username:
                self.username_input.setText(remembered_username)
                self.remember_checkbox.setChecked(True)

    def set_error_message(self, message):
        if message:
            self.error_label.setText(message)
            self.error_label.show()
        else:
            self.error_label.hide()

    def clear_error_message(self):
        self.error_label.hide()