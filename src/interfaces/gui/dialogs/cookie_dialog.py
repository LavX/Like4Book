"""Cookie management dialog implementation."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from selenium.common.exceptions import WebDriverException

from ....i18n.manager import i18n
from .base_dialog import BaseDialog

class BrowserThread(QThread):
    """Thread for browser-based cookie retrieval."""
    
    success = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, browser_service, auth_service, cookie_type):
        """Initialize browser thread.
        
        Args:
            browser_service: Browser service instance
            auth_service: Authentication service instance
            cookie_type: Type of cookies to retrieve
        """
        super().__init__()
        self.browser_service = browser_service
        self.auth_service = auth_service
        self.cookie_type = cookie_type
        
    def run(self):
        """Run browser cookie retrieval."""
        try:
            with self.browser_service as browser:
                try:
                    cookies = self.auth_service.get_cookies_from_browser(browser.driver)
                    if cookies:
                        self.success.emit(cookies)
                    else:
                        self.error.emit(
                            i18n.get_text(f'login.browser_login.cookies_failed.{self.cookie_type}')
                        )
                except WebDriverException:
                    self.error.emit(i18n.get_text('login.browser_login.closed'))
                except Exception as e:
                    self.error.emit(str(e))
        except Exception as e:
            self.error.emit(i18n.get_text('login.browser_login.launch_failed'))

class CookieDialog(BaseDialog):
    """Dialog for managing cookies."""
    
    def __init__(
        self, 
        parent=None, 
        cookie_type="like4like",
        current_cookies=None,
        on_save=None,
        browser_service=None,
        auth_service=None
    ):
        """Initialize cookie dialog.
        
        Args:
            parent: Parent widget
            cookie_type: Type of cookies ("like4like" or "facebook")
            current_cookies: Current cookie string
            on_save: Callback function when cookies are saved
            browser_service: Browser service instance
            auth_service: Authentication service instance
        """
        title = (
            i18n.get_text('interface.l4l_cookies')
            if cookie_type == "like4like" 
            else i18n.get_text('interface.fb_cookies')
        )
        super().__init__(parent, title)
        
        self.cookie_type = cookie_type
        self.current_cookies = current_cookies
        self.on_save = on_save
        self.browser_service = browser_service
        self.auth_service = auth_service
        
        self.browser_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        # Instructions
        instructions = QLabel(i18n.get_text(f'login.{self.cookie_type}_cookies'))
        instructions.setFont(QFont("", 11))
        instructions.setWordWrap(True)
        self.layout.addWidget(instructions)
        
        # Cookie input frame
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(10)
        
        # Cookie text area
        self.cookie_input = QTextEdit()
        self.cookie_input.setPlaceholderText(i18n.get_text('interface.paste_cookies'))
        self.cookie_input.setMinimumWidth(400)
        self.cookie_input.setMinimumHeight(150)
        if self.current_cookies:
            self.cookie_input.setText(self.current_cookies)
            
        input_layout.addWidget(self.cookie_input)
        
        self.layout.addWidget(input_frame)
        
        # Browser retrieval button
        self.browser_btn = QPushButton(i18n.get_text('interface.browser_cookies'))
        self.browser_btn.setFont(QFont("", 11))
        self.browser_btn.clicked.connect(self.handle_browser_retrieval)
        self.layout.addWidget(self.browser_btn)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Save button
        save_btn = QPushButton(i18n.get_text('actions.save'))
        save_btn.setFont(QFont("", 11))
        save_btn.clicked.connect(self.handle_save)
        button_layout.addWidget(save_btn)
        
        # Close button
        close_btn = QPushButton(i18n.get_text('actions.close'))
        close_btn.setFont(QFont("", 11))
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        self.layout.addLayout(button_layout)
        
        # Set dialog size
        self.setFixedSize(500, 450)
        
    def handle_browser_retrieval(self):
        """Handle retrieving cookies through browser."""
        if not self.browser_service or not self.auth_service:
            self.show_error(i18n.get_text('errors.browser_unavailable'))
            return
            
        # Disable browser button while retrieving
        self.browser_btn.setEnabled(False)
        self.show_notice(i18n.get_text(f'login.browser_login.steps.{self.cookie_type}'))
        
        # Initialize and start browser thread
        self.browser_thread = BrowserThread(
            self.browser_service,
            self.auth_service,
            self.cookie_type
        )
        self.browser_thread.success.connect(self.on_browser_success)
        self.browser_thread.error.connect(self.on_browser_error)
        self.browser_thread.finished.connect(self.on_browser_finished)
        self.browser_thread.start()
        
    def on_browser_success(self, cookies):
        """Handle successful cookie retrieval.
        
        Args:
            cookies: Retrieved cookie string
        """
        self.cookie_input.setText(cookies)
        self.show_success(i18n.get_text('login.browser_login.success'))
        
    def on_browser_error(self, error):
        """Handle browser error.
        
        Args:
            error: Error message
        """
        self.show_error(error)
        
    def on_browser_finished(self):
        """Handle browser thread completion."""
        self.browser_btn.setEnabled(True)
        self.browser_thread = None
        
    def handle_save(self):
        """Handle saving cookies."""
        cookies = self.cookie_input.toPlainText().strip()
        if not cookies:
            self.show_error(i18n.get_text('errors.invalid_cookies'))
            return
            
        if self.on_save:
            try:
                self.on_save(cookies)
                self.show_success(i18n.get_text('status.cookies_saved'))
                self.accept()
            except Exception as e:
                self.show_error(str(e))
                
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.browser_thread and self.browser_thread.isRunning():
            self.browser_thread.terminate()
            self.browser_thread.wait()
        super().closeEvent(event)