import sys
import os


class StartupManager:
    """Manages Windows startup integration"""

    def __init__(self, app_name="TheVault"):
        self.app_name = app_name
        self.registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def _get_executable_path(self):
        """Get the path to the current executable"""
        if getattr(sys, 'frozen', False):
            path = sys.executable
            print(f"DEBUG: Using executable path: {path}")
            return path
        else:
            script_path = os.path.abspath(sys.argv[0])
            if script_path.endswith('.py'):
                path = f'"{sys.executable}" "{script_path}"'
                print(f"DEBUG: Using script path: {path}")
                return path
            return script_path

    def enable_startup(self):
        """Enable startup using Windows shortcut"""
        try:
            print("DEBUG: Starting enable_startup...")

            startup_folder = os.path.join(os.environ['APPDATA'],
                                          'Microsoft', 'Windows', 'Start Menu',
                                          'Programs', 'Startup')

            os.makedirs(startup_folder, exist_ok=True)

            # Get executable path
            exe_path = self._get_executable_path()
            if not exe_path:
                return False

            # Create shortcut file (.lnk)
            shortcut_path = os.path.join(startup_folder, f"{self.app_name}.lnk")

            import pythoncom
            from win32com.client import Dispatch

            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)

            if getattr(sys, 'frozen', False):
                # Compiled executable
                shortcut.Targetpath = exe_path
                shortcut.Arguments = "--minimized"
            else:
                # Dev mode
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{os.path.abspath(sys.argv[0])}" --minimized'

            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.Description = "TheVault Password Manager"
            shortcut.save()

            print(f"DEBUG: Created shortcut at: {shortcut_path}")
            return True

        except Exception as e:
            print(f"Failed to create shortcut: {e}")
            return self._create_batch_file()

    def is_startup_enabled(self):
        """Check if startup is enabled by looking for shortcut"""
        try:
            startup_folder = os.path.join(os.environ['APPDATA'],
                                          'Microsoft', 'Windows', 'Start Menu',
                                          'Programs', 'Startup')

            # Check for shortcut
            shortcut_path = os.path.join(startup_folder, f"{self.app_name}.lnk")
            if os.path.exists(shortcut_path):
                return True

            batch_path = os.path.join(startup_folder, f"{self.app_name}.bat")
            return os.path.exists(batch_path)

        except Exception as e:
            print(f"DEBUG: Startup check failed: {e}")
            return False

    def disable_startup(self):
        """Disable startup by removing shortcut and batch file"""
        try:
            startup_folder = os.path.join(os.environ['APPDATA'],
                                          'Microsoft', 'Windows', 'Start Menu',
                                          'Programs', 'Startup')

            # Remove shortcut
            shortcut_path = os.path.join(startup_folder, f"{self.app_name}.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)

            # Remove batch file
            batch_path = os.path.join(startup_folder, f"{self.app_name}.bat")
            if os.path.exists(batch_path):
                os.remove(batch_path)

            return True

        except Exception as e:
            print(f"Failed to disable startup: {e}")
            return False

    def get_startup_command(self):
        """Get the current startup command if enabled"""
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path) as key:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                return value
        except:
            return None