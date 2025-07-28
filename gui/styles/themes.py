DARK_THEME = """
/* ===========================================
   MAIN WINDOW & LAYOUT - FIXED
   =========================================== */

QMainWindow {
    background: #2d2d30;  /* CHANGED: Was transparent */
}

QWidget#mainWidget {
    background: #2d2d30;
    border-radius: 15px;
}

QWidget {
    background: transparent;
    color: #ffffff;
    font-family: "Segoe UI", system-ui, sans-serif;
}
QLabel#navLogo {
    background: #4CAF50;
    color: white;
    border-radius: 12px;
    font-weight: bold;
    font-size: 14px;
}

QLabel#navAppName {
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
}

/* ===========================================
   NAVIGATION BAR (TOP)
   =========================================== */

QWidget#navBar {
    background: #1a1a1d;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

QPushButton#navTab {
    background: transparent;
    border: none;
    border-radius: 8px;
    color: #888888;
    font-size: 11px;
    font-weight: 500;
}

QPushButton#navTab[active="true"] {
    background: rgba(76, 175, 80, 0.15);
    color: #4CAF50;
}

QPushButton#navTab:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #ffffff;
}

QLabel#navTabIcon {
    font-size: 14px;
    background: transparent;
}

QLabel#navTabText {
    font-size: 11px;
    font-weight: 500;
    background: transparent;
}

QLineEdit#navSearch {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #ffffff;
    font-size: 12px;
    padding: 0px 12px;
}

QPushButton#navNotification, QPushButton#navUser {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #ffffff;
    font-size: 14px;
}

QPushButton#navUser {
    background: #4CAF50;
    font-weight: bold;
    font-size: 12px;
}

/* ===========================================
   LEFT SIDEBAR
   =========================================== */

QWidget#leftPanel {
    background: #1a1a1d;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* Security Health */
QWidget#securityHealth {
    background: #2d2d30;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

QLabel#securityTitle {
    color: #ffffff;
    font-size: 12px;
    font-weight: bold;
    background: transparent;
}

QLabel#securityStatus[hasIssues="true"] {
    color: #ff9500;
    font-size: 11px;
    font-weight: 600;
    background: transparent;
}

QLabel#securityStatus[hasIssues="false"] {
    color: #4CAF50;
    font-size: 11px;
    font-weight: 600;
    background: transparent;
}

QLabel#securityDesc {
    color: #888888;
    font-size: 11px;
    background: transparent;
}

/* ===========================================
   FOLDER LIST STYLES
   =========================================== */

QPushButton#folderItemBtn {
    background: transparent;
    border: none;
    border-radius: 6px;
    text-align: left;
}

QPushButton#folderItemBtn[selected="true"] {
    background: rgba(76, 175, 80, 0.15);
}

QPushButton#folderItemBtn:hover {
    background: rgba(255, 255, 255, 0.05);
}

QWidget#folderIcon[color="red"] { 
    background: #ff6b6b; 
    border-radius: 6px; 
}
QWidget#folderIcon[color="orange"] { 
    background: #ffa726; 
    border-radius: 6px; 
}
QWidget#folderIcon[color="blue"] { 
    background: #42a5f5; 
    border-radius: 6px; 
}
QWidget#folderIcon[color="green"] { 
    background: #66bb6a; 
    border-radius: 6px; 
}
QWidget#folderIcon[color="purple"] { 
    background: #ab47bc; 
    border-radius: 6px; 
}
QWidget#folderIcon[color="gray"] { 
    background: #666666; 
    border-radius: 6px; 
}

QLabel#folderIconLabel {
    background: transparent;
    font-size: 14px;
}

QLabel#folderName {
    color: #ffffff;
    font-size: 11px;
    font-weight: 500;
    background: transparent;
}

QLabel#folderCount {
    color: #888888;
    font-size: 9px;
    background: transparent;
}

QWidget#folderIndicator[selected="true"] {
    background: #4CAF50;
    border-radius: 1px;
}

QWidget#folderIndicator {
    background: transparent;
}

/* ===========================================
   PASSWORD CARDS
   =========================================== */

QWidget#passwordCard {
    background: #3a3a3d;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

QWidget#passwordCard:hover {
    background: #404043;
    border: 1px solid rgba(255, 255, 255, 0.12);
}

QLabel#expandArrow {
    color: #666666;
    font-size: 12px;
    background: transparent;
}

QLabel#cardTitle {
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
    background: transparent;
}

QLabel#cardSubtitle {
    color: #888888;
    font-size: 12px;
    background: transparent;
}

QPushButton#cardCopyBtn {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    color: #ffffff;
    font-size: 10px;
    font-weight: 500;
}

QPushButton#cardEditBtn, QPushButton#cardDeleteBtn {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    font-size: 12px;
}

QPushButton#cardDeleteBtn {
    background: rgba(255, 71, 87, 0.1);
    border: 1px solid rgba(255, 71, 87, 0.3);
    color: #ff4757;
}

/* ===========================================
   TITLE BAR & WINDOW CONTROLS
   =========================================== */

QWidget#titleBar {
    background: #2d2d30;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
}

QLabel#titleLabel {
    color: #ffffff;
    font-weight: 500;
    background: transparent;
}

QLabel#versionLabel {
    color: #ffffff;
    background: transparent;
}

QPushButton#windowControl {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 15px;
    color: #ffffff;
    font-size: 16px;
    font-weight: bold;
}

QPushButton#windowControl:hover {
    background: rgba(255, 255, 255, 0.2);
}

QPushButton#closeControl {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 15px;
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
}

QPushButton#closeControl:hover {
    background: #ff4757;
}

/* ===========================================
   MODERN WIDGETS (Your custom components)
   =========================================== */

ModernLineEdit {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 8px 12px;
    color: #ffffff;
    selection-background-color: #4CAF50;
}

ModernLineEdit:focus {
    border: 2px solid #4CAF50;
    background: rgba(255, 255, 255, 0.15);
    padding: 7px 11px;
}

ModernLineEdit::placeholder {
    color: #888888;
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
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4CAF50, stop:1 #45a049);
    color: white;
}

ModernButton[primary="true"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #45a049, stop:1 #3d8b40);
}

ModernButton[primary="true"]:pressed {
    background: #3d8b40;
}

ModernButton[primary="false"] {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.25);
}

ModernButton[primary="false"]:hover {
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.35);
}

ModernButton[primary="false"]:pressed {
    background: rgba(255, 255, 255, 0.2);
}

/* ===========================================
   GENERAL LABELS & TEXT
   =========================================== */

QLabel {
    color: #ffffff;
    background: transparent;
}

QLabel#subtitle {
    color: #b0b0b0;
    background: transparent;
}

/* ===========================================
   SCROLLBARS
   =========================================== */

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: rgba(255, 255, 255, 0.1);
    width: 12px;
    border-radius: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.5);
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
    background: #2d2d30;
    color: #ffffff;
    border: 2px solid #4CAF50;
    border-radius: 8px;
}

/* ===========================================
   FOCUS STATES
   =========================================== */

QPushButton:focus {
    outline: none;
    border: none;
}

ModernButton:focus {
    outline: none;
    border: none;
}

QLineEdit:focus {
    outline: none;
}

ModernLineEdit:focus {
    outline: none;
}
"""

def apply_theme(app_instance):
    app_instance.setStyleSheet(DARK_THEME)