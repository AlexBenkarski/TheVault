import json
import os
import secrets
import platform
import sys
from datetime import datetime, timedelta
from .update_manager import get_current_version
from secrets_encryption import get_firebase_credentials


def get_analytics_file_path():
    """Get writable path for analytics data"""
    if getattr(sys, 'frozen', False):
        # Running as executable - use AppData
        app_data = os.path.join(os.path.expanduser("~"), "AppData", "Local", "TheVault")
        os.makedirs(app_data, exist_ok=True)
        return os.path.join(app_data, "analytics_data.json")
    else:
        # Running as script - use project directory
        from .update_manager import get_app_directory
        return os.path.join(get_app_directory(), "analytics_data.json")


class AnalyticsManager:
    def __init__(self):
        try:
            self.data_file_path = get_analytics_file_path()
            self.analytics_data = None
        except Exception as e:
            raise

    def load_or_create_data(self):
        try:
            if os.path.exists(self.data_file_path):
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    self.analytics_data = json.load(f)

                if "valorant_autofill_triggered_count" not in self.analytics_data.get("feature_usage", {}):
                    if "feature_usage" not in self.analytics_data:
                        self.analytics_data["feature_usage"] = {}

                    self.analytics_data["feature_usage"].update({
                        "valorant_autofill_triggered_count": 0,
                        "valorant_autofill_successful_fills": 0,
                        "valorant_autofill_cancelled_count": 0,
                        "valorant_autofill_error_count": 0,
                        "valorant_autofill_first_used": None,
                        "valorant_autofill_last_used": None,
                    })
                    self.save_data_locally()

            else:
                self.analytics_data = {
                    "vault_id": f"anon_{secrets.token_hex(8)}",
                    "version": get_current_version(),
                    "os": platform.system() + " " + platform.release(),
                    "last_ping": datetime.now().strftime("%Y-%m-%d"),
                    "needs_send": True,
                    "consent_given": None,
                    "consent_prompted": False,
                    "install_metrics": {
                        "days_since_install": 0,
                        "total_app_opens": 0,
                        "opens_last_7_days": 0,
                        "avg_session_length_minutes": 0.0
                    },
                    "vault_stats": {
                        "total_passwords": 0,
                        "total_folders": 0,
                        "largest_folder_size": 0
                    },
                    "feature_usage": {
                        "export_used_ever": False,
                        "recovery_key_used_ever": False,
                        "password_show_clicks": 0,
                        "copy_password_clicks": 0,
                        "update_notifications_seen": 0,
                        "valorant_autofill_triggered_count": 0,
                        "valorant_autofill_successful_fills": 0,
                        "valorant_autofill_cancelled_count": 0,
                        "valorant_autofill_error_count": 0,
                        "valorant_autofill_first_used": None,
                        "valorant_autofill_last_used": None,
                    },
                    "recent_opens": [],
                    "performance": {
                        "avg_startup_time_ms": 0,
                        "vault_decrypt_time_ms": 0,
                        "avg_save_time_ms": 0,
                    }
                }
                self.save_data_locally()

        except Exception as e:
            import traceback
            raise

    def send_to_firebase(self):
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            # Get Firebase config
            firebase_config = get_firebase_credentials()
            if not firebase_config:
                print("Firebase credentials not available")
                return False

            # Initialize Firebase
            if not firebase_admin._apps:
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)

            db = firestore.client()

            # Send complete analytics data
            db.collection("users").document(self.analytics_data["vault_id"]).set(self.analytics_data)

            print("Analytics sent to Firebase successfully")
            return True

        except Exception as e:
            print(f"Firebase send failed: {e}")
            return False

    def save_data_locally(self):
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.analytics_data, f, indent=2)
        except Exception as e:
            import traceback
            raise

    def increment_counter(self, metric_name):
        try:
            parts = metric_name.split('.')
            current = self.analytics_data
            for part in parts[:-1]:
                current = current[part]
            current[parts[-1]] += 1
            self.save_data_locally()
        except (KeyError, TypeError) as e:
            print(f"Failed to increment {metric_name}: {e}")

    def update_metric(self, metric_name, value):
        try:
            parts = metric_name.split('.')
            current = self.analytics_data
            for part in parts[:-1]:
                current = current[part]
            current[parts[-1]] = value
            self.save_data_locally()
        except (KeyError, TypeError) as e:
            print(f"Failed to update {metric_name}: {e}")

    def mark_as_sent(self):
        self.analytics_data["needs_send"] = False
        self.save_data_locally()


_global_analytics_manager = None


def get_or_create_manager():
    global _global_analytics_manager
    try:
        if _global_analytics_manager is None:
            _global_analytics_manager = AnalyticsManager()
            _global_analytics_manager.load_or_create_data()
        return _global_analytics_manager
    except Exception as e:
        import traceback
        return None


def increment_counter(metric_name):
    manager = get_or_create_manager()
    if manager:
        manager.increment_counter(metric_name)


def update_metric(metric_name, value):
    manager = get_or_create_manager()
    if manager:
        manager.update_metric(metric_name, value)


def send_to_firebase():
    manager = get_or_create_manager()
    if not manager:
        return False

    # Only send if user consented
    if not manager.analytics_data.get("consent_given", False):
        print("User declined analytics - skipping send")
        return False

    return manager.send_to_firebase()


def mark_as_sent():
    manager = get_or_create_manager()
    if manager:
        manager.mark_as_sent()


def update_vault_stats(vault_data: dict):
    """Calculate and update vault statistics from current vault data"""
    if not vault_data or not isinstance(vault_data, dict):
        return

    total_passwords = 0
    total_folders = len(vault_data)
    largest_folder_size = 0

    for folder_name, folder_data in vault_data.items():
        entries = folder_data.get("entries", [])
        folder_size = len(entries)
        total_passwords += folder_size
        largest_folder_size = max(largest_folder_size, folder_size)

    # Update the metrics
    update_metric("vault_stats.total_passwords", total_passwords)
    update_metric("vault_stats.total_folders", total_folders)
    update_metric("vault_stats.largest_folder_size", largest_folder_size)


def update_days_since_install():
    """Calculate days since vault creation (first app use)"""
    from config import get_vault_path

    vault_path = get_vault_path()

    if vault_path and os.path.exists(vault_path):
        # Get vault file creation time
        creation_time = os.path.getctime(vault_path)
        creation_date = datetime.fromtimestamp(creation_time)
        current_date = datetime.now()

        # Calculate days difference
        days_diff = (current_date - creation_date).days

        # Update the metric
        update_metric("install_metrics.days_since_install", days_diff)


def update_opens_last_7_days():
    """Track app opens and calculate 7-day rolling count"""
    manager = get_or_create_manager()
    if not manager:
        return

    today = datetime.now().strftime("%Y-%m-%d")

    # Get existing opens list or create new one
    if "recent_opens" not in manager.analytics_data:
        manager.analytics_data["recent_opens"] = []

    recent_opens = manager.analytics_data["recent_opens"]

    # Add today's date if not already added
    if today not in recent_opens:
        recent_opens.append(today)

    # Remove dates older than 7 days
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    manager.analytics_data["recent_opens"] = [
        date for date in recent_opens
        if date >= seven_days_ago
    ]

    # Update the metric
    opens_count = len(manager.analytics_data["recent_opens"])
    manager.update_metric("install_metrics.opens_last_7_days", opens_count)

    # Save the updated data
    manager.save_data_locally()


def has_been_prompted_for_consent():
    manager = get_or_create_manager()
    if manager:
        return manager.analytics_data.get("consent_prompted", False)
    return False


def set_consent_choice(consent_given):
    try:
        manager = get_or_create_manager()

        if not manager:
            return False

        if not hasattr(manager, 'analytics_data'):
            return False

        if not manager.analytics_data:
            return False

        manager.analytics_data["consent_given"] = consent_given
        manager.analytics_data["consent_prompted"] = True
        manager.save_data_locally()

        return True

    except Exception as e:
        import traceback
        return False


def should_collect_analytics():
    try:
        manager = get_or_create_manager()
        if manager and manager.analytics_data:
            result = manager.analytics_data.get("consent_given", False)
            return result
        return False
    except Exception as e:
        return False


def send_firebase_consent_ping(consent_given):
    """Send one-time consent ping to Firebase regardless of user choice"""
    temp_file_path = None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        firebase_config = get_firebase_credentials()
        temp_file_path = firebase_config

        if not firebase_config:
            return False

        try:
            cred = credentials.Certificate(firebase_config)
        except Exception as cred_error:
            return False

        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
        except Exception as init_error:
            return False

        try:
            db = firestore.client()
        except Exception as db_error:
            return False

        manager = get_or_create_manager()
        if not manager:
            return False

        consent_data = {
            "vault_id": manager.analytics_data["vault_id"],
            "consent_given": consent_given,
            "consent_timestamp": datetime.now().isoformat(),
            "version": manager.analytics_data["version"],
            "os": manager.analytics_data["os"]
        }

        try:
            db.collection("consent").document(manager.analytics_data["vault_id"]).set(consent_data)
            return True
        except Exception as write_error:
            return False

    except ImportError as e:
        return False
    except Exception as e:
        import traceback
        return False
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                pass


def track_valorant_autofill_triggered():
    """Track when auto-fill overlay appears"""
    manager = get_or_create_manager()
    if not manager:
        return

    manager.analytics_data["feature_usage"]["valorant_autofill_triggered_count"] += 1

    # Set first use timestamp
    if not manager.analytics_data["feature_usage"]["valorant_autofill_first_used"]:
        manager.analytics_data["feature_usage"]["valorant_autofill_first_used"] = datetime.now().isoformat()

    manager.analytics_data["feature_usage"]["valorant_autofill_last_used"] = datetime.now().isoformat()
    manager.save_data_locally()


def track_valorant_autofill_success():
    """Track successful credential filling"""
    manager = get_or_create_manager()
    if not manager:
        return

    manager.analytics_data["feature_usage"]["valorant_autofill_successful_fills"] += 1
    manager.save_data_locally()


def track_valorant_autofill_cancelled():
    """Track when user cancels auto-fill"""
    manager = get_or_create_manager()
    if not manager:
        return

    manager.analytics_data["feature_usage"]["valorant_autofill_cancelled_count"] += 1
    manager.save_data_locally()


def track_valorant_autofill_error(error_type):
    """Track auto-fill errors"""
    manager = get_or_create_manager()
    if not manager:
        return

    manager.analytics_data["feature_usage"]["valorant_autofill_error_count"] += 1
    manager.save_data_locally()

