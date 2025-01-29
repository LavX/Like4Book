"""Profile exchange dialog implementation."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QSpinBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ....i18n.manager import i18n
from .base_dialog import BaseDialog

class ProfileExchangeDialog(BaseDialog):
    """Dialog for exchanging profiles/pages for followers."""
    
    def __init__(self, parent=None, credits_service=None, l4l_cookies=None):
        """Initialize profile exchange dialog.
        
        Args:
            parent: Parent widget
            credits_service: Credits service instance
            l4l_cookies: Like4Like cookies
        """
        super().__init__(parent, i18n.get_text('menu.exchange_profile'))
        
        self.credits_service = credits_service
        self.l4l_cookies = l4l_cookies
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        # Input frame
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(15)
        
        # Profile URL input
        url_layout = QVBoxLayout()
        url_label = QLabel(i18n.get_text('actions.enter_profile'))
        url_label.setFont(QFont("", 11))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://facebook.com/profile...")
        self.url_input.setMinimumWidth(300)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        input_layout.addLayout(url_layout)
        
        # Credits input
        credits_layout = QVBoxLayout()
        credits_label = QLabel(i18n.get_text('actions.enter_credits'))
        credits_label.setFont(QFont("", 11))
        self.credits_input = QSpinBox()
        self.credits_input.setMinimum(2)
        self.credits_input.setMaximum(21)
        self.credits_input.setValue(10)
        self.credits_input.setMinimumWidth(100)
        credits_layout.addWidget(credits_label)
        credits_layout.addWidget(self.credits_input)
        input_layout.addLayout(credits_layout)
        
        self.layout.addWidget(input_frame)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Exchange button
        self.exchange_btn = QPushButton(i18n.get_text('actions.exchange'))
        self.exchange_btn.setFont(QFont("", 11))
        self.exchange_btn.clicked.connect(self.handle_exchange)
        button_layout.addWidget(self.exchange_btn)
        
        # Close button
        close_btn = QPushButton(i18n.get_text('actions.close'))
        close_btn.setFont(QFont("", 11))
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        self.layout.addLayout(button_layout)
        
        # Set dialog size
        self.setFixedSize(400, 300)
        
    def handle_exchange(self):
        """Handle the exchange action."""
        if not self.credits_service or not self.l4l_cookies:
            self.show_error(i18n.get_text('errors.not_logged_in'))
            return
            
        profile_url = self.url_input.text().strip()
        credits = self.credits_input.value()
        
        if not profile_url:
            self.show_error(i18n.get_text('errors.invalid_profile'))
            return
            
        try:
            self.show_notice(i18n.get_text('actions.processing_exchange'))
            self.exchange_btn.setEnabled(False)
            
            success = self.credits_service.exchange_for_followers(
                self.l4l_cookies,
                profile_url,
                credits
            )
            
            if success:
                self.show_success(i18n.get_text('status.exchange_success'))
                # Clear inputs
                self.url_input.clear()
                self.credits_input.setValue(10)
            else:
                self.show_error(i18n.get_text('errors.exchange_failed'))
                
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.exchange_btn.setEnabled(True)