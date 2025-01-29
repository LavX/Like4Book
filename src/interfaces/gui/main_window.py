"""PyQt6-based main window implementation."""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ...i18n.manager import i18n
from ...auth.like4like import Like4LikeAuth
from ...services.credits import CreditsService
from ...services.browser import BrowserService
from ...features.twitter.like import TwitterLikeFeature
from .dialogs import ProfileExchangeDialog, MissionDialog, LanguageDialog, CookieDialog

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize services
        self.like4like_auth = Like4LikeAuth()
        self.credits_service = CreditsService()
        self.browser_service = BrowserService()
        
        # Feature modules
        self.twitter_feature = TwitterLikeFeature()
        
        # Share credits service with features
        self.twitter_feature.credits_service = self.credits_service
        
        # State
        self.l4l_cookies = None
        
        self.setup_ui()
        self.init_auth()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("✨ Like4Like Suite")
        self.setFixedSize(900, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with status info
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("✨ Like4Like Suite")
        title.setFont(QFont("", 24))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Status info - only coins
        self.credits_label = QLabel(f"💰 {i18n.get_text('status.coins')}: 0")
        self.credits_label.setFont(QFont("", 24))
        header_layout.addWidget(self.credits_label)
            
        main_layout.addLayout(header_layout)
        
        # Available Missions Section
        missions_group = QGroupBox("🎯 Available Missions")
        missions_group.setFont(QFont("", 24))
        missions_layout = QVBoxLayout(missions_group)
        missions_layout.setSpacing(10)
        
        # Mission buttons
        fb_mission_btn = QPushButton("👥 Facebook Follow Mission")
        fb_mission_btn.clicked.connect(self.handle_follow_mission)
        fb_mission_btn.setMinimumHeight(50)
        missions_layout.addWidget(fb_mission_btn)
        
        twitter_mission_btn = QPushButton("❤️ Twitter Like Mission")
        twitter_mission_btn.clicked.connect(self.handle_twitter_likes)
        twitter_mission_btn.setMinimumHeight(50)
        missions_layout.addWidget(twitter_mission_btn)
        
        main_layout.addWidget(missions_group)
        
        # Settings Section
        settings_group = QGroupBox("⚙️ Settings")
        settings_group.setFont(QFont("", 24))
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(10)
        
        # Cookie management button
        l4l_cookie_btn = QPushButton("🔑 Like4Like Cookies")
        l4l_cookie_btn.clicked.connect(lambda: self.handle_cookies("like4like"))
        l4l_cookie_btn.setMinimumHeight(40)
        settings_layout.addWidget(l4l_cookie_btn)
        
        # Management buttons
        exchange_btn = QPushButton("💱 Exchange Coins for Followers")
        exchange_btn.clicked.connect(self.handle_profile_exchange)
        exchange_btn.setMinimumHeight(50)
        settings_layout.addWidget(exchange_btn)
        
        delete_btn = QPushButton("🗑️ Delete Connected Links")
        delete_btn.clicked.connect(self.handle_delete_links)
        delete_btn.setMinimumHeight(50)
        settings_layout.addWidget(delete_btn)
        
        main_layout.addWidget(settings_group)
        
        # App Settings Section
        app_settings_layout = QHBoxLayout()
        app_settings_layout.setSpacing(10)
        
        # Language switch button
        lang_btn = QPushButton(f"🌐 {i18n.get_text('menu.switch_language')}")
        lang_btn.clicked.connect(self.handle_language_switch)
        lang_btn.setMinimumHeight(40)
        app_settings_layout.addWidget(lang_btn)
        
        # Exit button
        exit_btn = QPushButton(f"🚪 {i18n.get_text('menu.exit')}")
        exit_btn.clicked.connect(self.close)
        exit_btn.setMinimumHeight(40)
        app_settings_layout.addWidget(exit_btn)
        
        main_layout.addLayout(app_settings_layout)
        
        # Status area
        self.status_area = QLabel()
        self.status_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_area.setFont(QFont("", 24))
        main_layout.addWidget(self.status_area)
        
        # Set up status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds

    def init_auth(self):
        """Initialize authentication."""
        try:
            # Load and validate Like4Like session
            cookies = self.like4like_auth.load_cookies()
            self.l4l_cookies = cookies.get("Like4Like")
            
            # If Like4Like cookies are missing, open cookie dialog
            if not self.l4l_cookies:
                self.handle_cookies("like4like")
            else:
                self.update_status()
                
        except Exception as e:
            self.show_error(str(e))
            # Open Like4Like cookie dialog on error
            self.handle_cookies("like4like")
            
    def update_status(self):
        """Update status display."""
        if self.l4l_cookies:
            try:
                credits = self.credits_service.get_balance(self.l4l_cookies)
                self.credits_label.setText(f"💰 {i18n.get_text('status.coins')}: {credits}")
            except Exception as e:
                self.show_error(str(e))
                
    def show_error(self, message):
        """Display error message."""
        self.status_area.setText(f"❌ Error: {message}")
        
    def show_success(self, message):
        """Display success message."""
        self.status_area.setText(f"✅ {message}")
        
    def show_notice(self, message):
        """Display notice message."""
        self.status_area.setText(f"ℹ️ {message}")
        
    def handle_cookies(self, cookie_type: str):
        """Handle cookie management.
        
        Args:
            cookie_type: Type of cookies to manage ("like4like")
        """
        def save_cookies(cookies: str):
            """Save cookies callback.
            
            Args:
                cookies: Cookie string to save
            """
            stored_cookies = {"Like4Like": cookies}
            self.like4like_auth.save_cookies(stored_cookies)
            self.l4l_cookies = cookies
            self.update_status()
        
        dialog = CookieDialog(
            self,
            cookie_type=cookie_type,
            current_cookies=current_cookies,
            on_save=save_cookies,
            browser_service=self.browser_service,
            auth_service=auth_service
        )
        dialog.exec()
        
    def handle_profile_exchange(self):
        """Handle profile exchange action."""
        if not self.l4l_cookies:
            self.show_error(i18n.get_text('errors.not_logged_in'))
            self.handle_cookies("like4like")
            return
            
        dialog = ProfileExchangeDialog(
            self,
            credits_service=self.credits_service,
            l4l_cookies=self.l4l_cookies
        )
        dialog.exec()
        self.update_status()
        
    def handle_follow_mission(self):
        """Handle follow mission action."""
        if not self.l4l_cookies:
            self.show_error(i18n.get_text('errors.not_logged_in'))
            self.handle_cookies("like4like")
            return
            
        dialog = MissionDialog(
            self,
            mission_type="follow",
            feature=self.twitter_feature,  # Using Twitter method for Facebook follows
            credits_service=self.credits_service,
            l4l_cookies=self.l4l_cookies
        )
        dialog.exec()
        self.update_status()
        
    def handle_delete_links(self):
        """Handle delete links action."""
        if not self.l4l_cookies:
            self.show_error(i18n.get_text('errors.not_logged_in'))
            self.handle_cookies("like4like")
            return
            
        self.show_notice(i18n.get_text('actions.removing_links'))
        # TODO: Implement link deletion
        self.show_success(i18n.get_text('actions.links_removed'))
        
    def handle_twitter_likes(self):
        """Handle Twitter likes action."""
        if not self.l4l_cookies:
            self.show_error(i18n.get_text('errors.not_logged_in'))
            self.handle_cookies("like4like")
            return
            
        dialog = MissionDialog(
            self,
            mission_type="like",
            feature=self.twitter_feature,
            credits_service=self.credits_service,
            l4l_cookies=self.l4l_cookies
        )
        dialog.exec()
        self.update_status()
        
    def handle_language_switch(self):
        """Handle language switch action."""
        dialog = LanguageDialog(self)
        if dialog.exec():
            # Refresh UI with new language
            self.setup_ui()