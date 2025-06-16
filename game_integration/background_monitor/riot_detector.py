import time
import threading
import pygetwindow as gw
import pyautogui
from PyQt6.QtCore import QObject, pyqtSignal


class RiotDetector(QObject):
    username_field_detected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.monitor_thread = None
        self.overlay_shown = False
        self.last_trigger_time = 0
        self.riot_was_active = False
        self.overlay_was_closed_in_riot = False

    def start_monitoring(self):
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Started Riot monitoring with single-click detection...")

    def stop_monitoring(self):
        self.monitoring = False

    def reset_overlay_flag(self):
        """Called when overlay is closed"""
        self.overlay_shown = False

        # If user closes overlay while Riot is still active, don't show again until they leave and come back
        if self.is_riot_active():
            self.overlay_was_closed_in_riot = True
            print("Overlay closed while in Riot - won't trigger again until user leaves Riot")
        else:
            self.overlay_was_closed_in_riot = False
            print("Overlay closed - can trigger again")

    def _monitor_loop(self):
        while self.monitoring:
            current_time = time.time()

            riot_currently_active = self.is_riot_active()

            if not riot_currently_active and self.riot_was_active:
                print("User left Riot - resetting autofill availability")
                self.overlay_was_closed_in_riot = False
                self.riot_was_active = False

            # Detect click into Riot username field
            elif riot_currently_active and not self.riot_was_active:
                if (self.is_username_field_click() and
                        not self.overlay_shown and
                        not self.overlay_was_closed_in_riot):

                    print("USERNAME FIELD CLICKED - TRIGGERING OVERLAY!")
                    self.overlay_shown = True
                    self.last_trigger_time = current_time
                    self.username_field_detected.emit()
                else:
                    if self.overlay_was_closed_in_riot:
                        print("Click detected but overlay was already closed in this Riot session")
                    else:
                        print("Click detected but not in username field area")

                self.riot_was_active = True

            time.sleep(0.2)

    def is_username_field_click(self):
        """Check if click is specifically in the username field area"""
        try:
            current_mouse = pyautogui.position()
            if current_mouse is None:
                return False

            windows = gw.getWindowsWithTitle("Riot Client")
            if not windows:
                return False

            riot_window = windows[0]

            # Calculate relative position
            relative_x = (current_mouse.x - riot_window.left) / riot_window.width
            relative_y = (current_mouse.y - riot_window.top) / riot_window.height

            # Username field boundaries
            username_left = 0.035
            username_right = 0.225
            username_top = 0.275
            username_bottom = 0.325

            in_username_field = (
                    username_left <= relative_x <= username_right and
                    username_top <= relative_y <= username_bottom
            )

            print(f"Click at ({relative_x:.1%}, {relative_y:.1%}) - In username field: {in_username_field}")
            return in_username_field

        except Exception as e:
            print(f"Username field check error: {e}")
            return False

    def is_riot_active(self):
        """Check if Riot Client is the active window"""
        try:
            active_window = gw.getActiveWindow()
            return active_window and "Riot Client" in active_window.title
        except:
            return False
