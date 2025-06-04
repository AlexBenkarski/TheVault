The Vault
A secure, modern password manager with automatic update functionality built with Python.

🔐 Features
Secure Password Storage: High-grade encryption for all of your passwords
Auto-Update System: Seamlessly updates to the latest version automatically
Secure Recovery: Recovery key system for account restoration

📥 Installation
For New Users
Download the latest installer: TheVault_Setup_v1.0.0.exe from Releases
Run the installer and follow the setup wizard
Launch The Vault from your desktop or start menu

For Developers
Clone the repository
git clone https://github.com/AlexBenkarski/TheVault.git
cd TheVault

# Install dependencies
pip install -r requirements.txt

# Run from source
python main_gui.py


🔄 Auto-Update System
The Vault includes an intelligent auto-update system that:

Checks for new releases on startup
Downloads and installs updates automatically
Preserves your data during updates
Shows patch notes for new features

🛠️ Building from Source
To create your own executables:
bash# Install PyInstaller
pip install pyinstaller

# Build main application
pyinstaller --onefile main.py --name TheVault

# Build updater
pyinstaller --onefile updater.py
    
Requirements

Python 3.8+
Dear PyGui
Cryptography libraries
See requirements.txt for full list

🔒 Security
All passwords are encrypted using industry-standard cryptography
Local storage only - no cloud dependencies
Recovery key system for account restoration

🐛 Bug Reports & Feature Requests
Found a bug or have a feature request? Please create an issue on the Issues page.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

⚠️ Disclaimer
This software is provided "as is" without warranty of any kind. Please ensure you have backups of your important data.

The Vault - Secure. Simple. Smart.
