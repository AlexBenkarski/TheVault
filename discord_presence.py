# discord_presence.py
from pypresence import Presence
import time


class DiscordPresence:
    def __init__(self, client_id="1400362211813232650"):
        self.client_id = client_id
        self.rpc = None
        self.connected = False

    def connect(self):
        """Connect to Discord and set status"""
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()

            # Check if in dev mode
            is_dev_mode = self._check_dev_mode()

            if is_dev_mode:
                details = "Developing Vault"
                state = "Password Manager"
            else:
                details = "Vault"
                state = "Password Manager"

            buttons_data = [
                {"label": "Join Community", "url": "https://discord.gg/qGGAbsjMg9"}
            ]

            self.rpc.update(
                details=details,
                state=state,
                large_image="vault_logo",
                large_text="Vault",
                buttons=buttons_data,
                start=int(time.time())
            )

            print(f"Discord status updated with buttons: {buttons_data}")

            self.connected = True
            print("Discord Rich Presence connected")
            return True
        except Exception as e:
            print(f"Discord connection failed: {e}")
            return False

    def _check_dev_mode(self):
        """Check if app is running in dev mode"""
        try:
            # Check the dev manager flag
            import dev_tools.dev_manager
            if dev_tools.dev_manager.DEV_MODE_ACTIVE:
                return True

            # Also check if running as script (not exe)
            import sys
            if not getattr(sys, 'frozen', False):
                return True

            return False
        except ImportError:
            # Check if running as script
            import sys
            return not getattr(sys, 'frozen', False)

    def disconnect(self):
        """Clean disconnect"""
        if self.rpc and self.connected:
            try:
                self.rpc.close()
                self.connected = False
            except:
                pass