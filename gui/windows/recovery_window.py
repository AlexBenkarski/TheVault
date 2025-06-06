from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui.widgets.modern_widgets import ModernButton, ModernLineEdit, LogoWidget, ModernDialog


class RecoveryWindow(QWidget):
    recovery_requested = pyqtSignal(str)
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

        page_title = QLabel("Account Recovery")
        page_title.setFont(QFont("Segoe UI", 14))
        page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_title.setObjectName("subtitle")

        title_layout.addWidget(app_title)
        title_layout.addWidget(page_title)

        # Recovery form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(0)

        # Error message label
        self.error_label = QLabel("")
        self.error_label.setFont(QFont("Segoe UI", 10))
        self.error_label.setStyleSheet("color: #ff4757;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)

        # Instructions
        instructions = QLabel("Enter your recovery key to reset your password:")
        instructions.setFont(QFont("Segoe UI", 11))
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #b0b0b0;")
        form_layout.addWidget(instructions)
        form_layout.addSpacing(15)

        # Recovery key field
        recovery_label = QLabel("Recovery Key")
        recovery_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.recovery_input = ModernLineEdit("XXXX-XXXX-XXXX-XXXX")

        form_layout.addWidget(recovery_label)
        form_layout.addWidget(self.recovery_input)
        form_layout.addSpacing(20)

        # Buttons
        button_layout = QHBoxLayout()

        self.back_btn = ModernButton("Back to Login", primary=False)
        self.back_btn.clicked.connect(self.handle_back_to_login)

        self.continue_btn = ModernButton("Continue", primary=True)
        self.continue_btn.clicked.connect(self.handle_recovery)

        button_layout.addWidget(self.back_btn)
        button_layout.addWidget(self.continue_btn)
        form_layout.addLayout(button_layout)

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

        version_layout.addWidget(version_label)
        layout.addLayout(version_layout)

        self.setLayout(layout)

    def handle_recovery(self):
        recovery_key = self.recovery_input.text().strip()
        self.clear_error_message()

        if not recovery_key:
            self.set_error_message("Please enter your recovery key")
            return

        self.recovery_requested.emit(recovery_key)

    def handle_back_to_login(self):
        self.back_to_login_requested.emit()

    def show_password_reset_dialog(self, recovery_key):
        # Create password reset dialog
        dialog = ModernDialog(self, "Create New Password")
        dialog.setFixedSize(420, 380)

        # Dialog styling
        dialog.setStyleSheet("""
            QDialog {
                background: #2d2d30;
                border: 2px solid #4CAF50;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
            }
        """)

        # Create layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("Create New Password")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; background: transparent;")
        layout.addWidget(header_label)

        layout.addSpacing(10)

        # New password field
        new_password_label = QLabel("New Password")
        new_password_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        self.new_password_input = ModernLineEdit("")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.textChanged.connect(self.validate_password_strength)

        layout.addWidget(new_password_label)
        layout.addWidget(self.new_password_input)
        layout.addSpacing(8)

        # Confirm password field
        confirm_password_label = QLabel("Confirm Password")
        confirm_password_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        self.confirm_password_input = ModernLineEdit("")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.textChanged.connect(self.validate_password_match)

        layout.addWidget(confirm_password_label)
        layout.addWidget(self.confirm_password_input)
        layout.addSpacing(20)

        # Password requirements
        req_container = QWidget()
        req_layout = QVBoxLayout(req_container)
        req_layout.setSpacing(2)
        req_layout.setContentsMargins(0, 0, 0, 0)

        self.req_length = QLabel("• At least 8 characters")
        self.req_length.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")

        self.req_upper = QLabel("• One uppercase letter")
        self.req_upper.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")

        self.req_symbol = QLabel("• One symbol")
        self.req_symbol.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")

        self.req_match = QLabel("• Passwords must match")
        self.req_match.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")

        req_layout.addWidget(self.req_length)
        req_layout.addWidget(self.req_upper)
        req_layout.addWidget(self.req_symbol)
        req_layout.addWidget(self.req_match)

        layout.addWidget(req_container)
        layout.addSpacing(20)

        # Error message
        self.dialog_error_label = QLabel("")
        self.dialog_error_label.setStyleSheet("color: #ff4757; font-size: 11px; background: transparent;")
        self.dialog_error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dialog_error_label.hide()
        layout.addWidget(self.dialog_error_label)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        reset_btn = ModernButton("Reset Password", primary=False)
        reset_btn.setStyleSheet("""
            ModernButton {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
            }
            ModernButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid #45a049;
            }
        """)
        reset_btn.clicked.connect(lambda: self.attempt_password_reset(recovery_key, dialog))

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(reset_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def validate_password_strength(self):
        password = self.new_password_input.text()

        # Length check
        if len(password) >= 8:
            self.req_length.setStyleSheet("color: #4CAF50; font-size: 10px; background: transparent;")
        else:
            self.req_length.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")

        # Uppercase check
        if any(c.isupper() for c in password):
            self.req_upper.setStyleSheet("color: #4CAF50; font-size: 10px; background: transparent;")
        else:
            self.req_upper.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")

        # Symbol check
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in symbols for c in password):
            self.req_symbol.setStyleSheet("color: #4CAF50; font-size: 10px; background: transparent;")
        else:
            self.req_symbol.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")

        self.validate_password_match()

    def validate_password_match(self):
        password = self.new_password_input.text()
        confirm = self.confirm_password_input.text()

        if confirm and password == confirm:
            self.req_match.setStyleSheet("color: #4CAF50; font-size: 10px; background: transparent;")
        elif confirm:
            self.req_match.setStyleSheet("color: #ff4757; font-size: 10px; background: transparent;")
        else:
            self.req_match.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")

    def attempt_password_reset(self, recovery_key, dialog):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        self.dialog_error_label.hide()

        # Basic validation
        if not new_password or not confirm_password:
            self.dialog_error_label.setText("Please fill in both password fields")
            self.dialog_error_label.show()
            return

        if new_password != confirm_password:
            self.dialog_error_label.setText("Passwords do not match")
            self.dialog_error_label.show()
            return

        # Use backend recovery function
        from core.vault_manager import recover_password
        success, message, new_recovery_key = recover_password(recovery_key, new_password, confirm_password)

        if success:
            dialog.accept()
            self.show_recovery_success_dialog(new_recovery_key)
        else:
            self.dialog_error_label.setText(message)
            self.dialog_error_label.show()

    def show_recovery_success_dialog(self, new_recovery_key):
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
        from PyQt6.QtCore import Qt

        # Create recovery key dialog
        dialog = ModernDialog(self, "Password Reset Successful")
        dialog.setFixedSize(420, 320)

        # Dialog styling
        dialog.setStyleSheet("""
            QDialog {
                background: #2d2d30;
                border: 2px solid #4CAF50;
                border-radius: 12px;
            }
            QLabel {
                background: transparent;
            }
        """)

        # Create layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Success message
        success_label = QLabel("Password reset successful!")
        success_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; background: transparent;")
        layout.addWidget(success_label)

        layout.addSpacing(10)

        # Recovery key info
        info_label = QLabel("Your new recovery key is:")
        info_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        layout.addWidget(info_label)

        layout.addSpacing(8)

        # Recovery key display
        self.success_recovery_display = QLabel("****-****-****-****")
        self.success_recovery_display.setStyleSheet("""
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 18px 25px;
            color: #ffffff;
            font-family: 'Courier New', monospace;
            font-size: 18px;
            font-weight: bold;
            min-height: 50px;
            max-width: 380px;
        """)
        self.success_recovery_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_recovery_display.setWordWrap(True)
        layout.addWidget(self.success_recovery_display)

        layout.addSpacing(12)

        # Show and Copy buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(15)

        show_btn = ModernButton("Show", primary=False)
        show_btn.setMinimumWidth(100)
        show_btn.clicked.connect(lambda: self.toggle_success_key_visibility(new_recovery_key))

        copy_btn = ModernButton("Copy", primary=False)
        copy_btn.setMinimumWidth(100)
        copy_btn.clicked.connect(lambda: self.copy_success_recovery_key(new_recovery_key))

        button_row.addStretch()
        button_row.addWidget(show_btn)
        button_row.addWidget(copy_btn)
        button_row.addStretch()
        layout.addLayout(button_row)

        layout.addSpacing(15)

        # Warning messages
        warning1 = QLabel("WARNING: Save this recovery key now!")
        warning1.setStyleSheet("color: #ff4757; font-size: 13px; font-weight: bold; background: transparent;")
        layout.addWidget(warning1)

        warning2 = QLabel("You will not be able to see it again.")
        warning2.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        layout.addWidget(warning2)

        warning3 = QLabel("Store it in a safe place separate from your vault.")
        warning3.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        layout.addWidget(warning3)

        warning4 = QLabel("You can use this key to recover your account if you forget your password.")
        warning4.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")
        layout.addWidget(warning4)

        layout.addSpacing(15)

        # Continue button
        continue_btn = ModernButton("I Have Saved My Recovery Key", primary=False)
        continue_btn.setMinimumHeight(50)
        continue_btn.setMinimumWidth(300)
        continue_btn.setStyleSheet("""
            ModernButton {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            ModernButton:hover {
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid #45a049;
            }
            ModernButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        continue_btn.clicked.connect(lambda: self.complete_recovery(dialog))

        # Center the button
        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(continue_btn)
        button_container.addStretch()
        layout.addLayout(button_container)

        dialog.exec()

    def toggle_success_key_visibility(self, recovery_key):
        current_text = self.success_recovery_display.text()
        if current_text == "****-****-****-****":
            self.success_recovery_display.setText(recovery_key)
        else:
            self.success_recovery_display.setText("****-****-****-****")

    def copy_success_recovery_key(self, recovery_key):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(recovery_key)

    def complete_recovery(self, dialog):
        dialog.accept()
        self.clear_inputs()
        self.back_to_login_requested.emit()

    def focus_first_input(self):
        self.recovery_input.setFocus()

    def clear_inputs(self):
        self.recovery_input.clear()

    def set_error_message(self, message):
        if message:
            self.error_label.setText(message)
            self.error_label.show()
        else:
            self.error_label.hide()

    def clear_error_message(self):
        self.error_label.hide()