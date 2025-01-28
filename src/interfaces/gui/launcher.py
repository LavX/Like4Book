"""GUI application launcher."""

import sys
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from PyQt6.QtGui import QFontDatabase

from .main_window import MainWindow

def launch_gui():
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    
    # Apply dark theme
    apply_stylesheet(app, theme='dark_teal.xml', invert_secondary=True)
    
    # Ensure emoji font support
    emoji_font = app.font()
    emoji_font.setFamily("Segoe UI Emoji")  # Windows
    emoji_font.setFamily("Noto Color Emoji")  # Linux
    emoji_font.setFamily("Apple Color Emoji")  # macOS
    app.setFont(emoji_font)
    
    # Add material design button styles
    app.setStyleSheet("""
        QPushButton {
            text-transform: none;
            height: 36px;
            padding: 0 16px;
            border-radius: 18px;
            font-weight: 500;
            font-size: 14px;
            background-color: #1e88e5;
            color: white;
            border: none;
            margin: 4px;
        }
        QPushButton:hover {
            background-color: #2196f3;
        }
        QPushButton:pressed {
            background-color: #1976d2;
        }
        QGroupBox {
            font-size: 14px;
            padding-top: 24px;
            margin-top: 8px;
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.05);
        }
        QLabel {
            font-size: 24px;
        }
        .emoji {
            font-family: "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", sans-serif;
            font-size: 24px;
        }
    """)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())