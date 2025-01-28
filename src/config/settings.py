"""Configuration settings for the Like4Book application."""

import os
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class AppConfig:
    """Application configuration settings."""
    debug: bool = False
    storage_path: str = "Penyimpanan"
    i18n_path: str = os.path.join("Penyimpanan", "i18n")
    default_language: str = "en"

@dataclass
class BrowserConfig:
    """Browser configuration settings."""
    no_sandbox: bool = True
    disable_dev_shm: bool = True
    default_wait_timeout: int = 600

@dataclass
class Settings:
    """Global settings container."""
    app: AppConfig
    browser: BrowserConfig
    cookies: Dict[str, Optional[str]]

    @classmethod
    def load(cls) -> 'Settings':
        """Load settings from environment/files."""
        return cls(
            app=AppConfig(
                debug=os.getenv('DEBUG', '').lower() == 'true',
                storage_path=os.getenv('STORAGE_PATH', 'Penyimpanan'),
                i18n_path=os.getenv('I18N_PATH', os.path.join('Penyimpanan', 'i18n')),
                default_language=os.getenv('DEFAULT_LANGUAGE', 'en')
            ),
            browser=BrowserConfig(
                no_sandbox=os.getenv('BROWSER_NO_SANDBOX', '').lower() != 'false',
                disable_dev_shm=os.getenv('BROWSER_DISABLE_DEV_SHM', '').lower() != 'false',
                default_wait_timeout=int(os.getenv('BROWSER_WAIT_TIMEOUT', '600'))
            ),
            cookies={
                "Like4Like": None,
                "Facebook": None
            }
        )

# Global settings instance
settings = Settings.load()