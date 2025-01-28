"""Mission execution dialog implementation."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QSpinBox, 
    QPushButton, QLabel, QProgressBar, QFrame,
    QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

from ....i18n.manager import i18n
from .base_dialog import BaseDialog

class MissionThread(QThread):
    """Thread for executing missions."""
    
    success = pyqtSignal()
    error = pyqtSignal(str)
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, feature, mission_type, l4l_cookies, fb_cookies=None):
        """Initialize mission thread."""
        super().__init__()
        self.feature = feature
        self.mission_type = mission_type
        self.l4l_cookies = l4l_cookies
        self.fb_cookies = fb_cookies
        self.running = False
        
    def run(self):
        """Run mission execution."""
        self.running = True
        while self.running:
            try:
                if self.mission_type == "follow":
                    success = self.feature.execute_follow_cycle(
                        self.l4l_cookies,
                        self.fb_cookies
                    )
                else:
                    success = self.feature.execute_like_cycle(self.l4l_cookies)
                    
                if success:
                    self.success.emit()
                    
                # Get latest stats
                stats = self.feature.credits_service.get_statistics()
                self.stats_updated.emit(stats)
                
                # Sleep for delay
                self.msleep(self.delay)
                
            except Exception as e:
                self.error.emit(str(e))
                break
                
    def stop(self):
        """Stop mission execution."""
        self.running = False
        
    def set_delay(self, seconds):
        """Set delay between cycles."""
        self.delay = seconds * 1000  # Convert to milliseconds

class MissionDialog(BaseDialog):
    """Dialog for running follow/like missions."""
    
    def __init__(
        self, 
        parent=None, 
        mission_type="follow",
        feature=None,
        credits_service=None,
        l4l_cookies=None,
        fb_cookies=None
    ):
        title = (
            i18n.get_text('menu.follow_mission') 
            if mission_type == "follow" 
            else i18n.get_text('menu.twitter_likes')
        )
        super().__init__(parent, title)
        
        self.mission_type = mission_type
        self.feature = feature
        self.credits_service = credits_service
        self.l4l_cookies = l4l_cookies
        self.fb_cookies = fb_cookies
        
        self.success_count = 0
        self.fail_count = 0
        
        self.setup_ui()
        
        # Initialize mission thread
        self.mission_thread = MissionThread(
            feature,
            mission_type,
            l4l_cookies,
            fb_cookies
        )
        self.mission_thread.success.connect(self.on_mission_success)
        self.mission_thread.error.connect(self.show_error)
        self.mission_thread.stats_updated.connect(self.update_stats)
        
    def setup_ui(self):
        """Set up the dialog UI."""
        # Header with back button and title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 8, 8, 8)
        
        back_btn = QPushButton("←")
        back_btn.setFixedSize(30, 30)
        back_btn.clicked.connect(self.close)
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
            }
        """)
        header_layout.addWidget(back_btn)
        
        dialog_title = (
            i18n.get_text('dialog.facebook_mission_title') 
            if self.mission_type == "follow" 
            else i18n.get_text('dialog.twitter_mission_title')
        )
        title = QLabel(dialog_title)
        title.setStyleSheet("font-size: 14px; margin: 4px 0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
            }
        """)
        header_layout.addWidget(close_btn)
        
        self.layout.addLayout(header_layout)
        
        # Main content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(16, 16, 16, 16)
        
        # Mission type specific header
        mission_header = QLabel(
            i18n.get_text('menu.follow_mission') if self.mission_type == "follow" 
            else i18n.get_text('menu.twitter_likes')
        )
        mission_header.setStyleSheet("font-size: 14px;")
        mission_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(mission_header)
        
        # Delay settings
        delay_layout = QVBoxLayout()
        delay_layout.setSpacing(8)
        
        delay_label = QLabel(i18n.get_text('status.delay_between_actions'))
        delay_label.setStyleSheet("font-size: 14px;")
        delay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        delay_layout.addWidget(delay_label)
        
        self.delay_input = QSpinBox()
        self.delay_input.setMinimum(10)
        self.delay_input.setMaximum(300)
        self.delay_input.setValue(60)
        self.delay_input.setSuffix(" " + i18n.get_text('status.seconds'))
        self.delay_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.delay_input.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: none;
                border-radius: 4px;
                min-width: 200px;
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
                font-size: 14px;
            }
        """)
        delay_layout.addWidget(self.delay_input, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addLayout(delay_layout)
        
        # Progress section
        progress_label = QLabel(i18n.get_text('status.progress'))
        progress_label.setStyleSheet("font-size: 14px;")
        progress_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #1e88e5;
                border-radius: 4px;
            }
        """)
        content_layout.addWidget(self.progress_bar)
        
        # Stats layout with material design
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(16)
        
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(24)
        
        # Success count
        success_layout = QVBoxLayout()
        success_label = QLabel(i18n.get_text('status.success'))
        success_label.setStyleSheet("font-size: 14px; margin-bottom: 4px;")
        success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_label = QLabel("0")
        self.success_label.setStyleSheet("font-size: 14px;")
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_layout.addWidget(success_label)
        success_layout.addWidget(self.success_label)
        stats_grid.addLayout(success_layout)
        
        # Failed count
        failed_layout = QVBoxLayout()
        failed_label = QLabel(i18n.get_text('status.failed'))
        failed_label.setStyleSheet("font-size: 14px; margin-bottom: 4px;")
        failed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fail_label = QLabel("0")
        self.fail_label.setStyleSheet("font-size: 14px;")
        self.fail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        failed_layout.addWidget(failed_label)
        failed_layout.addWidget(self.fail_label)
        stats_grid.addLayout(failed_layout)
        
        # Coins count
        coins_layout = QVBoxLayout()
        coins_label = QLabel(i18n.get_text('status.coins'))
        coins_label.setStyleSheet("font-size: 14px; margin-bottom: 4px;")
        coins_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.credits_label = QLabel("0")
        self.credits_label.setStyleSheet("font-size: 14px;")
        self.credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coins_layout.addWidget(coins_label)
        coins_layout.addWidget(self.credits_label)
        stats_grid.addLayout(coins_layout)
        
        stats_layout.addLayout(stats_grid)
        content_layout.addLayout(stats_layout)
        
        content_layout.addStretch()
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Start button
        self.start_btn = QPushButton(i18n.get_text('actions.start'))
        self.start_btn.clicked.connect(self.toggle_mission)
        button_layout.addWidget(self.start_btn)
        
        # Close button
        self.close_btn = QPushButton(i18n.get_text('actions.close'))
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
            }
        """)
        button_layout.addWidget(self.close_btn)
        
        content_layout.addLayout(button_layout)
        
        self.layout.addLayout(content_layout)
        
        # Set dialog size and style
        self.setFixedSize(400, 500)
            
    def toggle_mission(self):
        """Toggle mission execution."""
        if not self.mission_thread.running:
            self.start_mission()
        else:
            self.stop_mission()
            
    def start_mission(self):
        """Start mission execution."""
        if not self.feature or not self.l4l_cookies:
            self.show_error(i18n.get_text('errors.not_logged_in'))
            return
            
        # Set delay and start thread
        self.mission_thread.set_delay(self.delay_input.value())
        self.mission_thread.start()
        
        self.start_btn.setText(i18n.get_text('actions.stop'))
        self.delay_input.setEnabled(False)
        self.show_notice(i18n.get_text('actions.running_mission'))
        
    def stop_mission(self):
        """Stop mission execution."""
        self.mission_thread.stop()
        self.start_btn.setText(i18n.get_text('actions.start'))
        self.delay_input.setEnabled(True)
        self.show_notice(i18n.get_text('actions.mission_stopped'))
        
    def on_mission_success(self):
        """Handle successful mission cycle."""
        self.success_count += 1
        self.update_progress()
        
    def update_stats(self, stats):
        """Update statistics display."""
        self.success_count = int(stats.get('success_count', 0))
        self.fail_count = int(stats.get('failed_count', 0))
        
        self.success_label.setText(str(self.success_count))
        self.fail_label.setText(str(self.fail_count))
        
        try:
            credits = self.credits_service.get_balance(self.l4l_cookies)
            self.credits_label.setText(str(credits))
        except Exception:
            pass
            
        self.update_progress()
        
    def update_progress(self):
        """Update progress bar."""
        total = self.success_count + self.fail_count
        if total > 0:
            progress = (self.success_count / total) * 100
            self.progress_bar.setValue(int(progress))
            
    def closeEvent(self, event):
        """Handle dialog close event."""
        self.stop_mission()
        super().closeEvent(event)