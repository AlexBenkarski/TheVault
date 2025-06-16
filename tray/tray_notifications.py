from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtCore import QSettings, QTimer
from enum import Enum


class NotificationType(Enum):
    """Types of notifications"""
    INFO = QSystemTrayIcon.MessageIcon.Information
    WARNING = QSystemTrayIcon.MessageIcon.Warning
    CRITICAL = QSystemTrayIcon.MessageIcon.Critical
    SUCCESS = QSystemTrayIcon.MessageIcon.Information


class TrayNotificationManager:
    """Manages system tray notifications with user preferences"""

    def __init__(self, tray_icon):
        self.tray_icon = tray_icon
        self.settings = QSettings("TheVault", "NotificationSettings")

        # Notification queuing
        self.notification_queue = []
        self.is_showing = False

        # Rate limiting
        self.last_notification_time = {}
        self.rate_limit_seconds = 5

    def show_notification(self, title, message, notification_type=NotificationType.INFO, duration=3000):
        """Show a system tray notification"""
        if not self._should_show_notification(notification_type):
            return

        if not self.tray_icon.isVisible():
            return

        # Rate limiting
        if self._is_rate_limited(title):
            return

        # Queue notification if one is already showing
        if self.is_showing:
            self.notification_queue.append((title, message, notification_type, duration))
            return

        self._display_notification(title, message, notification_type, duration)

    def _display_notification(self, title, message, notification_type, duration):
        """Actually display the notification"""
        self.is_showing = True
        self.last_notification_time[title] = QTimer()

        # Show the notification
        self.tray_icon.showMessage(
            title,
            message,
            notification_type.value,
            duration
        )

        QTimer.singleShot(duration + 500, self._on_notification_finished)

    def _on_notification_finished(self):
        """Handle notification finish"""
        self.is_showing = False

        # Show next queued notification
        if self.notification_queue:
            next_notification = self.notification_queue.pop(0)
            self._display_notification(*next_notification)

    def _should_show_notification(self, notification_type):
        """Check if this type of notification should be shown"""
        type_name = notification_type.name.lower()
        setting_key = f"show_{type_name}_notifications"
        return self.settings.value(setting_key, True, type=bool)

    def _is_rate_limited(self, title):
        """Check if this notification is rate limited"""
        if title in self.last_notification_time:
            last_timer = self.last_notification_time[title]
            if hasattr(last_timer, 'isActive') and last_timer.isActive():
                return True

        timer = QTimer()
        timer.setSingleShot(True)
        timer.start(self.rate_limit_seconds * 1000)
        self.last_notification_time[title] = timer

        return False

    def show_game_detected(self, game_name):
        """Show game detection notification"""
        self.show_notification(
            f"{game_name} Detected",
            f"Auto-fill is ready for {game_name}",
            NotificationType.SUCCESS,
            duration=4000
        )

    def show_autofill_success(self, game_name, entry_name):
        """Show successful auto-fill notification"""
        self.show_notification(
            "Auto-fill Complete",
            f"Filled credentials for {entry_name} in {game_name}",
            NotificationType.SUCCESS,
            duration=3000
        )

    def show_vault_locked(self):
        """Show vault locked notification"""
        self.show_notification(
            "Vault Locked",
            "Your vault has been locked for security",
            NotificationType.INFO,
            duration=3000
        )

    def show_monitoring_status(self, enabled):
        """Show monitoring status change"""
        status = "enabled" if enabled else "disabled"
        self.show_notification(
            "Monitoring Status",
            f"Background monitoring {status}",
            NotificationType.INFO,
            duration=2000
        )

    def show_update_available(self, version):
        """Show update available notification"""
        self.show_notification(
            "Update Available",
            f"TheVault {version} is available for download",
            NotificationType.INFO,
            duration=5000
        )

    def show_startup_changed(self, enabled):
        """Show startup setting change"""
        status = "enabled" if enabled else "disabled"
        self.show_notification(
            "Startup Setting",
            f"Start with Windows {status}",
            NotificationType.INFO,
            duration=2000
        )

    def show_error(self, title, message):
        """Show error notification"""
        self.show_notification(
            title,
            message,
            NotificationType.CRITICAL,
            duration=5000
        )

    def show_warning(self, title, message):
        """Show warning notification"""
        self.show_notification(
            title,
            message,
            NotificationType.WARNING,
            duration=4000
        )

    # Settings management
    def get_notification_settings(self):
        """Get current notification settings"""
        return {
            'show_info_notifications': self.settings.value("show_info_notifications", True, type=bool),
            'show_warning_notifications': self.settings.value("show_warning_notifications", True, type=bool),
            'show_critical_notifications': self.settings.value("show_critical_notifications", True, type=bool),
            'show_success_notifications': self.settings.value("show_success_notifications", True, type=bool),
            'show_game_notifications': self.settings.value("show_game_notifications", True, type=bool),
        }

    def update_notification_settings(self, settings_dict):
        """Update notification settings"""
        for key, value in settings_dict.items():
            self.settings.setValue(key, value)

    def reset_notification_settings(self):
        """Reset all notification settings to defaults"""
        default_settings = {
            'show_info_notifications': True,
            'show_warning_notifications': True,
            'show_critical_notifications': True,
            'show_success_notifications': True,
            'show_game_notifications': True,
        }
        self.update_notification_settings(default_settings)