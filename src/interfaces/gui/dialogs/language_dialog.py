"""Language selection dialog implementation."""

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ....i18n.manager import i18n
from .base_dialog import BaseDialog

class LanguageDialog(BaseDialog):
    """Dialog for selecting application language."""
    
    def __init__(self, parent=None):
        """Initialize language selection dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, i18n.get_text('menu.language.select'))
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        # Language selection frame
        lang_frame = QFrame()
        lang_layout = QVBoxLayout(lang_frame)
        lang_layout.setSpacing(10)
        
        # English button
        self.en_btn = QPushButton(i18n.get_text('menu.language.english'))
        self.en_btn.setFont(QFont("", 11))
        self.en_btn.setMinimumHeight(40)
        self.en_btn.clicked.connect(lambda: self.select_language("en"))
        lang_layout.addWidget(self.en_btn)
        
        # Indonesian button
        self.id_btn = QPushButton(i18n.get_text('menu.language.indonesian'))
        self.id_btn.setFont(QFont("", 11))
        self.id_btn.setMinimumHeight(40)
        self.id_btn.clicked.connect(lambda: self.select_language("id"))
        lang_layout.addWidget(self.id_btn)
        
        self.layout.addWidget(lang_frame)
        
        # Set dialog size
        self.setFixedSize(300, 200)
        
    def select_language(self, lang_code: str):
        """Handle language selection.
        
        Args:
            lang_code: Language code to switch to
        """
        try:
            i18n.current_lang = lang_code
            i18n.save_language_preference()
            self.show_success(i18n.get_text('status.language_changed'))
            self.accept()  # Close dialog with success
            
        except Exception as e:
            self.show_error(str(e))