def get_mock_vault_data(preset_name):
    presets = {
        "empty": {},

        "small": {
            "Gaming": {
                "schema": ["Title", "username", "password"],
                "entries": [
                    {"Title": "Steam", "username": "gamer123", "password": "SecurePass1!"},
                    {"Title": "Epic Games", "username": "gamer123", "password": "EpicPass2@"}
                ]
            },
            "Personal": {
                "schema": ["Title", "email", "password"],
                "entries": [
                    {"Title": "Gmail", "email": "user@gmail.com", "password": "Gmail123!"}
                ]
            }
        },

        "large": {
            "Gaming": {
                "schema": ["Title", "username", "password"],
                "entries": [
                    {"Title": f"Game Account {i}", "username": f"user{i}", "password": f"Pass{i}!"}
                    for i in range(1, 51)
                ]
            },
            "Banking": {
                "schema": ["Title", "account", "pin"],
                "entries": [
                    {"Title": f"Bank {i}", "account": f"12345{i:04d}", "pin": f"{1000 + i}"}
                    for i in range(1, 21)
                ]
            },
            "Social": {
                "schema": ["Title", "username", "password", "email"],
                "entries": [
                    {"Title": f"Social Site {i}", "username": f"social{i}", "password": f"Social{i}!",
                     "email": f"user{i}@email.com"}
                    for i in range(1, 31)
                ]
            }
        },

        "massive": {
            **{
                f"Category_{i:02d}": {
                    "schema": ["Title", "username", "password", "notes"],
                    "entries": [
                        {
                            "Title": f"Account_{j:03d}_in_Cat{i:02d}",
                            "username": f"user{i}{j}@example.com",
                            "password": f"Pass{i}{j}!@#",
                            "notes": f"Test entry {j} in category {i}"
                        }
                        for j in range(1, 1001)  # 1000 entries per folder
                    ]
                }
                for i in range(1, 1001)  # 1000 folders
            }
        }
    }
    return presets.get(preset_name, {})




