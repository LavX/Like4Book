"""Browser service for managing browser instances and operations."""

from typing import Optional
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..core.exceptions import BrowserError
from ..config.settings import settings

class BrowserService:
    """Service for managing browser operations."""

    def __init__(self):
        """Initialize browser service."""
        self.driver: Optional[uc.Chrome] = None
        self.config = settings.browser

    def launch_browser(self) -> uc.Chrome:
        """Launch and configure undetected-chromedriver browser.
        
        Returns:
            uc.Chrome: Configured browser instance
            
        Raises:
            BrowserError: If browser launch fails
        """
        try:
            options = uc.ChromeOptions()
            
            # Apply configuration
            if self.config.no_sandbox:
                options.add_argument('--no-sandbox')
            if self.config.disable_dev_shm:
                options.add_argument('--disable-dev-shm-usage')
                
            # Additional security and performance options
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-notifications')
            
            # Create driver instance
            self.driver = uc.Chrome(options=options)
            return self.driver
            
        except Exception as e:
            raise BrowserError(f"Failed to launch browser: {str(e)}")

    def wait_for_element(self, locator: tuple, timeout: Optional[int] = None) -> bool:
        """Wait for element to be present.
        
        Args:
            locator: Selenium locator tuple (By.XX, "value")
            timeout: Optional custom timeout in seconds
            
        Returns:
            bool: True if element found within timeout
            
        Raises:
            BrowserError: If driver not initialized
        """
        if not self.driver:
            raise BrowserError("Browser not initialized")
            
        try:
            timeout = timeout or self.config.default_wait_timeout
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False
        except Exception as e:
            raise BrowserError(f"Wait operation failed: {str(e)}")

    def wait_for_any_element(self, locators: list[tuple], timeout: Optional[int] = None) -> bool:
        """Wait for any of the specified elements to be present.
        
        Args:
            locators: List of Selenium locator tuples
            timeout: Optional custom timeout in seconds
            
        Returns:
            bool: True if any element found within timeout
            
        Raises:
            BrowserError: If driver not initialized
        """
        if not self.driver:
            raise BrowserError("Browser not initialized")
            
        try:
            timeout = timeout or self.config.default_wait_timeout
            wait = WebDriverWait(self.driver, timeout)
            
            conditions = [EC.presence_of_element_located(locator) for locator in locators]
            wait.until(EC.any_of(*conditions))
            return True
            
        except TimeoutException:
            return False
        except Exception as e:
            raise BrowserError(f"Wait operation failed: {str(e)}")

    def get_cookies(self) -> list[dict]:
        """Get all cookies from current session.
        
        Returns:
            list: List of cookie dictionaries
            
        Raises:
            BrowserError: If driver not initialized
        """
        if not self.driver:
            raise BrowserError("Browser not initialized")
            
        try:
            return self.driver.get_cookies()
        except Exception as e:
            raise BrowserError(f"Failed to get cookies: {str(e)}")

    def quit(self) -> None:
        """Safely close browser instance."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            raise BrowserError(f"Failed to quit browser: {str(e)}")

    def __enter__(self) -> 'BrowserService':
        """Context manager entry.
        
        Returns:
            BrowserService: Self for context management
        """
        self.launch_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit.
        
        Ensures browser is properly closed.
        """
        self.quit()