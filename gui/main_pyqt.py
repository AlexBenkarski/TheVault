import atexit
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QStackedWidget, \
    QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from dev_tools.dev_manager import persistent_dev_cli
from gui.analytics_manager import AnalyticsManager
from gui.update_manager import get_current_version, load_secrets
from gui.windows.login_window import LoginWindow
from gui.windows.signup_window import SignupWindow
from gui.windows.recovery_window import RecoveryWindow
from gui.windows.vault_window import VaultWindow
from gui.styles.themes import apply_theme
import threading
import time
from datetime import datetime
from tray import SystemTrayManager
from PyQt6.QtWidgets import QSystemTrayIcon
from game_integration.tray_bridge import GameIntegrationBridge
from game_integration.background_monitor.epic_detector import EpicDetector



class TheVaultApp(QMainWindow):
    def __init__(self):
        startup_start = time.time()
        super().__init__()

        self.session_start = time.time()
        atexit.register(self._cleanup_session)

        self._init_window()
        self._create_ui()
        self._init_windows()

        apply_theme(self)
        self._setup_startup_tasks()
        self._determine_initial_view()

        startup_time = (time.time() - startup_start) * 1000
        from gui.analytics_manager import update_metric
        update_metric("performance.avg_startup_time_ms", startup_time)

        self._init_game_integration_bridge()
        self._init_system_tray()
        self._setup_signal_checking()

        # Start monitoring after basic init
        self.start_game_monitoring()

        self.drag_position = None

    def _setup_signal_checking(self):
        """Check for signals from other instances"""
        from PyQt6.QtCore import QTimer
        import tempfile
        import os

        self.signal_timer = QTimer()
        self.signal_timer.timeout.connect(self._check_for_signals)
        self.signal_timer.start(1000)

    def _check_for_signals(self):
        """Check if another instance wants us to show"""
        import tempfile
        import os

        signal_file = os.path.join(tempfile.gettempdir(), "thevault_show.signal")

        if os.path.exists(signal_file):
            try:
                self.show_main_window()
                os.remove(signal_file)
            except:
                pass

    def show_main_window(self):
        """Show and raise the main window (called by tray or signal)"""
        self.show()
        self.raise_()
        self.activateWindow()
        if self.isMinimized():
            self.showNormal()

    def start_game_monitoring(self):
        """Start background game detection for Riot and Epic"""
        # Existing Riot detection
        from game_integration.background_monitor.riot_detector import RiotDetector

        self.riot_detector = RiotDetector()
        self.riot_detector.username_field_detected.connect(self.show_vault_overlay)
        self.riot_detector.start_monitoring()

        # New Epic detection
        self.epic_detector = EpicDetector()
        self.epic_detector.username_field_detected.connect(self.show_epic_overlay)
        self.epic_detector.start_monitoring()

    def _init_game_integration_bridge(self):
        """Initialize bridge for existing game integration systems"""
        self.game_bridge = GameIntegrationBridge()

        if hasattr(self, 'riot_detector'):
            self.game_bridge.set_riot_detector(self.riot_detector)

        if hasattr(self, 'epic_detector'):
            self.game_bridge.set_epic_detector(self.epic_detector)

        print("Game integration bridge initialized with Riot and Epic")

    def _init_system_tray(self):
        """Initialize system tray functionality"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_manager = SystemTrayManager(self, self.game_bridge)

            if self.tray_manager.show():
                self.tray_manager.start_monitoring()


                if '--minimized' in sys.argv:
                    self.hide()
                    self.tray_manager.show_notification(
                        "TheVault Started",
                        "Running in background. Right-click tray icon for options.",
                        duration=4000
                    )
                    return

    def show_vault_overlay(self):
        """Show the vault overlay when username field detected"""
        print("=== SIGNAL RECEIVED - SHOWING OVERLAY ===")

        try:
            from game_integration.background_monitor.overlay_manager import VaultOverlay

            print(f"=== MAIN APP DEBUG ===")
            print(f"self = {self}")
            print(f"type(self) = {type(self)}")
            print(f"About to pass self to VaultOverlay...")

            if not hasattr(self, 'overlay') or self.overlay is None:
                print("Creating new overlay...")
                self.overlay = VaultOverlay(main_app=self)
                self.overlay.finished.connect(self.riot_detector.reset_overlay_flag)

            self.overlay.show_overlay()

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    def show_epic_overlay(self):
        """Show Epic overlay - either direct autofill or mode selection"""
        print("=== EPIC SIGNAL RECEIVED ===")

        try:
            from game_integration.background_monitor.overlay_manager import VaultOverlay

            if not hasattr(self, 'epic_overlay') or self.epic_overlay is None:
                print("Creating new Epic overlay...")
                self.epic_overlay = VaultOverlay(main_app=self)
                self.epic_overlay.finished.connect(self.epic_detector.reset_overlay_flag)

            # Check if Epic is already standard size
            if self.epic_detector.is_epic_standard_size():
                print("Epic is standard size - showing direct autofill")
                # Skip popup, go straight to vault check
                if self.epic_overlay.is_vault_already_open():
                    self.epic_overlay.load_vault_from_main_app()
                    self.epic_overlay.show_epic_account_list()
                else:
                    self.epic_overlay.show_vault_login()
                    self.epic_overlay.post_login_action = 'epic'
            else:
                print("Epic needs resize - showing mode selection")
                # Show resize popup
                self.epic_overlay.show_epic_mode_selection()

            # Track Epic analytics
            from gui.analytics_manager import track_epic_autofill_triggered
            track_epic_autofill_triggered()

            self.epic_overlay.show()
            self.epic_overlay.raise_()
            self.epic_overlay.activateWindow()

        except Exception as e:
            print(f"ERROR showing Epic overlay: {e}")
            import traceback
            traceback.print_exc()

    # =============================================================================
    # DEV MODE METHODS
    # =============================================================================

    @pyqtSlot()
    def load_vault_with_mock_data(self):
        from dev_tools.dev_manager import get_current_mock_data
        mock_data = get_current_mock_data()
        self.show_vault("DEV_MODE", mock_data, b"mock_key")

    def show_vault_with_settings(self):
        """Open vault and immediately show settings dialog"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("small")
        self.load_vault_with_mock_data()
        QTimer.singleShot(100, self.vault_window.show_settings_dialog)

    def customEvent(self, event):
        """Handle dev command events from CLI thread"""
        if hasattr(event, 'command_id'):
            command_id = event.command_id
            print(f"Processing dev command: {command_id}")

            if not self.isVisible():
                self.show()

            if command_id == "1.1":  # Main Windows
                self.show_login()
                # Force proper window sizing for auth views
                QTimer.singleShot(50, lambda: self.resize_window(*self.login_size))
            elif command_id == "1.2":
                self.show_signup()
                QTimer.singleShot(50, lambda: self.resize_window(*self.login_size))
            elif command_id == "1.3":
                self.show_recovery()
                QTimer.singleShot(50, lambda: self.resize_window(*self.login_size))
            elif command_id == "1.4":
                self.load_vault_with_mock_data()
            elif command_id == "2.1":  # Popups & Dialogs
                self.show_vault_with_settings()
            elif command_id == "2.2":
                self.show_vault_with_add_folder()
            elif command_id == "2.3":
                self.show_vault_with_add_entry()
            elif command_id == "2.4":
                self.show_vault_with_edit_entry()
            elif command_id == "2.5":
                self.show_vault_with_delete_confirmation()
            elif command_id == "2.6":
                self.show_recovery_key_dialog_standalone()
            elif command_id == "2.7":
                self.show_password_reset_dialog_standalone()
            elif command_id == "2.8":
                self.show_update_available_popup()
            elif command_id == "2.9":
                self.show_update_complete_popup()
            elif command_id == "3.1":
                self.load_empty_vault()
            elif command_id == "3.2":
                self.load_large_vault()
            elif command_id == "3.3":
                self.load_massive_vault()
            elif command_id == "4.1":
                self.load_small_preset()
            elif command_id == "4.2":
                self.load_large_preset()
            else:
                print(f"Command {command_id} not implemented yet")

    def show_vault_with_add_folder(self):
        """Open vault and show add folder popup"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("small")
        self.load_vault_with_mock_data()
        QTimer.singleShot(100, self.vault_window.add_folder)

    def show_vault_with_add_entry(self):
        """Open vault and show add entry popup"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("small")
        self.load_vault_with_mock_data()
        QTimer.singleShot(100, self._dev_add_entry_with_folder)

    def _dev_add_entry_with_folder(self):
        """Helper: select first folder and show add entry"""
        if self.vault_window.vault_data.get("data"):
            folders = list(self.vault_window.vault_data["data"].keys())
            if folders:
                self.vault_window.select_folder(folders[0])
                QTimer.singleShot(50, self.vault_window.add_entry_to_folder)

    def show_update_available_popup(self):
        """Show update available dialog"""
        # Track update notification seen
        from gui.analytics_manager import increment_counter
        increment_counter("feature_usage.update_notifications_seen")

        from gui.update_manager import show_update_popup
        # Mock update info
        mock_update = {
            'available': True,
            'version': '2.1.0',
            'download_url': 'https://example.com/update.exe',
            'patch_notes': '# New Features\n- Dev Mode\n- Better UI\n- Bug fixes',
            'release_name': 'v2.1.0',
            'asset_name': 'Vault.exe'
        }
        show_update_popup(self, mock_update)

    def show_update_complete_popup(self):
        """Show update complete dialog"""
        from gui.update_manager import show_post_update_popup
        mock_notes = "# Update Complete!\n- Dev mode added\n- Performance improvements\n- UI enhancements"
        show_post_update_popup(self, mock_notes)

    def show_vault_with_edit_entry(self):
        """Open vault and show edit entry popup"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("small")
        self.load_vault_with_mock_data()
        QTimer.singleShot(100, self._dev_edit_entry_with_data)

    def _dev_edit_entry_with_data(self):
        """Helper: select folder, entry, and show edit dialog"""
        if self.vault_window.vault_data.get("data"):
            folders = list(self.vault_window.vault_data["data"].keys())
            if folders:
                folder_name = folders[0]
                self.vault_window.select_folder(folder_name)

                folder_data = self.vault_window.vault_data["data"][folder_name]
                entries = folder_data.get("entries", [])
                if entries:
                    QTimer.singleShot(50, lambda: self.vault_window.edit_entry(0, entries[0]))

    def show_vault_with_delete_confirmation(self):
        """Open vault and show delete confirmation"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("small")
        self.load_vault_with_mock_data()
        QTimer.singleShot(100, self._dev_delete_entry_with_data)

    def _dev_delete_entry_with_data(self):
        """Helper: select folder, entry, and show delete dialog"""
        if self.vault_window.vault_data.get("data"):
            folders = list(self.vault_window.vault_data["data"].keys())
            if folders:
                folder_name = folders[0]
                self.vault_window.select_folder(folder_name)

                folder_data = self.vault_window.vault_data["data"][folder_name]
                entries = folder_data.get("entries", [])
                if entries:
                    QTimer.singleShot(50, lambda: self.vault_window.delete_entry(0))

    def show_recovery_key_dialog_standalone(self):
        """Show recovery key dialog as standalone (for dev testing)"""
        # Generate a mock recovery key for display
        mock_recovery_key = "ABCD-EFGH-IJKL-MNOP"
        self._show_recovery_key_dialog(mock_recovery_key)

    def show_password_reset_dialog_standalone(self):
        """Show password reset dialog as standalone (for dev testing)"""
        self.show_recovery()
        QTimer.singleShot(200, self._dev_trigger_password_reset)

    def _dev_trigger_password_reset(self):
        """Helper: automatically trigger password reset dialog"""
        # Generate a mock recovery key and trigger the reset dialog
        mock_recovery_key = "TEST-MOCK-RECO-VERY"
        self.recovery_window.show_password_reset_dialog(mock_recovery_key)

    def load_empty_vault(self):
        """Load completely empty vault"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("empty")
        self.load_vault_with_mock_data()

    def load_large_vault(self):
        """Load vault with 100+ passwords for performance testing"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("large")
        self.load_vault_with_mock_data()

    def load_small_preset(self):
        """Switch current vault to small preset"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("small")
        self.load_vault_with_mock_data()

    def load_large_preset(self):
        """Switch current vault to large preset"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("large")
        self.load_vault_with_mock_data()

    def load_massive_vault(self):
        """Load vault with 100 folders × 100 entries = 10,000 total entries"""
        from dev_tools.dev_manager import set_current_preset
        set_current_preset("massive")
        print("Loading massive vault - this may take a moment...")
        self.load_vault_with_mock_data()

    # =============================================================================
    # INITIALIZATION METHODS
    # =============================================================================

    def _init_window(self):
        self.set_application_icon()

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

        # Add bug report button
        self.bug_report_btn = QPushButton("🐛 Bug")
        self.bug_report_btn.setFixedHeight(30)
        self.bug_report_btn.setMinimumWidth(30)
        self.bug_report_btn.setObjectName("userProfileBtn")
        self.bug_report_btn.clicked.connect(self.show_bug_report_dialog)

        # Add user profile button
        self.user_profile_btn = QPushButton("👤 User")
        self.user_profile_btn.setFixedHeight(30)
        self.user_profile_btn.setMinimumWidth(30)
        self.user_profile_btn.setObjectName("userProfileBtn")

        user_layout.addWidget(self.bug_report_btn)
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
        try:
            import dev_tools.dev_manager
            if not dev_tools.dev_manager.DEV_MODE_ACTIVE:
                QTimer.singleShot(2000, self._check_for_updates_startup)

                from gui.update_manager import check_post_update_launch
                check_post_update_launch(self)
        except ImportError:
            QTimer.singleShot(2000, self._check_for_updates_startup)
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

    def show_bug_report_dialog(self):
        from gui.widgets.modern_widgets import ModernDialog, ModernButton
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QHBoxLayout

        # Create dialog
        dialog = ModernDialog(self, "Bug Report / Feedback")
        dialog.setFixedSize(450, 320)

        # Main layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_label = QLabel("Bug Report / Feedback")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header_label)

        # Description text
        desc_label = QLabel("Describe the issue or share your feedback:")
        desc_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(desc_label)

        # Text area
        text_area = QTextEdit()
        text_area.setPlaceholderText("What happened? What were you trying to do?")
        text_area.setFixedHeight(150)
        text_area.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
            }
        """)
        layout.addWidget(text_area)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = ModernButton("Cancel", primary=False)
        cancel_btn.clicked.connect(dialog.reject)

        send_btn = ModernButton("Send", primary=True)
        send_btn.clicked.connect(lambda: self.send_bug_report(text_area.toPlainText(), dialog))

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(send_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def send_bug_report(self, message, dialog):
        if not message.strip():
            return

        try:
            from gui.update_manager import get_discord_webhook
            webhook_url = get_discord_webhook()

            if not webhook_url:
                print("Discord webhook not available")
                dialog.accept()
                return

            # Get user info for context
            from gui.analytics_manager import get_or_create_manager
            manager = get_or_create_manager()
            user_id = manager.analytics_data.get("vault_id", "unknown")
            version = get_current_version()
            os_info = manager.analytics_data.get("os", "unknown")

            # Create Discord message
            discord_data = {
                "embeds": [{
                    "title": "🐛 Bug Report / Feedback",
                    "description": message,
                    "color": 15158332,
                    "fields": [
                        {"name": "User ID", "value": user_id, "inline": True},
                        {"name": "Version", "value": version, "inline": True},
                        {"name": "OS", "value": os_info, "inline": True}
                    ],
                    "timestamp": datetime.now().isoformat()
                }]
            }

            import requests
            response = requests.post(webhook_url, json=discord_data)

            if response.status_code == 204:
                print("Bug report sent successfully")
            else:
                print(f"Failed to send bug report: {response.status_code}")

        except Exception as e:
            print(f"Error sending bug report: {e}")

        dialog.accept()

    # =============================================================================
    # VIEW NAVIGATION METHODS
    # =============================================================================

    def _determine_initial_view(self):
        if '--minimized' in sys.argv:
            return

        try:
            import dev_tools.dev_manager
            if dev_tools.dev_manager.DEV_MODE_ACTIVE:
                print("DEBUG: Skipping initial view in dev mode")
                return
        except ImportError:
            pass

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
            self.bug_report_btn.clicked.disconnect()
        except:
            pass
        self.user_profile_btn.clicked.connect(self.vault_window.show_settings_dialog)

        # Load vault data and switch to vault view
        self.vault_window.load_vault_data(vault_data, username, vault_key)
        self.stacked_widget.setCurrentWidget(self.vault_window)

        from gui.analytics_manager import has_been_prompted_for_consent
        if not has_been_prompted_for_consent():
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, self.vault_window.show_analytics_consent_dialog)

    # =============================================================================
    # AUTHENTICATION HANDLERS
    # =============================================================================

    def handle_login(self, username, password):
        self.login_window.clear_error_message()

        if not username or not password:
            self.login_window.set_error_message("Please enter both username and password")
            return

        # CHECK BETA ACCESS FIRST - NEW
        try:
            from beta.beta_validator import BetaKeyValidator
            validator = BetaKeyValidator()
            allowed, beta_error = validator.check_beta_access_on_login(username)
            if not allowed:
                self.login_window.set_error_message(beta_error)
                return
        except:
            # Beta check failed, continue with normal login
            pass

        # Normal login process (unchanged)
        from core.vault_manager import user_verification, load_vault

        vault_key, verified_username = user_verification(username, password)

        if vault_key and verified_username:
            vault_data = load_vault(vault_key)
            self.show_vault(verified_username, vault_data, vault_key)
        else:
            self.login_window.set_error_message("Invalid username or password")

    # Update signup_window.py signal to include beta_key
    class SignupWindow(QWidget):
        signup_requested = pyqtSignal(str, str, str, str, str)  # Added str for beta_key

    def handle_signup(self, username, password, confirm_password, vault_location, beta_key=""):
        # Basic validation checks (unchanged)
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

        # Create new account
        from core.vault_manager import handle_first_setup
        success, message = handle_first_setup(username, password)

        if success:
            # Save beta key to auth file if provided
            if beta_key:
                try:
                    from beta.beta_validator import BetaKeyValidator
                    validator = BetaKeyValidator()
                    from config import get_auth_path
                    validator.save_beta_key_to_auth(get_auth_path(), beta_key)
                except:
                    pass  # Don't fail signup if beta save fails

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

    def _cleanup_session(self):
        if hasattr(self, 'session_start') and self.session_start:
            duration = (time.time() - self.session_start) / 60
            try:
                from gui.analytics_manager import get_or_create_manager, update_metric, send_to_oracle

                manager = get_or_create_manager()
                current_avg = manager.analytics_data["install_metrics"]["avg_session_length_minutes"]
                total_opens = manager.analytics_data["install_metrics"]["total_app_opens"]

                new_avg = (current_avg * (total_opens - 1) + duration) / total_opens
                update_metric("install_metrics.avg_session_length_minutes", new_avg)
                send_to_oracle()
                self.session_start = None

            except Exception as e:
                print(f"Analytics cleanup failed: {e}")

    def closeEvent(self, event):
        """Override close event to stop all monitoring"""
        if (hasattr(self, 'tray_manager') and
                self.tray_manager and
                self.tray_manager.tray_icon.isVisible()):

            self.hide()
            self.tray_manager.show_notification(
                "TheVault",
                "Minimized to tray. Auto-fill still active.",
                duration=2000
            )
            event.ignore()
        else:
            self._cleanup_session()
            if hasattr(self, 'tray_manager') and self.tray_manager:
                self.tray_manager.stop_monitoring()
            if hasattr(self, 'game_bridge'):
                self.game_bridge.stop_monitoring()
            if hasattr(self, 'riot_detector'):
                self.riot_detector.stop_monitoring()
            if hasattr(self, 'epic_detector'):
                self.epic_detector.stop_monitoring()
            event.accept()


# =============================================================================
# APPLICATION STARTUP
# =============================================================================

def main():
    try:
        import tempfile
        import os
        from datetime import datetime

        forced_log = os.path.join(tempfile.gettempdir(), "vault_startup_forced.log")
        with open(forced_log, "a") as f:
            f.write(f"[{datetime.now()}] VAULT STARTUP ATTEMPT\n")
            f.flush()
    except:
        pass
    # Check if running as executable (production)
    if getattr(sys, 'frozen', False):
        start_app()
    else:
        # Running as script - show dev options
        print("Vault DEV")
        print("1. Dev Mode (Mock data, no auth)")
        print("2. Production Mode (Real files/auth)")

        while True:
            try:
                choice = int(input("Enter choice: "))
                if choice in [1, 2]:
                    break
                else:
                    print("Please enter 1 or 2")
            except ValueError:
                print("Enter valid input")

        if choice == 1:
            start_app_with_dev_cli()
        elif choice == 2:
            start_app()


def start_app_with_dev_cli():
    from dev_tools.dev_manager import set_dev_mode
    set_dev_mode(True)
    load_secrets()

    # Initialize analytics
    analytics_manager = AnalyticsManager()
    analytics_manager.load_or_create_data()

    # Increment app opens for this session
    analytics_manager.increment_counter("install_metrics.total_app_opens")

    # Check for unsent data from previous session
    if analytics_manager.analytics_data.get("needs_send", False):
        success = analytics_manager.send_to_oracle()
        if success:
            analytics_manager.mark_as_sent()

    app = QApplication(sys.argv)
    app.setApplicationName("TheVault")
    app.setApplicationVersion(get_current_version())
    app.setOrganizationName("AlexBenkarski")

    window = TheVaultApp()

    # Start CLI thread
    cli_thread = threading.Thread(target=persistent_dev_cli, args=(window,), daemon=True)
    cli_thread.start()

    sys.exit(app.exec())


def start_app():
    import tempfile
    import os
    import atexit

    def is_process_running(pid):
        """Check if a process is running without psutil"""
        try:
            if os.name == 'nt':
                import subprocess
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'],
                                        capture_output=True, text=True)
                return str(pid) in result.stdout
            else:
                os.kill(pid, 0)
                return True
        except (OSError, subprocess.SubprocessError):
            return False

    # Single instance detection using lock file
    lock_file = os.path.join(tempfile.gettempdir(), "thevault.lock")
    pid_file = os.path.join(tempfile.gettempdir(), "thevault.pid")

    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                old_pid = int(f.read().strip())

            if is_process_running(old_pid):
                print("TheVault is already running.")

                try:
                    signal_file = os.path.join(tempfile.gettempdir(), "thevault_show.signal")
                    with open(signal_file, 'w') as f:
                        f.write("show")
                    print("Sent show signal to existing instance.")
                except:
                    pass

                return
            else:
                print("Removing stale lock file...")
                os.remove(lock_file)
                if os.path.exists(pid_file):
                    os.remove(pid_file)

        except (ValueError, FileNotFoundError):
            print("Removing corrupted lock file...")
            try:
                os.remove(lock_file)
                if os.path.exists(pid_file):
                    os.remove(pid_file)
            except:
                pass

    # Create lock file
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))

    # Create PID file for communication
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

    def cleanup_lock():
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
            if os.path.exists(pid_file):
                os.remove(pid_file)
        except:
            pass

    atexit.register(cleanup_lock)

    try:
        load_secrets()

        from gui.analytics_manager import get_or_create_manager, increment_counter

        manager = get_or_create_manager()
        if not manager:
            print("Failed to initialize analytics")

        version = get_current_version()
        print(f"DEBUG: Current version detected as: '{version}'")

        increment_counter("install_metrics.total_app_opens")

        from gui.analytics_manager import update_days_since_install, update_opens_last_7_days
        update_days_since_install()
        update_opens_last_7_days()

        # Check for unsent data
        if manager and manager.analytics_data.get("needs_send", False):
            success = manager.send_to_oracle()
            if success:
                manager.mark_as_sent()

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setApplicationName("TheVault")
        app.setApplicationVersion(get_current_version())
        app.setOrganizationName("AlexBenkarski")

        window = TheVaultApp()

        if '--minimized' not in sys.argv:
            window.show()

        sys.exit(app.exec())

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

        # Clean up lock files on crash
        cleanup_lock()

        raise


if __name__ == "__main__":
    main()