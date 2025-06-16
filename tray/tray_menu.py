from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction


class TrayMenuBuilder:
    def __init__(self, parent, tray_manager):
        self.parent = parent
        self.tray_manager = tray_manager

    def create_menu(self):
        """Create the tray menu"""
        menu = QMenu()

        # Show Vault
        show_action = QAction("🏠 Show Vault", self.parent)
        show_action.triggered.connect(self.tray_manager.show_main_window)
        menu.addAction(show_action)

        # Lock Vault (if user is logged in)
        lock_action = QAction("🔒 Lock Vault", self.parent)
        lock_action.triggered.connect(self._lock_vault)
        menu.addAction(lock_action)

        menu.addSeparator()

        # Exit
        exit_action = QAction("❌ Exit", self.parent)
        exit_action.triggered.connect(self.tray_manager.exit_application)
        menu.addAction(exit_action)

        return menu

    def _lock_vault(self):
        """Lock the vault and return to login screen"""
        # Show main window first
        self.tray_manager.show_main_window()

        if hasattr(self.tray_manager.main_window, 'show_login'):
            self.tray_manager.main_window.show_login()

        self.tray_manager.show_notification(
            "Vault Locked",
            "Please log in to access your vault",
            duration=2000
        )