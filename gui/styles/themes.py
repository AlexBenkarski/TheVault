DARK_THEME = """
QMainWindow {
    background: transparent;
}

QWidget#mainWidget {
    background: #2d2d30;
    border-radius: 15px;
}

QWidget {
    background: transparent;
    color: #ffffff;
}

QWidget#titleBar {
    background: #2d2d30;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
}

QLabel#titleLabel {
    color: #ffffff;
    font-weight: 500;
}

QLabel#versionLabel {
    color: #ffffff;
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

QLabel {
    color: #ffffff;
}

QLabel#subtitle {
    color: #b0b0b0;
}

QWidget#leftPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #2a2a2d, stop:1 #232326);
}

QWidget#rightPanel {
    background: #2d2d30;
}

QLabel#featureText {
    color: #e0e0e0;
    padding: 4px 0px;
}

QCheckBox {
    color: #ffffff;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.1);
}

QCheckBox::indicator:hover {
    border: 2px solid rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.15);
}

QCheckBox::indicator:checked {
    border: 2px solid #4CAF50;
    background: #4CAF50;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}

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

/* Entry Widget Styles */
QFrame[entryWidget="true"] {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    margin: 2px;
}

QFrame[entryWidget="true"][expanded="true"] {
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid #4CAF50;
    border-radius: 8px;
    margin: 2px;
}

QPushButton[entryHeader="true"] {
    background: transparent;
    border: none;
    color: #ffffff;
    font-size: 13px;
    font-weight: bold;
    text-align: left;
    padding-left: 15px;
    outline: none;
    border-radius: 8px;
}

QPushButton[entryHeader="true"]:hover {
    background: rgba(255, 255, 255, 0.1);
}

QPushButton[entryHeader="true"]:focus {
    outline: none;
    border: none;
}

/* Small Action Buttons */
QPushButton[smallButton="true"] {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    color: #ffffff;
    font-size: 9px;
    font-weight: bold;
    outline: none;
}

QPushButton[smallButton="true"]:hover {
    background: rgba(255, 255, 255, 0.2);
}

QPushButton[smallButton="true"]:focus {
    outline: none;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

QPushButton[smallButton="true"][delete="true"] {
    background: rgba(255, 87, 87, 0.2);
    border: 1px solid rgba(255, 87, 87, 0.4);
    color: #ff5757;
}

QPushButton[smallButton="true"][delete="true"]:hover {
    background: rgba(255, 87, 87, 0.3);
}

QPushButton[smallButton="true"][delete="true"]:focus {
    outline: none;
    border: 1px solid rgba(255, 87, 87, 0.6);
}

/* Dialog Styles */
QDialog[modern="true"] {
    background: #2d2d30;
    color: #ffffff;
    border: 2px solid #4CAF50;
    border-radius: 8px;
}

QLineEdit[modern="true"] {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 8px 12px;
    color: #ffffff;
}

QLineEdit[modern="true"]:focus {
    border: 2px solid #4CAF50;
    background: rgba(255, 255, 255, 0.15);
}

QTextEdit[modern="true"] {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 8px 12px;
    color: #ffffff;
}

QTextEdit[modern="true"]:focus {
    border: 2px solid #4CAF50;
    background: rgba(255, 255, 255, 0.15);
}
"""


def apply_theme(app_instance):
    app_instance.setStyleSheet(DARK_THEME)