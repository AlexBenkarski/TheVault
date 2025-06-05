# The Vault - Development Cheat Sheet

## 🌿 Git Commands

### Branch Management
```bash
# See all branches (local and remote)
git branch -a

# Create and switch to new branch
git checkout -b branch-name

# Switch to existing branch
git checkout branch-name

# Push new branch to GitHub
git push origin branch-name

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name
```

### Daily Workflow
```bash
# Check status
git status

# Stage all changes (including deletions)
git add -A

# Commit changes
git commit -m "Your commit message"

# Push to current branch
git push

# Pull latest changes
git pull origin branch-name
```

### Merging
```bash
# Merge branch into current branch
git merge branch-name

# Merge feature branch into main
git checkout main
git merge feature-branch
git push origin main
```

### Fixing Common Issues
```bash
# Pull before push (when rejected)
git pull origin branch-name

# Force push (use carefully!)
git push --force

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See commit history
git log --oneline
```

---

## 🔨 Build Commands

### Build Main Application
```bash
# Clean build with icon and assets
pyinstaller --clean --onefile --windowed --add-data "assets;assets" --icon=assets/icon.ico gui/main_gui.py --name Vault

# For PyQt6 (when you switch)
pyinstaller --clean --onefile --windowed --add-data "assets;assets" --icon=assets/icon.ico main.py --name Vault
```

### Build Updater
```bash
# Build updater with admin privileges
pyinstaller --clean --onefile --console --icon=assets/icon.ico updater.py
```

### Build Both (Full Release)
```bash
# Build main app
pyinstaller --clean --onefile --windowed --add-data "assets;assets" --icon=assets/icon.ico gui/main_gui.py --name Vault

# Build updater
pyinstaller --clean --onefile --console --icon=assets/icon.ico updater.py

# Check results
Get-ChildItem dist/
```

---

## 📦 Installer Commands

### Prepare Installer Files
```powershell
# Create directories
New-Item -ItemType Directory -Force -Path "installer\setup_files"
New-Item -ItemType Directory -Force -Path "installer\setup_files\assets"

# Copy build files
Copy-Item "dist\Vault.exe" "installer\setup_files\" -Force
Copy-Item "dist\updater.exe" "installer\setup_files\" -Force
Copy-Item "version.txt" "installer\setup_files\" -Force
Copy-Item "assets\*" "installer\setup_files\assets\" -Recurse -Force

# Verify files copied
Get-ChildItem "installer\setup_files\" -Recurse
```

### Build Installer
```
1. Open Inno Setup
2. File → Open → installer\setup.iss
3. Build → Compile (F9)
4. Output: installer\output\TheVault_Setup_v1.0.0.exe
```

---

## 🚀 Release Workflow

### 1. Prepare Release
```bash
# Make sure you're on main branch
git checkout main

# Set version in update_manager.py
CURRENT_VERSION = "1.0.X"

# Update version.txt
echo 1.0.X > version.txt

# Commit version changes
git add .
git commit -m "Version 1.0.X release"
git push origin main
```

### 2. Build Everything
```powershell
# Build executables
pyinstaller --clean --onefile --windowed --add-data "assets;assets" --icon=assets/icon.ico gui/main_gui.py --name Vault
pyinstaller --clean --onefile --console --icon=assets/icon.ico updater.py

# Prepare installer
Copy-Item "dist\Vault.exe" "installer\setup_files\" -Force
Copy-Item "dist\updater.exe" "installer\setup_files\" -Force
Copy-Item "version.txt" "installer\setup_files\" -Force

# Build installer in Inno Setup
```

### 3. GitHub Release
```
1. Go to GitHub → Releases → Create new release
2. Tag: v1.0.X
3. Title: The Vault v1.0.X - Description
4. Upload:
   - TheVault_Setup_v1.0.X.exe (installer)
   - Vault.exe (for auto-updates)
5. Publish release
```

---

## 🐛 Testing Commands

### Test Update System
```powershell
# Test manually
cd "C:\Program Files (x86)\TheVault"
.\updater.exe "https://github.com/AlexBenkarski/TheVault/releases/download/v1.0.1/Vault.exe" "1.0.1" "Test update"

# Test from Python
python -c "from gui.update_manager import check_for_updates; print(check_for_updates())"
```

### Debug Builds
```powershell
# Run and see console output
.\dist\Vault.exe

# Check file sizes
Get-ChildItem dist/

# Verify icon
# Right-click exe → Properties → should show icon
```

---

## 📁 Important File Locations

### Development Files
```
TheVault/
├── gui/main_gui.py          # Current main app
├── updater.py               # Auto-updater
├── gui/update_manager.py    # Update system
├── version.txt              # Version file
├── assets/icon.ico          # App icon
└── installer/setup.iss      # Installer script
```

### Build Output
```
dist/
├── Vault.exe               # Main application
└── updater.exe             # Auto-updater

installer/output/
└── TheVault_Setup_v1.0.0.exe  # Installer
```

### Installation Paths
```
C:\Program Files (x86)\TheVault\    # Installed app
C:\Users\[user]\OneDrive\TheVault\  # User vault data (default)
```

---

## 🔧 Version Management

### For New Release
```python
# In gui/update_manager.py
CURRENT_VERSION = "1.0.X"

# In version.txt
1.0.X

# In installer/setup.iss
AppVersion=1.0.X
OutputBaseFilename=TheVault_Setup_v1.0.X
```

### Version Numbering
- **1.0.X** - Bug fixes, small updates
- **1.X.0** - New features (like PyQt6 GUI)
- **X.0.0** - Major rewrites

---

## 🎯 Quick Commands for Common Tasks

### Start New Feature
```bash
git checkout main
git pull origin main
git checkout -b feature-name
```

### Daily Work
```bash
git add -A
git commit -m "Description of changes"
git push origin branch-name
```

### Finish Feature
```bash
git checkout main
git merge feature-name
git push origin main
git branch -d feature-name
```

### Emergency Hotfix
```bash
# Build fix
pyinstaller --clean --onefile --windowed --add-data "assets;assets" --icon=assets/icon.ico gui/main_gui.py --name Vault

# Quick GitHub release (just exe, no installer needed)
# Upload Vault.exe to new release
```

---

## 💡 Pro Tips

- Always test installer on clean machine
- Keep version numbers in sync (code, files, releases)
- Use descriptive commit messages
- Test auto-update before releasing
- Backup working versions before major changes