DARK_THEME = """
/* ===========================================
   DESIGN TOKENS - All colors and spacing
   =========================================== */

/* Core Colors */
:root {
    --primary-green: #4CAF50;
    --primary-green-hover: #45a049;
    --primary-green-light: rgba(76, 175, 80, 0.15);

    --background-main: #2d2d30;
    --background-sidebar: #1a1a1d;
    --background-card: #3a3a3d;
    --background-card-hover: #404043;

    --text-primary: #ffffff;
    --text-secondary: #888888;
    --text-muted: #666666;

    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-light: rgba(255, 255, 255, 0.15);
    --border-medium: rgba(255, 255, 255, 0.25);

    --danger-red: #ff4757;
    --warning-orange: #ffa726;
    --info-blue: #42a5f5;

    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 12px;
    --spacing-lg: 16px;
    --spacing-xl: 20px;
    --spacing-xxl: 24px;
}

/* ===========================================
   MAIN WINDOW & LAYOUT
   =========================================== */

QMainWindow {
    background: transparent;
}

QWidget#mainWidget {
    background: var(--background-main);
    border-radius: 15px;
}

QWidget {
    background: transparent;
    color: var(--text-primary);
    font-family: "Segoe UI", system-ui, sans-serif;
}

/* ===========================================
   NAVIGATION BAR (TOP)
   =========================================== */

/* Navigation container */
QWidget[objectName="navBar"] {
    background: var(--background-sidebar);
    border-bottom: 1px solid var(--border-subtle);
}

/* Navigation tabs */
QPushButton[objectName="navTab"] {
    background: transparent;
    border: none;
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 500;
    padding: 8px 12px;
    text-align: left;
}

QPushButton[objectName="navTab"]:hover {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary);
}

QPushButton[objectName="navTab"][active="true"] {
    background: var(--primary-green-light);
    color: var(--primary-green);
    font-weight: 600;
}

/* Search bar */
QLineEdit[objectName="searchBar"] {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 12px;
    padding: 8px 12px;
}

QLineEdit[objectName="searchBar"]:focus {
    border: 1px solid var(--primary-green);
    background: rgba(255, 255, 255, 0.08);
}

QLineEdit[objectName="searchBar"]::placeholder {
    color: var(--text-muted);
}

/* Profile and control buttons */
QPushButton[objectName="profileBtn"] {
    background: var(--primary-green);
    border: none;
    border-radius: 18px;
    color: white;
    font-size: 12px;
    font-weight: bold;
}

QPushButton[objectName="profileBtn"]:hover {
    background: var(--primary-green-hover);
}

QPushButton[objectName="windowControl"] {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 15px;
    color: var(--text-primary);
    font-weight: bold;
}

QPushButton[objectName="windowControl"]:hover {
    background: rgba(255, 255, 255, 0.2);
}

QPushButton[objectName="closeControl"]:hover {
    background: var(--danger-red);
}

/* ===========================================
   LEFT SIDEBAR
   =========================================== */

QWidget[objectName="leftSidebar"] {
    background: var(--background-sidebar);
    border-right: 1px solid var(--border-subtle);
}

/* Security Health Section */
QWidget[objectName="securityHealth"] {
    background: var(--background-main);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
}

/* Folders Section */
QLabel[objectName="sectionTitle"] {
    color: var(--text-muted);
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Individual folder items */
QWidget[objectName="folderItem"] {
    background: transparent;
    border-radius: 6px;
    padding: 8px 12px;
}

QWidget[objectName="folderItem"]:hover {
    background: rgba(255, 255, 255, 0.05);
}

QWidget[objectName="folderItem"][selected="true"] {
    background: var(--primary-green-light);
}

/* Folder icons */
QLabel[objectName="folderIcon"] {
    border-radius: 6px;
    font-size: 14px;
    text-align: center;
}

/* Folder text */
QLabel[objectName="folderName"] {
    color: var(--text-primary);
    font-size: 11px;
    font-weight: 500;
}

QLabel[objectName="folderCount"] {
    color: var(--text-secondary);
    font-size: 9px;
}

/* Selection indicator */
QWidget[objectName="selectionIndicator"] {
    background: transparent;
    border-radius: 1px;
}

QWidget[objectName="selectionIndicator"][selected="true"] {
    background: var(--primary-green);
}

/* Quick Actions */
QPushButton[objectName="quickAction"] {
    background: transparent;
    border: 1px solid var(--border-light);
    border-radius: 6px;
    color: var(--text-primary);
    font-size: 10px;
    padding: 8px 12px;
    text-align: left;
}

QPushButton[objectName="quickAction"]:hover {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-medium);
}

/* Recent Activity */
QLabel[objectName="activityText"] {
    color: var(--text-primary);
    font-size: 10px;
}

QLabel[objectName="activityTime"] {
    color: var(--text-secondary);
    font-size: 8px;
}

/* ===========================================
   MAIN CONTENT AREA (RIGHT)
   =========================================== */

QWidget[objectName="mainContent"] {
    background: var(--background-main);
}

/* Content header */
QWidget[objectName="contentHeader"] {
    background: transparent;
    border-bottom: 1px solid var(--border-subtle);
    padding: var(--spacing-xxl);
}

QLabel[objectName="contentTitle"] {
    color: var(--text-primary);
    font-size: 24px;
    font-weight: bold;
}

QLabel[objectName="contentSubtitle"] {
    color: var(--text-secondary);
    font-size: 12px;
}

QLabel[objectName="contentPrefix"] {
    color: var(--text-muted);
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

/* Header action buttons */
QPushButton[objectName="headerAction"] {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 12px;
    font-weight: 500;
    padding: 8px 16px;
}

QPushButton[objectName="headerAction"]:hover {
    background: rgba(255, 255, 255, 0.12);
}

QPushButton[objectName="headerActionDanger"] {
    background: rgba(255, 71, 87, 0.1);
    border: 1px solid rgba(255, 71, 87, 0.3);
    color: var(--danger-red);
}

QPushButton[objectName="headerActionDanger"]:hover {
    background: rgba(255, 71, 87, 0.15);
}

QPushButton[objectName="headerActionPrimary"] {
    background: var(--primary-green);
    border: none;
    color: white;
    font-weight: 600;
}

QPushButton[objectName="headerActionPrimary"]:hover {
    background: var(--primary-green-hover);
}

/* ===========================================
   PASSWORD CARDS
   =========================================== */

QWidget[objectName="passwordCard"] {
    background: var(--background-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    margin: 2px;
}

QWidget[objectName="passwordCard"]:hover {
    background: var(--background-card-hover);
    border: 1px solid var(--border-light);
}

/* Card content */
QLabel[objectName="cardTitle"] {
    color: var(--text-primary);
    font-size: 15px;
    font-weight: 500;
}

QLabel[objectName="cardSubtitle"] {
    color: var(--text-secondary);
    font-size: 12px;
}

QLabel[objectName="cardIcon"] {
    color: var(--text-muted);
    font-size: 12px;
}

/* Card action buttons */
QPushButton[objectName="cardAction"] {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid var(--border-light);
    border-radius: 6px;
    color: var(--text-primary);
    font-size: 10px;
    font-weight: 500;
}

QPushButton[objectName="cardAction"]:hover {
    background: rgba(255, 255, 255, 0.12);
}

QPushButton[objectName="cardActionDanger"] {
    background: rgba(255, 71, 87, 0.1);
    border: 1px solid rgba(255, 71, 87, 0.3);
    color: var(--danger-red);
}

QPushButton[objectName="cardActionDanger"]:hover {
    background: rgba(255, 71, 87, 0.15);
}

/* ===========================================
   MODERN WIDGETS (Your custom components)
   =========================================== */

ModernLineEdit {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 8px 12px;
    color: var(--text-primary);
    selection-background-color: var(--primary-green);
}

ModernLineEdit:focus {
    border: 2px solid var(--primary-green);
    background: rgba(255, 255, 255, 0.15);
    padding: 7px 11px;
}

ModernLineEdit::placeholder {
    color: var(--text-secondary);
}

ModernButton {
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

ModernButton[primary="true"] {
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--primary-green-hover) 100%);
    color: white;
}

ModernButton[primary="true"]:hover {
    background: linear-gradient(135deg, var(--primary-green-hover) 0%, #3d8b40 100%);
}

ModernButton[primary="false"] {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-primary);
    border: 2px solid var(--border-medium);
}

ModernButton[primary="false"]:hover {
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.35);
}

/* ===========================================
   SCROLLBARS
   =========================================== */

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: rgba(255, 255, 255, 0.05);
    width: 8px;
    border-radius: 4px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.3);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}

/* ===========================================
   DIALOGS
   =========================================== */

QDialog[modern="true"] {
    background: var(--background-main);
    color: var(--text-primary);
    border: 2px solid var(--primary-green);
    border-radius: 12px;
}

/* ===========================================
   STATES & FOCUS
   =========================================== */

/* Remove focus outlines */
QPushButton:focus, ModernButton:focus, QLineEdit:focus, ModernLineEdit:focus {
    outline: none;
}

/* Disabled states */
*:disabled {
    opacity: 0.5;
}

/* ===========================================
   ANIMATIONS (Future)
   =========================================== */

/* All hover transitions */
* {
    transition: all 0.2s ease;
}
"""


def apply_theme(app_instance):
    """Apply the complete theme to the application"""
    app_instance.setStyleSheet(DARK_THEME)