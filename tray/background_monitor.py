from PyQt6.QtCore import QThread, pyqtSignal


class TrayBackgroundMonitor(QThread):
    monitoring_status_changed = pyqtSignal(str)
    game_integration_status = pyqtSignal(str, bool)  # game_name, is_active

    def __init__(self, game_integration_manager=None):
        super().__init__()
        self.running = False
        self.monitoring_enabled = True
        self.game_integration_manager = game_integration_manager

    def run(self):
        """monitoring loop"""
        self.running = True
        self.monitoring_status_changed.emit("Tray monitoring active")

        while self.running and self.monitoring_enabled:
            try:
                self._check_integration_status()

                self.msleep(5000)

            except Exception as e:
                self.monitoring_status_changed.emit(f"Tray monitor error: {str(e)}")
                self.msleep(10000)

    def _check_integration_status(self):
        """Check status of existing game integration systems"""
        if not self.game_integration_manager:
            return

        try:
            status_messages = []

            if hasattr(self.game_integration_manager, 'riot_detector'):
                if self.game_integration_manager.riot_detector.monitoring:
                    status_messages.append("Riot monitoring active")
                    self.game_integration_status.emit("Riot Client", True)
                else:
                    self.game_integration_status.emit("Riot Client", False)

            if status_messages:
                self.monitoring_status_changed.emit("; ".join(status_messages))
            else:
                self.monitoring_status_changed.emit("Game integration available")

        except Exception as e:
            self.monitoring_status_changed.emit(f"Integration check failed: {str(e)}")

    def stop(self):
        """Stop monitoring thread"""
        self.running = False
        self.wait(3000)

    def enable_monitoring(self, enabled):
        """Enable/disable monitoring without stopping thread"""
        self.monitoring_enabled = enabled
        status = "enabled" if enabled else "disabled"
        self.monitoring_status_changed.emit(f"Tray monitoring {status}")

    def set_game_integration_manager(self, manager):
        """Set reference to game integration manager"""
        self.game_integration_manager = manager