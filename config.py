import json
import os
import sys


def is_dev_environment():
    return not hasattr(sys, '_MEIPASS')


def get_config_file_path():
    if is_dev_environment():
        # DEV: Store config in project directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(project_root, "dev_config.json")
    else:
        # PRODUCTION: Use existing AppData location
        return os.path.join(os.path.expanduser("~"), "AppData", "Local", "TheVault", "config.json")


def get_default_vault_directory():
    if is_dev_environment():
        # DEV: Use project subdirectory
        project_root = os.path.dirname(os.path.abspath(__file__))
        dev_vault_dir = os.path.join(project_root, "dev_vault_data")
        # Ensure dev directory exists
        if not os.path.exists(dev_vault_dir):
            os.makedirs(dev_vault_dir, exist_ok=True)
        return dev_vault_dir
    else:
        # PRODUCTION: Return None to let user choose (existing behavior)
        return None


def get_window_title():
    if is_dev_environment():
        return "TheVault (Development)"
    else:
        return "TheVault"


# Dynamic config file path based on environment
CONFIG_FILE = get_config_file_path()

AUTH_PATH = None
VAULT_PATH = None


def get_asset_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, 'assets', filename)


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
    # Store environment info for debugging
    config['is_dev_environment'] = is_dev_environment()

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

    # If no config exists, return default for dev environment
    return get_default_vault_directory()


def get_current_auth_path():
    vault_dir = get_vault_directory()
    if vault_dir:
        auth_dir = os.path.join(vault_dir, "auth")
        # Ensure auth directory exists
        if not os.path.exists(auth_dir):
            os.makedirs(auth_dir, exist_ok=True)
        return os.path.join(auth_dir, "credentials.enc")
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


def print_environment_info():
    print(f"Development Environment: {is_dev_environment()}")
    print(f"Config File: {CONFIG_FILE}")
    print(f"Vault Directory: {get_vault_directory()}")
    print(f"Window Title: {get_window_title()}")


# Initialize paths on import
initialize_paths()

# Auto-create dev environment on first run
if is_dev_environment():
    vault_dir = get_vault_directory()
    if vault_dir and not os.path.exists(CONFIG_FILE):
        # First time dev setup - save the default dev directory
        save_vault_directory(vault_dir)