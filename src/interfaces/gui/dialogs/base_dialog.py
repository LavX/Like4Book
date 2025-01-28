"""Base dialog implementation with common functionality."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class BaseDialog(QDialog):
    """Base dialog with common functionality."""
    
    def __init__(self, parent=None, title=""):
        """Initialize base dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Status label for showing messages
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("", 11))
        self.status_label.hide()
        self.layout.addWidget(self.status_label)
        
        # Apply material design styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
            QPushButton:pressed {
                background-color: #1976d2;
            }
            QPushButton#closeButton {
                background-color: #424242;
            }
            QPushButton#closeButton:hover {
                background-color: #616161;
            }
            QSpinBox {
                background-color: #424242;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #616161;
                border-radius: 2px;
            }
            QProgressBar {
                border: none;
                background-color: #424242;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196f3;
                border-radius: 4px;
            }
            QGroupBox {
                color: white;
                font-weight: bold;
                padding-top: 16px;
            }
        """)
        
    def show_error(self, message: str):
        """Show error message.
        
        Args:
            message: Error message to display
        """
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet("color: #f44336;")  # Red color for errors
        self.status_label.show()
        
    def show_success(self, message: str):
        """Show success message.
        
        Args:
            message: Success message to display
        """
        self.status_label.setText(f"✅ {message}")
        self.status_label.setStyleSheet("color: #4caf50;")  # Green color for success
        self.status_label.show()
        
    def show_notice(self, message: str):
        """Show notice message.
        
        Args:
            message: Notice message to display
        """
        self.status_label.setText(f"ℹ️ {message}")
        self.status_label.setStyleSheet("color: #2196f3;")  # Blue color for notices
        self.status_label.show()