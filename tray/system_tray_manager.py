import os
from PyQt6.QtWidgets import QSystemTrayIcon, QApplication
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon

from .background_monitor import TrayBackgroundMonitor
from .startup_manager import StartupManager
from .tray_menu import TrayMenuBuilder
from .tray_notifications import TrayNotificationManager
from config import get_asset_path


class SystemTrayManager:
    def __init__(self, main_window, game_integration_manager=None):
        self.main_window = main_window
        self.game_integration_manager = game_integration_manager
        self.settings = QSettings("TheVault", "TraySettings")

        # Core components
        self.tray_icon = QSystemTrayIcon()
        self.startup_manager = StartupManager()
        self.monitor = TrayBackgroundMonitor(game_integration_manager)

        # UI components
        self.menu_builder = TrayMenuBuilder(main_window, self)
        self.notifications = TrayNotificationManager(self.tray_icon)

        # Setup
        self._setup_tray_icon()
        self._setup_monitoring()
        self._connect_signals()
        self._connect_existing_game_systems()

    def _setup_tray_icon(self):
        """Setup the system tray icon"""
        icon_path = get_asset_path("logo.png")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            icon = self.main_window.style().standardIcon(
                self.main_window.style().StandardPixmap.SP_ComputerIcon
            )

        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("TheVault")

        # Set context menu
        menu = self.menu_builder.create_menu()
        self.tray_icon.setContextMenu(menu)

    def _setup_monitoring(self):
        """Setup tray monitoring (not game detection)"""
        monitoring_enabled = self.settings.value("tray_monitoring_enabled", True, type=bool)
        self.monitor.enable_monitoring(monitoring_enabled)

    def _connect_signals(self):
        """Connect tray-specific signals"""
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.messageClicked.connect(self._on_message_clicked)


    def _connect_existing_game_systems(self):
        """Connect to your existing game integration systems"""
        if not self.game_integration_manager:
            return

        try:
            if hasattr(self.game_integration_manager, 'overlay_manager'):
                overlay_manager = self.game_integration_manager.overlay_manager
                if hasattr(overlay_manager, 'overlay_shown'):
                    overlay_manager.overlay_shown.connect(self._on_overlay_shown)
                if hasattr(overlay_manager, 'overlay_closed'):
                    overlay_manager.overlay_closed.connect(self._on_overlay_closed)
                if hasattr(overlay_manager, 'autofill_success'):
                    overlay_manager.autofill_success.connect(self._on_autofill_success)

        except Exception as e:
            print(f"Warning: Could not connect to game systems: {e}")

    def show(self):
        """Show the tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()
            return True
        return False

    def hide(self):
        """Hide the tray icon"""
        self.tray_icon.hide()

    def start_monitoring(self):
        """Start tray monitoring (not game detection)"""
        if not self.monitor.isRunning():
            self.monitor.start()

    def stop_monitoring(self):
        """Stop tray monitoring"""
        if self.monitor.isRunning():
            self.monitor.stop()

    def set_game_integration_manager(self, manager):
        """Set reference to game integration manager after initialization"""
        self.game_integration_manager = manager
        self.monitor.set_game_integration_manager(manager)
        self._connect_existing_game_systems()

    # Event handlers for tray
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.show_quick_search()

    def _on_message_clicked(self):
        """Handle notification click"""
        self.show_main_window()



    def _on_overlay_closed(self, game_name=""):
        """Handle when overlay is closed"""
        pass


    def show_main_window(self):
        """Show and raise the main window"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

        if self.main_window.isMinimized():
            self.main_window.showNormal()

    def show_quick_search(self):
        """Show quick search dialog"""
        # Future implementation
        self.notifications.show_notification(
            "Quick Search",
            "Quick search feature coming soon!",
            duration=2000
        )

    def show_password_generator(self):
        """Show password generator dialog"""
        # Future implementation
        self.notifications.show_notification(
            "Password Generator",
            "Password generator coming soon!",
            duration=2000
        )

    def show_notification_settings(self):
        """Show notification settings dialog"""
        self.show_main_window()

    def show_settings(self):
        """Show main settings dialog"""
        self.show_main_window()
        if hasattr(self.main_window, 'vault_window') and hasattr(self.main_window.vault_window, 'show_settings_dialog'):
            self.main_window.vault_window.show_settings_dialog()

    def show_about(self):
        """Show about dialog"""
        self.show_main_window()

    def toggle_monitoring(self, enabled):
        """Toggle tray monitoring"""
        self.monitor.enable_monitoring(enabled)
        self.settings.setValue("tray_monitoring_enabled", enabled)

        # Update menu
        self.menu_builder.update_monitoring_status(enabled)

    def toggle_game_integration(self, enabled):
        """Toggle game integration systems"""
        if not self.game_integration_manager:
            self.notifications.show_error(
                "Game Integration Error",
                "Game integration manager not available"
            )
            return

        try:
            if enabled:
                if hasattr(self.game_integration_manager, 'start_monitoring'):
                    self.game_integration_manager.start_monitoring()
                elif hasattr(self.game_integration_manager, 'riot_detector'):
                    self.game_integration_manager.riot_detector.start_monitoring()
            else:
                if hasattr(self.game_integration_manager, 'stop_monitoring'):
                    self.game_integration_manager.stop_monitoring()
                elif hasattr(self.game_integration_manager, 'riot_detector'):
                    self.game_integration_manager.riot_detector.stop_monitoring()

        except Exception as e:
            self.notifications.show_error(
                "Game Integration Error",
                f"Failed to toggle game integration: {str(e)}"
            )

    def toggle_startup(self, enabled):
        """Toggle startup with Windows"""
        if enabled:
            success = self.startup_manager.enable_startup()
        else:
            success = self.startup_manager.disable_startup()

        if success:
            self.menu_builder.update_startup_status(enabled)
        else:
            # Revert menu state on failure
            self.menu_builder.update_startup_status(not enabled)
            self.notifications.show_error(
                "Startup Error",
                "Failed to change startup settings. Try running as administrator."
            )

    def exit_application(self):
        """Clean exit of the application"""
        # Stop tray monitoring
        self.stop_monitoring()

        # Stop game integration if available
        if self.game_integration_manager:
            try:
                if hasattr(self.game_integration_manager, 'stop_monitoring'):
                    self.game_integration_manager.stop_monitoring()
                elif hasattr(self.game_integration_manager, 'riot_detector'):
                    self.game_integration_manager.riot_detector.stop_monitoring()
            except Exception as e:
                print(f"Warning: Error stopping game integration: {e}")

        self.hide()
        QApplication.quit()

    # Utility methods
    def show_notification(self, title, message, notification_type=None, duration=3000):
        """Public method to show notifications"""
        if notification_type is None:
            from .tray_notifications import NotificationType
            notification_type = NotificationType.INFO

        self.notifications.show_notification(title, message, notification_type, duration)

    def is_monitoring_enabled(self):
        """Check if tray monitoring is enabled"""
        return self.monitor.monitoring_enabled

    def is_startup_enabled(self):
        """Check if startup is enabled"""
        return self.startup_manager.is_startup_enabled()