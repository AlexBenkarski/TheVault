import json
import os
import sys

# Config file path - stored in user's AppData directory (Windows standard)
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "AppData", "Local", "TheVault", "config.json")

AUTH_PATH = None
VAULT_PATH = None


def get_asset_path(filename):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "assets", filename)


def save_vault_directory(vault_directory):
    # Ensure config directory exists
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error reading existing config: {e}")
            config = {}

    config['vault_directory'] = vault_directory

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get_vault_directory():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return config.get('vault_directory')
        except Exception as e:
            print(f"Error reading config: {e}")
    return None


def get_current_auth_path():
    vault_dir = get_vault_directory()
    if vault_dir:
        return os.path.join(vault_dir, "auth", "credentials.enc")
    return None


def get_current_vault_path():
    vault_dir = get_vault_directory()
    if vault_dir:
        return os.path.join(vault_dir, "vault.enc")
    return None


def update_config_paths(vault_directory):
    # Save to persistent config file
    if save_vault_directory(vault_directory):
        # Update global variables (for current session)
        initialize_paths()
        return True
    return False


def initialize_paths():
    global AUTH_PATH, VAULT_PATH
    vault_dir = get_vault_directory()
    if vault_dir:
        AUTH_PATH = os.path.join(vault_dir, "auth", "credentials.enc")
        VAULT_PATH = os.path.join(vault_dir, "vault.enc")
    else:
        AUTH_PATH = None
        VAULT_PATH = None


def get_auth_path():
    current_path = get_current_auth_path()
    return current_path if current_path else AUTH_PATH


def get_vault_path():
    current_path = get_current_vault_path()
    return current_path if current_path else VAULT_PATH


initialize_paths()