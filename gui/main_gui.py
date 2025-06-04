import pywinstyles
from dearpygui import dearpygui as dpg
import os
from config import AUTH_PATH, get_asset_path
import gui.views.login_view as login_view
import gui.views.signup_view as signup_view
from gui.update_manager import check_post_update_launch, show_update_popup, check_for_updates


def cleanup_existing_items():
    items_to_cleanup = [
        "MainWindow", "SignupWindow", "LoginWindow", "RecoveryView",
        "input_username", "input_password", "input_confirm_password",
        "recovery_key", "new_password", "confirm_password",
        "logo_texture"
    ]

    for item in items_to_cleanup:
        if dpg.does_item_exist(item):
            dpg.delete_item(item)



def run_gui():
    try:
        dpg.destroy_context()
    except:
        pass

    dpg.create_context()

    setup_logo()

    # Check for updates on startup
    update_info = check_for_updates()

    with dpg.window(label="Main Window", tag="MainWindow"):
        if AUTH_PATH and os.path.exists(AUTH_PATH):
            login_view.show_login_view()
        else:
            signup_view.show_signup_view()

    dpg.set_primary_window("MainWindow", True)
    dpg.create_viewport(
        title="The Vault",
        width=1200,
        height=800,
        resizable=False
    )

    try:
        icon_path = get_asset_path('icon.png')
        print(f"Attempting to set icons: {icon_path}")
        print(f"Icon file exists: {os.path.exists(icon_path)}")

        if os.path.exists(icon_path):
            dpg.set_viewport_small_icon(icon_path)
            dpg.set_viewport_large_icon(icon_path)
            print("Icons set successfully")
        else:
            print("Icon file not found, skipping icon setup")

    except Exception as e:
        print(f"Icon setting failed: {e}")
        try:
            icon_ico_path = get_asset_path('icon.ico')
            print(f"Trying .ico format: {icon_ico_path}")
            if os.path.exists(icon_ico_path):
                dpg.set_viewport_small_icon(icon_ico_path)
                dpg.set_viewport_large_icon(icon_ico_path)
                print("ICO icons set successfully")
        except Exception as e2:
            print(f"ICO icon setting also failed: {e2}")

    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Show update popup if available
    if update_info['available']:
        dpg.set_frame_callback(30, lambda: show_update_popup(update_info))

    # Check for post-update launch
    check_post_update_launch()

    # small delay before applying OS-level customizations
    def apply_custom_style():
        from ctypes import windll

        hwnd = windll.user32.FindWindowW(None, "The Vault")
        if hwnd:
            # Disable resizing and maximize button
            GWL_STYLE = -16
            WS_MAXIMIZEBOX = 0x00010000
            WS_SIZEBOX = 0x00040000

            style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            style &= ~WS_MAXIMIZEBOX
            style &= ~WS_SIZEBOX

            windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                                       0x0027)  # SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED

            # Apply custom header color
            pywinstyles.change_header_color(hwnd, "grey")
        else:
            print("Window not found for title bar customization.")

    dpg.set_frame_callback(10, apply_custom_style)

    dpg.start_dearpygui()
    dpg.destroy_context()


def setup_logo():
    # Load and register the logo texture
    logo_path = get_asset_path("logo.png")

    print(f"Looking for logo at: {logo_path}")
    print(f"File exists: {os.path.exists(logo_path)}")

    if not os.path.exists(logo_path):
        print("Logo file not found! Creating placeholder texture.")
        with dpg.texture_registry(show=False):
            import array
            width, height = 300, 300
            data = array.array('f', [0.2, 0.4, 0.8, 1.0] * (width * height))  # Blue color
            dpg.add_static_texture(width, height, data, tag="logo_texture")
        return

    try:
        width, height, channels, data = dpg.load_image(logo_path)
        with dpg.texture_registry(show=False):
            dpg.add_static_texture(width, height, data, tag="logo_texture")
        print(f"Logo loaded successfully: {width}x{height}")
    except Exception as e:
        print(f"Error loading logo: {e}")
        with dpg.texture_registry(show=False):
            import array
            width, height = 300, 300
            data = array.array('f', [0.2, 0.4, 0.8, 1.0] * (width * height))
            dpg.add_static_texture(width, height, data, tag="logo_texture")


if __name__ == "__main__":
    run_gui()