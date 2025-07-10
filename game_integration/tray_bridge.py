from PyQt6.QtCore import QObject, pyqtSignal


class GameIntegrationBridge(QObject):
    overlay_shown = pyqtSignal(str)  # game_name
    overlay_closed = pyqtSignal(str)  # game_name
    autofill_success = pyqtSignal(str, str)  # game_name, account_name
    autofill_error = pyqtSignal(str, str)  # game_name, error_message

    def __init__(self):
        super().__init__()

        self.riot_detector = None
        self.overlay_manager = None

        # Track monitoring state
        self.is_monitoring = False

    def set_riot_detector(self, riot_detector):
        self.riot_detector = riot_detector

        if hasattr(riot_detector, 'username_field_detected'):
            riot_detector.username_field_detected.connect(self._on_riot_field_detected)
            print("Bridge: Connected to RiotDetector signals")

    def set_overlay_manager(self, overlay_manager):
        self.overlay_manager = overlay_manager
        print("Bridge: Connected to OverlayManager")

    def start_monitoring(self):
        """Start all game monitoring systems"""
        self.is_monitoring = True

        if self.riot_detector and hasattr(self.riot_detector, 'start_monitoring'):
            self.riot_detector.start_monitoring()
            print("Bridge: Started Riot monitoring")

        # Add Epic monitoring
        if self.epic_detector and hasattr(self.epic_detector, 'start_monitoring'):
            self.epic_detector.start_monitoring()
            print("Bridge: Started Epic monitoring")

    def stop_monitoring(self):
        """Stop all game monitoring systems"""
        self.is_monitoring = False

        if self.riot_detector and hasattr(self.riot_detector, 'stop_monitoring'):
            self.riot_detector.stop_monitoring()
            print("Bridge: Stopped Riot monitoring")

        # Add Epic monitoring
        if self.epic_detector and hasattr(self.epic_detector, 'stop_monitoring'):
            self.epic_detector.stop_monitoring()
            print("Bridge: Stopped Epic monitoring")

    def get_monitoring_status(self):
        """Get overall monitoring status"""
        statuses = []

        if self.is_riot_monitoring_active():
            statuses.append("Riot active")

        if self.is_epic_monitoring_active():
            statuses.append("Epic active")

        if statuses:
            return "; ".join(statuses)
        elif self.is_monitoring:
            return "Game integration ready"
        else:
            return "Game integration stopped"


    def stop_monitoring(self):
        """Stop all game monitoring systems"""
        self.is_monitoring = False

        if self.riot_detector and hasattr(self.riot_detector, 'stop_monitoring'):
            self.riot_detector.stop_monitoring()
            print("Bridge: Stopped Riot monitoring")


    def is_riot_monitoring_active(self):
        """Check if Riot monitoring is active"""
        if self.riot_detector and hasattr(self.riot_detector, 'monitoring'):
            return self.riot_detector.monitoring
        return False

    def get_monitoring_status(self):
        """Get overall monitoring status"""
        statuses = []

        if self.is_riot_monitoring_active():
            statuses.append("Riot active")

        if statuses:
            return "; ".join(statuses)
        elif self.is_monitoring:
            return "Game integration ready"
        else:
            return "Game integration stopped"

    def _on_riot_field_detected(self):
        print("Bridge: Riot username field detected by existing detector")


    def notify_overlay_shown(self, game_name="Riot Client"):
        print(f"Bridge: Overlay shown for {game_name}")
        self.overlay_shown.emit(game_name)

    def notify_overlay_closed(self, game_name="Riot Client"):
        print(f"Bridge: Overlay closed for {game_name}")
        self.overlay_closed.emit(game_name)

    def notify_autofill_success(self, account_name="", game_name="Riot Client"):
        print(f"Bridge: Autofill success - {account_name} in {game_name}")
        self.autofill_success.emit(game_name, account_name)

    def notify_autofill_error(self, error_message="", game_name="Riot Client"):
        print(f"Bridge: Autofill error in {game_name}: {error_message}")
        self.autofill_error.emit(game_name, error_message)

    def initialize_with_existing_systems(self, riot_detector=None, overlay_manager=None):
        """Helper method to set both systems at once"""
        if riot_detector:
            self.set_riot_detector(riot_detector)
        if overlay_manager:
            self.set_overlay_manager(overlay_manager)
        print("Bridge: Initialized with existing game systems")

    def set_epic_detector(self, epic_detector):
        self.epic_detector = epic_detector

        if hasattr(epic_detector, 'username_field_detected'):
            epic_detector.username_field_detected.connect(self._on_epic_field_detected)
            print("Bridge: Connected to EpicDetector signals")

    def _on_epic_field_detected(self):
        print("Bridge: Epic username field detected by existing detector")

    def is_epic_monitoring_active(self):
        """Check if Epic monitoring is active"""
        if self.epic_detector and hasattr(self.epic_detector, 'monitoring'):
            return self.epic_detector.monitoring
        return False