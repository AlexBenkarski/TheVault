import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QStackedWidget, \
    QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from gui.windows.login_window import LoginWindow
from gui.windows.signup_window import SignupWindow
from gui.windows.recovery_window import RecoveryWindow
from gui.windows.vault_window import VaultWindow
from gui.styles.themes import apply_theme


class TheVaultApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self._init_window()
        self._create_ui()
        self._init_windows()

        apply_theme(self)
        self._setup_startup_tasks()
        self._determine_initial_view()

        self.drag_position = None

    # =============================================================================
    # INITIALIZATION METHODS
    # =============================================================================

    def _init_window(self):
        self.set_application_icon()

        # Create frameless window with rounded corners
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set window sizes for different views
        self.login_size = (450, 650)
        self.vault_size = (1200, 800)

        self.setGeometry(100, 100, *self.login_size)
        self.setMinimumSize(400, 600)
        self.center_window()

    def _create_ui(self):
        # Create main container widget
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)

        # Add title bar and content area
        self._create_title_bar(main_layout)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

    def _create_title_bar(self, main_layout):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setObjectName("titleBar")

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(15, 0, 15, 0)
        title_bar.setLayout(title_layout)

        self._create_vault_controls(title_layout)
        self._create_user_controls(title_layout)
        self._create_window_controls(title_layout)

        main_layout.addWidget(title_bar)

        # Enable title bar dragging
        title_bar.mousePressEvent = self.mouse_press_event
        title_bar.mouseMoveEvent = self.mouse_move_event

    def _create_vault_controls(self, title_layout):
        self.vault_controls = QWidget()
        vault_layout = QHBoxLayout(self.vault_controls)
        vault_layout.setContentsMargins(0, 0, 0, 0)
        vault_layout.setSpacing(5)

        # Add logo and app title
        from gui.widgets.modern_widgets import LogoWidget
        self.vault_logo = LogoWidget()
        self.vault_logo.setFixedSize(28, 28)
        self.vault_logo.setScaledContents(True)

        self.vault_title = QLabel("The Vault")
        self.vault_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.vault_title.setStyleSheet("color: #ffffff;")

        vault_layout.addWidget(self.vault_logo)
        vault_layout.addWidget(self.vault_title)

        self.vault_controls.hide()
        title_layout.addWidget(self.vault_controls)

    def _create_user_controls(self, title_layout):
        self.user_controls = QWidget()
        user_layout = QHBoxLayout(self.user_controls)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(10)

        # Add user profile button
        self.user_profile_btn = QPushButton("👤 User")
        self.user_profile_btn.setFixedSize(80, 30)
        self.user_profile_btn.setObjectName("windowControl")

        user_layout.addWidget(self.user_profile_btn)
        self.user_controls.hide()

        title_layout.addStretch()
        title_layout.addWidget(self.user_controls)

    def _create_window_controls(self, title_layout):
        # Add minimize and close buttons
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setObjectName("windowControl")
        minimize_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setObjectName("closeControl")
        close_btn.clicked.connect(self.close)

        title_layout.addWidget(minimize_btn)
        title_layout.addWidget(close_btn)

    def _init_windows(self):
        # Create login window
        self.login_window = LoginWindow()
        self.login_window.login_requested.connect(self.handle_login)
        self.login_window.forgot_password_requested.connect(self.show_recovery)

        # Create signup window
        self.signup_window = SignupWindow()
        self.signup_window.signup_requested.connect(self.handle_signup)
        self.signup_window.back_to_login_requested.connect(self.show_login)

        # Create recovery window
        self.recovery_window = RecoveryWindow()
        self.recovery_window.recovery_requested.connect(self.handle_recovery)
        self.recovery_window.back_to_login_requested.connect(self.show_login)

        # Create vault window
        self.vault_window = VaultWindow()

        # Add all windows to stack
        for window in [self.login_window, self.signup_window, self.recovery_window, self.vault_window]:
            self.stacked_widget.addWidget(window)

    def _setup_startup_tasks(self):
        # Check for updates after 2 second delay
        QTimer.singleShot(2000, self._check_for_updates_startup)

        # Check if app was just updated
        from gui.update_manager import check_post_update_launch
        check_post_update_launch(self)

    # =============================================================================
    # WINDOW MANAGEMENT METHODS
    # =============================================================================

    def center_window(self):
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def resize_window(self, width, height):
        current_pos = self.pos()
        self.setGeometry(current_pos.x(), current_pos.y(), width, height)
        self.setMinimumSize(width - 50, height - 50)
        self.center_window()

    def mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouse_move_event(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def set_application_icon(self):
        # Find logo file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if 'gui' in current_dir:
            gui_dir = current_dir if current_dir.endswith('gui') else os.path.dirname(current_dir)
            project_root = os.path.dirname(gui_dir)
        else:
            project_root = current_dir

        logo_path = os.path.join(project_root, "assets", "logo.png")

        if os.path.exists(logo_path):
            icon = QIcon(logo_path)
            app = QApplication.instance()
            if app:
                app.setWindowIcon(icon)
            self.setWindowIcon(icon)

    # =============================================================================
    # VIEW NAVIGATION METHODS
    # =============================================================================

    def _determine_initial_view(self):
        from config import get_auth_path
        auth_path = get_auth_path()

        if auth_path and os.path.exists(auth_path):
            self.show_login()
        else:
            self.show_signup()

    def show_login(self):
        self._switch_to_auth_view(self.login_window)
        self.login_window.focus_first_input()
        self.login_window.clear_inputs()

    def show_signup(self):
        self._switch_to_auth_view(self.signup_window)
        self.signup_window.focus_first_input()

    def show_recovery(self):
        self._switch_to_auth_view(self.recovery_window)
        self.recovery_window.focus_first_input()
        self.recovery_window.clear_inputs()

    def _switch_to_auth_view(self, window):
        # Switch to login-sized window and hide vault controls
        self.resize_window(*self.login_size)
        self.vault_controls.hide()
        self.user_controls.hide()
        self.stacked_widget.setCurrentWidget(window)

    def show_vault(self, username, vault_data, vault_key):
        # Resize to vault size and show controls
        self.resize_window(*self.vault_size)
        self.vault_controls.show()
        self.user_controls.show()

        # Update user button text and connect to settings
        self.user_profile_btn.setText(f"👤 {username}")

        try:
            self.user_profile_btn.clicked.disconnect()
        except:
            pass
        self.user_profile_btn.clicked.connect(self.vault_window.show_settings_dialog)

        # Load vault data and switch to vault view
        self.vault_window.load_vault_data(vault_data, username, vault_key)
        self.stacked_widget.setCurrentWidget(self.vault_window)

    # =============================================================================
    # AUTHENTICATION HANDLERS
    # =============================================================================

    def handle_login(self, username, password):
        self.login_window.clear_error_message()

        if not username or not password:
            self.login_window.set_error_message("Please enter both username and password")
            return

        from core.vault_manager import user_verification, load_vault

        vault_key, verified_username = user_verification(username, password)

        if vault_key and verified_username:
            vault_data = load_vault(vault_key)
            self.show_vault(verified_username, vault_data, vault_key)
        else:
            self.login_window.set_error_message("Invalid username or password")

    def handle_signup(self, username, password, confirm_password, vault_location):
        # Basic validation checks
        if not all([username, password, confirm_password]):
            self.signup_window.set_error_message("Please fill in all fields")
            return

        if password != confirm_password:
            self.signup_window.set_error_message("Passwords do not match")
            return

        if len(username) < 3:
            self.signup_window.set_error_message("Username must be at least 3 characters")
            return

        # Update config paths first
        from config import update_config_paths
        if not update_config_paths(vault_location):
            self.signup_window.set_error_message("Failed to update configuration.")
            return

        # Create new account without vault_location (uses updated config)
        from core.vault_manager import handle_first_setup
        success, message = handle_first_setup(username, password)

        if success:
            recovery_key = message
            self._show_recovery_key_dialog(recovery_key)
        else:
            self.signup_window.set_error_message(message)

    def handle_recovery(self, recovery_key):
        self.recovery_window.clear_error_message()

        from config import get_auth_path
        import json
        import base64

        auth_path = get_auth_path()
        if not os.path.exists(auth_path):
            self.recovery_window.set_error_message("No account found for recovery")
            return

        with open(auth_path, 'r') as f:
            auth_data = json.load(f)

        if "recovery_salt" not in auth_data or "recovery_hash" not in auth_data:
            self.recovery_window.set_error_message("Recovery not available for this account")
            return

        # Verify recovery key against stored hash
        recovery_salt = base64.b64decode(auth_data["recovery_salt"])
        stored_hash = auth_data["recovery_hash"]

        from auth.auth_manager import verify_recovery_key
        if verify_recovery_key(recovery_key.upper(), stored_hash, recovery_salt):
            self.recovery_window.show_password_reset_dialog(recovery_key)
        else:
            self.recovery_window.set_error_message("Invalid recovery key")

    # =============================================================================
    # DIALOG METHODS
    # =============================================================================

    def _show_recovery_key_dialog(self, recovery_key):
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
        from PyQt6.QtCore import Qt

        dialog = ModernDialog(self, "IMPORTANT: Save Your Recovery Key")
        dialog.setFixedSize(420, 380)

        # Apply dialog styling
        dialog.setStyleSheet("""
            QDialog {
                background: #2d2d30;
                border: 2px solid #4CAF50;
                border-radius: 12px;
            }
            QLabel { background: transparent; }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Add success message
        success_label = QLabel("Account created successfully!")
        success_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(success_label)

        layout.addSpacing(10)

        # Add recovery key info label
        info_label = QLabel("Your recovery key is:")
        info_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(info_label)

        # Add masked recovery key display
        self.recovery_key_display = QLabel("****-****-****-****")
        self.recovery_key_display.setStyleSheet("""
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
        self.recovery_key_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.recovery_key_display)

        self._add_recovery_key_buttons(layout, recovery_key)
        self._add_recovery_warnings(layout)
        self._add_continue_button(layout, dialog)

        dialog.exec()

    def _add_recovery_key_buttons(self, layout, recovery_key):
        from gui.widgets.modern_widgets import ModernButton

        button_row = QHBoxLayout()
        button_row.setSpacing(15)

        # Add show and copy buttons
        show_btn = ModernButton("Show", primary=False)
        show_btn.setMinimumWidth(100)
        show_btn.clicked.connect(lambda: self._toggle_recovery_key_visibility(recovery_key))

        copy_btn = ModernButton("Copy", primary=False)
        copy_btn.setMinimumWidth(100)
        copy_btn.clicked.connect(lambda: self._copy_recovery_key(recovery_key))

        button_row.addStretch()
        button_row.addWidget(show_btn)
        button_row.addWidget(copy_btn)
        button_row.addStretch()

        layout.addLayout(button_row)
        layout.addSpacing(15)

    def _add_recovery_warnings(self, layout):
        warnings = [
            ("WARNING: Save this recovery key now!", "#ff4757", "bold"),
            ("You will not be able to see it again.", "#ffffff", "normal"),
            ("Store it in a safe place separate from your vault.", "#ffffff", "normal"),
            ("You can use this key to recover your account if you forget your password.", "#ffffff", "normal")
        ]

        # Add warning labels
        for text, color, weight in warnings:
            label = QLabel(text)
            font_weight = "font-weight: bold;" if weight == "bold" else ""
            label.setStyleSheet(f"color: {color}; font-size: 12px; {font_weight}")
            layout.addWidget(label)

        layout.addSpacing(15)

    def _add_continue_button(self, layout, dialog):
        from gui.widgets.modern_widgets import ModernButton

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
        continue_btn.clicked.connect(lambda: self._complete_signup(dialog))

        # Center the continue button
        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(continue_btn)
        button_container.addStretch()
        layout.addLayout(button_container)

    def _toggle_recovery_key_visibility(self, recovery_key):
        current_text = self.recovery_key_display.text()
        if current_text == "****-****-****-****":
            self.recovery_key_display.setText(recovery_key)
        else:
            self.recovery_key_display.setText("****-****-****-****")

    def _copy_recovery_key(self, recovery_key):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(recovery_key)

    def _complete_signup(self, dialog):
        dialog.accept()
        self.signup_window.clear_inputs()
        self.show_login()

    # =============================================================================
    # UPDATE MANAGEMENT
    # =============================================================================

    def _check_for_updates_startup(self):
        from gui.update_manager import check_for_updates, show_update_popup
        update_info = check_for_updates()

        if update_info['available']:
            show_update_popup(self, update_info)

    # =============================================================================
    # EVENT HANDLERS
    # =============================================================================

    def closeEvent(self, event):
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Set app properties
    app.setApplicationName("TheVault")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("AlexBenkarski")

    # Create and show main window
    window = TheVaultApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()