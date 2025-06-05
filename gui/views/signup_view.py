import os
import tkinter as tk
from tkinter import filedialog
from dearpygui import dearpygui as dpg
from core.vault_manager import is_password_strong
from gui.views import login_view
from gui.helpers.view_manager import set_view


def get_default_vault_path():
    from config import is_dev_environment

    if is_dev_environment():
        # DEV: Use project dev folder

        current_file = os.path.abspath(__file__)
        views_dir = os.path.dirname(current_file)
        gui_dir = os.path.dirname(views_dir)
        project_root = os.path.dirname(gui_dir)

        dev_vault_dir = os.path.join(project_root, "dev_vault_data")
        if not os.path.exists(dev_vault_dir):
            os.makedirs(dev_vault_dir, exist_ok=True)
        return dev_vault_dir
    else:
        # PRODUCTION: OneDrive logic
        user_home = os.path.expanduser("~")
        default_path = os.path.join(user_home, "OneDrive", "TheVault")
        return default_path


def browse_for_directory():
    root = tk.Tk()
    root.withdraw()

    # Get current directory or default
    current_path = dpg.get_value("storage_path_display")
    if not current_path:
        current_path = get_default_vault_path()

    # Open directory selection dialog
    selected_directory = filedialog.askdirectory(
        title="Select Directory for Vault Storage",
        initialdir=os.path.dirname(current_path)
    )

    root.destroy()

    if selected_directory:
        # Create TheVault subdirectory
        vault_directory = os.path.join(selected_directory, "TheVault")
        dpg.set_value("storage_path_display", vault_directory)
        dpg.set_value("selected_vault_directory", vault_directory)


def show_signup_view():
    print("*** show_signup_view() called ***")
    print(f"input_username exists before login_view: {dpg.does_item_exist('input_username')}")
    # Set default storage path
    default_path = get_default_vault_path()

    with dpg.child_window(parent="MainWindow", tag="SignupWindow", border=False):
        dpg.add_spacer(height=5)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=420)
            dpg.add_image("logo_texture", width=300, height=300)


        with dpg.group(horizontal=True):
            dpg.add_spacer(width=540)
            dpg.add_text("Sign Up", color=(255, 255, 255))

        dpg.add_spacer(height=5)


        with dpg.group(horizontal=True):
            dpg.add_spacer(width=580)
            dpg.add_text("", tag="status_text")


        with dpg.group(horizontal=True):
            dpg.add_spacer(width=455)
            dpg.add_input_text(hint="Username", label="", width=250, tag="input_username")

        dpg.add_spacer(height=5)


        with dpg.group(horizontal=True):
            dpg.add_spacer(width=455)
            dpg.add_input_text(
                hint="Password",
                label="",
                width=250,
                password=True,
                tag="input_password",
                callback=validate_password_strength_signup
            )

        dpg.add_spacer(height=5)

        # Password requirements positioned next to password field
        with dpg.child_window(width=250, height=128, pos=[735, 373], no_scrollbar=True, border=False):
            dpg.add_text("Password Requirements:", color=(200, 200, 200))
            dpg.add_text("At least 8 characters", tag="signup_req_length", color=(150, 150, 150))
            dpg.add_text("One uppercase letter", tag="signup_req_upper", color=(150, 150, 150))
            dpg.add_text("One symbol", tag="signup_req_symbol", color=(150, 150, 150))
            dpg.add_text("Passwords must match", tag="signup_req_match", color=(150, 150, 150))

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=455)
            dpg.add_input_text(hint="Confirm Password", label="", width=250, password=True,
                               tag="input_confirm_password", callback=validate_password_match_signup)

        dpg.add_spacer(height=5)


        with dpg.group(horizontal=True):
            dpg.add_spacer(width=455)
            dpg.add_text("Storage Location:")

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=455)
            dpg.add_input_text(
                default_value=default_path,
                width=250,
                readonly=True,
                tag="storage_path_display"
            )
            dpg.add_button(label="Browse...", callback=browse_for_directory)


        dpg.add_input_text(default_value=default_path, show=False, tag="selected_vault_directory")

        dpg.add_spacer(height=5)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=455)
            dpg.add_button(
                label="Create Account",
                callback=lambda: try_account_creation()
            )

        dpg.add_spacer(height=5)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=450, tag="error_spacer")


def validate_password_strength_signup():
    password = dpg.get_value("input_password")

    # Length check
    if len(password) >= 8:
        dpg.configure_item("signup_req_length", color=(100, 255, 100))
    else:
        dpg.configure_item("signup_req_length", color=(150, 150, 150))

    # Uppercase check
    if any(c.isupper() for c in password):
        dpg.configure_item("signup_req_upper", color=(100, 255, 100))
    else:
        dpg.configure_item("signup_req_upper", color=(150, 150, 150))

    # Symbol check
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in symbols for c in password):
        dpg.configure_item("signup_req_symbol", color=(100, 255, 100))
    else:
        dpg.configure_item("signup_req_symbol", color=(150, 150, 150))

    # Also check password match when password changes
    validate_password_match_signup()


def validate_password_match_signup():
    password = dpg.get_value("input_password")
    confirm = dpg.get_value("input_confirm_password")

    if confirm and password == confirm:
        dpg.configure_item("signup_req_match", color=(100, 255, 100))
    elif confirm:
        dpg.configure_item("signup_req_match", color=(255, 100, 100))
    else:
        dpg.configure_item("signup_req_match", color=(150, 150, 150))


def show_recovery_popup(recovery_key):
    with dpg.window(label="IMPORTANT: Save Your Recovery Key", modal=True,
                    tag="signup_recovery_popup", width=500, height=350, pos=[250, 200]):
        dpg.add_text("Account created successfully!", color=(100, 255, 100))
        dpg.add_spacer(height=15)

        dpg.add_text("Your recovery key is:", color=(255, 255, 100))
        dpg.add_spacer(height=10)

        # Display the recovery key as masked by default
        dpg.add_input_text(default_value="****-****-****-****", readonly=True, width=350,
                           tag="signup_display_recovery_key")

        dpg.add_spacer(height=10)

        # Show and Copy buttons side by side
        with dpg.group(horizontal=True):
            dpg.add_button(label="Show Key", callback=lambda: toggle_signup_key_visibility(recovery_key), width=100)
            dpg.add_spacer(width=20)
            dpg.add_button(label="Copy to Clipboard",
                           callback=lambda: dpg.set_clipboard_text(recovery_key), width=150)

        dpg.add_spacer(height=15)

        dpg.add_text("WARNING: Save this recovery key now!", color=(255, 100, 100))
        dpg.add_text("You will not be able to see it again.")
        dpg.add_text("Store it in a safe place separate from your vault.")
        dpg.add_text("You can use this key to recover your account if you")
        dpg.add_text("forget your password.")

        dpg.add_spacer(height=20)

        dpg.add_button(label="I Have Saved My Recovery Key",
                       callback=signup_recovery_complete, width=300)


def signup_recovery_complete():
    dpg.delete_item("signup_recovery_popup")
    set_view(login_view.show_login_view)


def toggle_signup_key_visibility(recovery_key):
    current_value = dpg.get_value("signup_display_recovery_key")
    if current_value == "****-****-****-****":
        # Show the actual key
        dpg.set_value("signup_display_recovery_key", recovery_key)
        dpg.configure_item("signup_display_recovery_key", readonly=False)
        dpg.configure_item("signup_display_recovery_key", readonly=True)  # Keep readonly
    else:
        # Hide the key
        dpg.set_value("signup_display_recovery_key", "****-****-****-****")


def go_to_login():
    dpg.delete_item("RecoveryPopup")
    set_view(login_view.show_login_view)


def center_error_text(message):
    if dpg.does_item_exist("error_text_group"):
        dpg.delete_item("error_text_group")

    if message:
        text_width = len(message) * 8
        center_x = 580
        text_x = max(0, center_x - text_width // 2)

        with dpg.group(horizontal=True, parent="SignupWindow", before="error_spacer", tag="error_text_group"):
            dpg.add_spacer(width=text_x)
            dpg.add_text(message, tag="error_text", color=(255, 0, 0))


def try_account_creation():
    input_username = dpg.get_value("input_username")
    input_password = dpg.get_value("input_password")
    input_confirm_password = dpg.get_value("input_confirm_password")
    selected_directory = dpg.get_value("selected_vault_directory")

    # Check for empty fields
    if not input_username or not input_password or not input_confirm_password:
        center_error_text("All fields are required.")
        return

    # Check if passwords match
    if input_password != input_confirm_password:
        center_error_text("Passwords do not match.")
        return

    # Check password strength
    if not is_password_strong(input_password):
        center_error_text("Password does not meet requirements.")
        return

    # Validate storage directory selection
    if not selected_directory:
        center_error_text("Please select a storage location.")
        return

    try:
        # Create the directory if it doesn't exist
        os.makedirs(selected_directory, exist_ok=True)

        # Update config paths
        from config import update_config_paths
        if not update_config_paths(selected_directory):
            center_error_text("Failed to update configuration.")
            return

        # Create the account using the standard function
        from core.vault_manager import handle_first_setup
        result = handle_first_setup(input_username, input_password)

        if result and result[0]:
            _, recovery_key = result
            show_recovery_popup(recovery_key)
        else:
            error_message = result[1] if result and len(result) > 1 else "Account creation failed."
            center_error_text(error_message)

    except Exception as e:
        center_error_text(f"Error during setup: {str(e)}")
        return