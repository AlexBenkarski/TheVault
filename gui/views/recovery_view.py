import dearpygui.dearpygui as dpg
from core.vault_manager import recover_password
from gui.helpers.view_manager import set_view


def show_recovery_view():
    # Create a new recovery screen inside MainWindow
    with dpg.child_window(parent="MainWindow", tag="RecoveryView", border=False):
        dpg.add_spacer(height=5)


        with dpg.group(horizontal=True):
            dpg.add_spacer(width=400)
            dpg.add_image("logo_texture", width=300, height=300)

        dpg.add_spacer(height=5)

        # Recovery key input section
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=490)
            dpg.add_text("Account Recovery", color=(255, 255, 255))

        dpg.add_spacer(height=15)

        with dpg.group(horizontal=True):
            dpg.add_spacer(width=390)
            dpg.add_text("Enter your recovery key to reset your password:")

        dpg.add_spacer(height=15)

        # Recovery key input
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=435)
            dpg.add_input_text(label="", hint="XXXX-XXXX-XXXX-XXXX", width=250, tag="recovery_key")

        dpg.add_spacer(height=15)

        # Buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=485)
            dpg.add_button(label="Cancel", width=75, callback=go_back)
            dpg.add_spacer(width=5)
            dpg.add_button(label="Confirm", width=75, callback=show_password_reset_popup)


def go_back():
    from gui.views.login_view import show_login_view
    set_view(show_login_view)


def show_password_reset_popup():

    # Check if recovery key is entered
    recovery_key = dpg.get_value("recovery_key").strip()
    if not recovery_key:
        # Show error popup for empty recovery key
        with dpg.window(label="Error", modal=True, tag="error_popup", width=300, height=150, pos=[450, 300]):
            dpg.add_text("Please enter your recovery key.")
            dpg.add_spacer(height=20)
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error_popup"), width=100)
        return

    # Validate recovery key first before showing password reset popup
    from config import get_auth_path
    import json
    import base64

    try:
        # Load auth data to get recovery salt and hash
        auth_path = get_auth_path()
        with open(auth_path, 'r') as f:
            auth_data = json.load(f)

        if "recovery_salt" not in auth_data or "recovery_hash" not in auth_data:
            with dpg.window(label="Error", modal=True, tag="error_popup", width=300, height=150, pos=[450, 300]):
                dpg.add_text("No recovery key found for this vault.")
                dpg.add_spacer(height=20)
                dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error_popup"), width=100)
            return

        # Verify the recovery key
        recovery_salt = base64.b64decode(auth_data["recovery_salt"])
        stored_hash = auth_data["recovery_hash"]

        from auth.auth_manager import verify_recovery_key
        if not verify_recovery_key(recovery_key.upper(), stored_hash, recovery_salt):
            with dpg.window(label="Error", modal=True, tag="error_popup", width=300, height=150, pos=[450, 300]):
                dpg.add_text("Invalid recovery key.")
                dpg.add_spacer(height=20)
                dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error_popup"), width=100)
            return

    except Exception as e:
        with dpg.window(label="Error", modal=True, tag="error_popup", width=300, height=150, pos=[450, 300]):
            dpg.add_text(f"Error validating recovery key: {str(e)}")
            dpg.add_spacer(height=20)
            dpg.add_button(label="OK", callback=lambda: dpg.delete_item("error_popup"), width=100)
        return

    # Only reach here if recovery key is valid - now show password reset popup

    # Create password reset popup
    with dpg.window(label="Create New Password", modal=True, tag="password_reset_popup",
                    width=400, height=350, pos=[300, 200]):

        dpg.add_text("Create a new password for your vault:")
        dpg.add_spacer(height=10)

        # New password input
        dpg.add_input_text(label="New Password", password=True, tag="new_password",
                           callback=validate_password_strength, width=250)

        # Confirm password input
        dpg.add_input_text(label="Confirm Password", password=True, tag="confirm_password",
                           callback=validate_password_match, width=250)

        dpg.add_spacer(height=10)

        # Password requirements
        dpg.add_text("Password Requirements:", color=(200, 200, 200))
        dpg.add_text("At least 8 characters", tag="req_length", color=(150, 150, 150))
        dpg.add_text("One uppercase letter", tag="req_upper", color=(150, 150, 150))
        dpg.add_text("One symbol", tag="req_symbol", color=(150, 150, 150))
        dpg.add_text("Passwords must match", tag="req_match", color=(150, 150, 150))

        dpg.add_spacer(height=15)

        # Error/status text
        dpg.add_text("", tag="popup_status_text")

        dpg.add_spacer(height=10)

        # Buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("password_reset_popup"))
            dpg.add_spacer(width=10)
            dpg.add_button(label="Reset Password", callback=attempt_password_recovery)


def validate_password_strength():

    password = dpg.get_value("new_password")

    # Length check
    if len(password) >= 8:
        dpg.configure_item("req_length", color=(100, 255, 100))
    else:
        dpg.configure_item("req_length", color=(150, 150, 150))

    # Uppercase check
    if any(c.isupper() for c in password):
        dpg.configure_item("req_upper", color=(100, 255, 100))
    else:
        dpg.configure_item("req_upper", color=(150, 150, 150))

    # Symbol check
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in symbols for c in password):
        dpg.configure_item("req_symbol", color=(100, 255, 100))
    else:
        dpg.configure_item("req_symbol", color=(150, 150, 150))

    # Also check password match when password changes
    validate_password_match()


def validate_password_match():
    password = dpg.get_value("new_password")
    confirm = dpg.get_value("confirm_password")

    if confirm and password == confirm:
        dpg.configure_item("req_match", color=(100, 255, 100))
    elif confirm:
        dpg.configure_item("req_match", color=(255, 100, 100))
    else:
        dpg.configure_item("req_match", color=(150, 150, 150))


def attempt_password_recovery():
    recovery_key = dpg.get_value("recovery_key").strip()
    new_password = dpg.get_value("new_password")
    confirm_password = dpg.get_value("confirm_password")

    try:
        # Call the recovery function from vault_manager
        result = recover_password(recovery_key, new_password, confirm_password)
        success, message, new_recovery_key = result

        if success:
            # Close password popup
            dpg.delete_item("password_reset_popup")

            # new popup to show after a delay
            def show_delayed_popup():
                show_new_recovery_key_popup(new_recovery_key)

            import threading
            threading.Timer(0.1, show_delayed_popup).start()

        else:
            # Show error message in popup
            dpg.configure_item("popup_status_text", default_value=message, color=(255, 100, 100))

    except Exception as e:
        dpg.configure_item("popup_status_text", default_value=f"Error: {str(e)}", color=(255, 100, 100))


def show_new_recovery_key_popup(new_recovery_key):
    # Delete any existing popup
    if dpg.does_item_exist("new_recovery_popup"):
        dpg.delete_item("new_recovery_popup")

    with dpg.window(label="IMPORTANT: Save Your New Recovery Key", modal=True,
                    tag="new_recovery_popup", width=500, height=300, pos=[250, 200]):
        dpg.add_text("Password reset successful!", color=(100, 255, 100))
        dpg.add_spacer(height=15)

        dpg.add_text("Your new recovery key is:", color=(255, 255, 100))
        dpg.add_spacer(height=10)

        # Display the recovery key as masked by default
        dpg.add_input_text(default_value="****-****-****-****", readonly=True, width=300,
                           tag="display_recovery_key")

        dpg.add_spacer(height=10)

        # Show and Copy buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label="Show Key", callback=lambda: toggle_recovery_key_visibility(new_recovery_key))
            dpg.add_spacer(width=10)
            dpg.add_button(label="Copy to Clipboard",
                           callback=lambda: dpg.set_clipboard_text(new_recovery_key))

        dpg.add_spacer(height=15)

        dpg.add_text("WARNING: Save this recovery key now!", color=(255, 100, 100))
        dpg.add_text("You will not be able to see it again.")
        dpg.add_text("Store it in a safe place separate from your vault.")

        dpg.add_spacer(height=20)

        dpg.add_button(label="I Have Saved My Recovery Key",
                       callback=recovery_complete, width=250)


def toggle_recovery_key_visibility(recovery_key):
    current_value = dpg.get_value("display_recovery_key")
    if current_value == "****-****-****-****":
        # Show the actual key
        dpg.set_value("display_recovery_key", recovery_key)
    else:
        # Hide the key
        dpg.set_value("display_recovery_key", "****-****-****-****")


def recovery_complete():
    dpg.delete_item("new_recovery_popup")
    from gui.views.login_view import show_login_view
    set_view(show_login_view)

