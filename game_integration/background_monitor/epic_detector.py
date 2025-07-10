import time
import threading
import pygetwindow as gw
import pyautogui
from PyQt6.QtCore import QObject, pyqtSignal


class EpicDetector(QObject):
    username_field_detected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.monitor_thread = None
        self.overlay_shown = False
        self.last_trigger_time = 0
        self.epic_was_active = False
        self.overlay_was_closed_in_epic = False

    def start_monitoring(self):
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Started Epic Games monitoring with single-click detection...")

    def stop_monitoring(self):
        self.monitoring = False

    def reset_overlay_flag(self):
        """Called when overlay is closed - DON'T reset until Epic is closed"""
        self.overlay_shown = False

        self.overlay_was_closed_in_epic = True
        print("Epic overlay closed - won't trigger again until Epic launcher is restarted")

    def is_epic_running(self):
        """Check if Epic Games Launcher process is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if 'EpicGamesLauncher' in proc.info['name'] or 'Epic Games Launcher' in proc.info['name']:
                    return True
            return False
        except:
            # Fallback to window detection
            windows = gw.getWindowsWithTitle("Epic Games Launcher")
            return len(windows) > 0

    def _monitor_loop(self):
        while self.monitoring:
            current_time = time.time()

            epic_currently_active = self.is_epic_active()
            epic_is_running = self.is_epic_running()

            # Reset if Epic process is completely closed
            if not epic_is_running and self.overlay_was_closed_in_epic:
                print("Epic Games Launcher closed - resetting autofill availability")
                self.overlay_was_closed_in_epic = False
                self.epic_was_active = False

            if not epic_currently_active and self.epic_was_active:
                self.epic_was_active = False

            elif epic_currently_active and not self.epic_was_active:
                if (self.is_epic_window_click() and
                        not self.overlay_shown and
                        not self.overlay_was_closed_in_epic):

                    # Check Epic window size first
                    if self.is_epic_standard_size():
                        # Epic is already correct size - wait for username field click
                        print("Epic is standard size - waiting for username field click")
                        if self.is_username_field_click_standard():
                            print("EPIC USERNAME FIELD CLICKED - TRIGGERING DIRECT AUTOFILL!")
                            self.overlay_shown = True
                            self.last_trigger_time = current_time
                            # Use a different signal for direct autofill
                            self.username_field_detected.emit()
                    else:
                        # Epic needs resizing - show mode selection popup
                        print("EPIC WINDOW CLICKED - NEEDS RESIZE - SHOWING POPUP!")
                        self.overlay_shown = True
                        self.last_trigger_time = current_time
                        self.username_field_detected.emit()
                else:
                    if self.overlay_was_closed_in_epic:
                        print("Click detected but overlay was disabled until Epic restart")

                self.epic_was_active = True

            time.sleep(0.2)

    def is_username_field_click(self):
        """Check if click is specifically in the Epic Games username field area"""
        try:
            current_mouse = pyautogui.position()
            if current_mouse is None:
                return False

            windows = gw.getWindowsWithTitle("Epic Games Launcher")
            if not windows:
                return False

            epic_window = windows[0]

            # Calculate relative position
            relative_x = (current_mouse.x - epic_window.left) / epic_window.width
            relative_y = (current_mouse.y - epic_window.top) / epic_window.height

            # Epic Games username field boundaries
            username_left = 0.3
            username_right = 0.7
            username_top = 0.4
            username_bottom = 0.5

            in_username_field = (
                    username_left <= relative_x <= username_right and
                    username_top <= relative_y <= username_bottom
            )

            print(f"Epic click at ({relative_x:.1%}, {relative_y:.1%}) - In username field: {in_username_field}")
            return in_username_field

        except Exception as e:
            print(f"Epic username field check error: {e}")
            return False

    def is_epic_window_click(self):
        """Check if click is anywhere in the Epic Games window"""
        try:
            current_mouse = pyautogui.position()
            if current_mouse is None:
                return False

            windows = gw.getWindowsWithTitle("Epic Games Launcher")
            if not windows:
                return False

            epic_window = windows[0]

            # Check if click is within Epic window bounds
            in_epic_window = (
                    epic_window.left <= current_mouse.x <= epic_window.left + epic_window.width and
                    epic_window.top <= current_mouse.y <= epic_window.top + epic_window.height
            )

            print(f"Epic click detected in window: {in_epic_window}")
            return in_epic_window

        except Exception as e:
            print(f"Epic window click check error: {e}")
            return False

    def is_epic_standard_size(self):
        """Check if Epic window is already at standard size (1200x800)"""
        try:
            windows = gw.getWindowsWithTitle("Epic Games Launcher")
            if not windows:
                return False

            epic_window = windows[0]

            # Check if window is at standard size (with some tolerance)
            standard_width = 1200
            standard_height = 800
            tolerance = 10

            width_ok = abs(epic_window.width - standard_width) <= tolerance
            height_ok = abs(epic_window.height - standard_height) <= tolerance

            is_standard = width_ok and height_ok
            print(f"Epic size check: {epic_window.width}x{epic_window.height} - Standard: {is_standard}")

            return is_standard

        except Exception as e:
            print(f"Epic size check error: {e}")
            return False

    def is_username_field_click_standard(self):
        """Check if click is in username field (assumes 1200x800 window)"""
        try:
            current_mouse = pyautogui.position()
            if current_mouse is None:
                return False

            windows = gw.getWindowsWithTitle("Epic Games Launcher")
            if not windows:
                return False

            epic_window = windows[0]

            # Calculate relative position
            relative_x = (current_mouse.x - epic_window.left) / epic_window.width
            relative_y = (current_mouse.y - epic_window.top) / epic_window.height

            # Username field boundaries for 1200x800 window
            username_left = 0.318
            username_right = 0.672
            username_top = 0.710
            username_bottom = 0.761

            in_username_field = (
                    username_left <= relative_x <= username_right and
                    username_top <= relative_y <= username_bottom
            )

            print(f"Epic username click at ({relative_x:.1%}, {relative_y:.1%}) - In field: {in_username_field}")
            return in_username_field

        except Exception as e:
            print(f"Epic username field check error: {e}")
            return False
        """Check if click is anywhere in the Epic Games window"""
        try:
            current_mouse = pyautogui.position()
            if current_mouse is None:
                return False

            windows = gw.getWindowsWithTitle("Epic Games Launcher")
            if not windows:
                return False

            epic_window = windows[0]

            # Check if click is within Epic window bounds
            in_epic_window = (
                    epic_window.left <= current_mouse.x <= epic_window.left + epic_window.width and
                    epic_window.top <= current_mouse.y <= epic_window.top + epic_window.height
            )

            print(f"Epic click detected in window: {in_epic_window}")
            return in_epic_window

        except Exception as e:
            print(f"Epic window click check error: {e}")
            return False

    def reset_overlay_flag_after_resize(self):
        """Reset overlay flag after resize (keep detection active)"""
        self.overlay_shown = False
        print("Epic overlay hidden after resize - detection still active")

    def is_epic_active(self):
        """Check if Epic Games Launcher is the active window"""
        try:
            active_window = gw.getActiveWindow()
            return active_window and "Epic Games Launcher" in active_window.title
        except:
            return False
        """Check if Epic Games Launcher is the active window"""
        try:
            active_window = gw.getActiveWindow()
            return active_window and "Epic Games Launcher" in active_window.title
        except:
            return False