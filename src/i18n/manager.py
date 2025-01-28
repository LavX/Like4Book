"""Internationalization manager for handling translations."""

import json
import os
from typing import Dict, Any, Optional

class I18nManager:
    """Handle application translations and language switching."""
    
    def __init__(self):
        """Initialize the i18n manager."""
        self.current_lang = 'en'  # Default language is English
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.lang_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'language.json')
        self._load_translations()
        self._load_language_preference()
    
    def _load_translations(self) -> None:
        """Load all available language files."""
        i18n_dir = os.path.dirname(os.path.abspath(__file__))
        for lang_file in ['en.json', 'id.json']:
            lang_code = lang_file.split('.')[0]
            file_path = os.path.join(i18n_dir, lang_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading {lang_file}: {str(e)}")

    def get_text(self, key_path: str) -> str:
        """
        Get translated text using dot notation.
        
        Args:
            key_path: Path to translation key (e.g., 'login.like4like_cookies')
            
        Returns:
            str: Translated text, falling back to English if not found
        """
        # Try current language first
        try:
            current_dict = self.translations[self.current_lang]
            for key in key_path.split('.'):
                current_dict = current_dict[key]
            return current_dict
        except (KeyError, TypeError):
            # If not found and current language is not English, try English
            if self.current_lang != 'en':
                try:
                    current_dict = self.translations['en']
                    for key in key_path.split('.'):
                        current_dict = current_dict[key]
                    return current_dict
                except (KeyError, TypeError):
                    pass
            return f"Missing translation: {key_path}"

    def switch_language(self) -> str:
        """
        Switch between available languages.
        
        Returns:
            str: New language code
        """
        self.current_lang = 'en' if self.current_lang == 'id' else 'id'
        return self.current_lang

    def get_current_language(self) -> str:
        """
        Get current language code.
        
        Returns:
            str: Current language code
        """
        return self.current_lang

    def get_available_languages(self) -> Dict[str, str]:
        """
        Get available languages and their display names.
        
        Returns:
            dict: Language codes and their display names
        """
        return {
            'en': 'English',
            'id': 'Indonesian (Bahasa Indonesia)'
        }

    def _load_language_preference(self) -> None:
        """Load saved language preference."""
        try:
            if os.path.exists(self.lang_file):
                with open(self.lang_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_lang = data.get('language', 'en')
        except Exception:
            self.current_lang = 'en'  # Default to English on error

    def save_language_preference(self) -> None:
        """Save current language preference."""
        try:
            with open(self.lang_file, 'w', encoding='utf-8') as f:
                json.dump({'language': self.current_lang}, f)
        except Exception:
            pass  # Silently fail if we can't save the preference

# Create a singleton instance
i18n = I18nManager()