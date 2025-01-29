"""Like4Like authentication and interaction module."""

import json
import re
import time
from typing import Optional, Dict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

from ..core.constants import (
    LIKE4LIKE_BASE_URL,
    LIKE4LIKE_API,
    SUCCESS_CODES,
    COOKIE_FILE_PATH,
    BROWSER_WAIT_TIMEOUT
)
from ..core.exceptions import AuthenticationError, APIError
from ..utils.http import create_session, make_request

class Like4LikeAuth:
    """Handle Like4Like authentication and platform operations."""

    def __init__(self):
        """Initialize Like4Like authentication handler."""
        self.session = create_session()
        self.credits = "0"
        self._ensure_cookie_file()

    def _ensure_cookie_file(self) -> None:
        """Ensure cookie file exists with default structure."""
        try:
            with open(COOKIE_FILE_PATH, "r") as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(COOKIE_FILE_PATH, "w") as f:
                json.dump({"Like4Like": None}, f, indent=4)

    def get_cookies_from_browser(self, driver: uc.Chrome) -> Optional[str]:
        """Get Like4Like cookies after manual login.
        
        Args:
            driver: Undetected Chrome driver instance
            
        Returns:
            str: Cookie string if successful, None otherwise
            
        Raises:
            AuthenticationError: If login process fails
        """
        try:
            driver.get(f"{LIKE4LIKE_BASE_URL}/login/")
            
            # Wait for successful login by checking for any earn feature page
            WebDriverWait(driver, BROWSER_WAIT_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='earn-']"))
            )
            
            # Additional delay to ensure cookies are set
            time.sleep(2)
            
            cookies = driver.get_cookies()
            if not cookies:
                raise AuthenticationError("No cookies found after login")
                
            cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            return cookie_str
            
        except Exception as e:
            raise AuthenticationError(f"Like4Like cookie extraction failed: {str(e)}")

    def validate_cookies(self, cookies: str) -> bool:
        """Validate Like4Like cookies.
        
        Args:
            cookies: Like4Like cookie string
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            response = make_request(
                method="GET",
                url=f"{LIKE4LIKE_BASE_URL}{LIKE4LIKE_API['USER_INFO']}",
                cookies={"Cookie": cookies},
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            
            return all(code in response.text for code in SUCCESS_CODES.values())
        except Exception:
            return False

    def get_credits(self, cookies: str) -> str:
        """Get current credit balance.
        
        Args:
            cookies: Like4Like cookie string
            
        Returns:
            str: Credit balance
            
        Raises:
            AuthenticationError: If credit fetch fails
        """
        try:
            response = make_request(
                method="GET",
                url=f"{LIKE4LIKE_BASE_URL}{LIKE4LIKE_API['USER_INFO']}",
                cookies={"Cookie": cookies},
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            
            if SUCCESS_CODES['LIKE4LIKE_SUCCESS'] in response.text and SUCCESS_CODES['LIKE4LIKE_CREDITS'] in response.text:
                data = json.loads(response.text)
                self.credits = data["data"]["credits"]
                return self.credits
            else:
                raise AuthenticationError("Failed to fetch credits")
                
        except Exception as e:
            raise AuthenticationError(f"Credit check failed: {str(e)}")

    def save_cookies(self, cookies: Dict[str, str]) -> None:
        """Save cookies to storage.
        
        Args:
            cookies: Dictionary of cookies to save
            
        Raises:
            APIError: If save operation fails
        """
        try:
            with open(COOKIE_FILE_PATH, "w") as f:
                json.dump(cookies, f, indent=4, sort_keys=True)
        except Exception as e:
            raise APIError(f"Failed to save cookies: {str(e)}")

    def load_cookies(self) -> Dict[str, str]:
        """Load cookies from storage.
        
        Returns:
            dict: Loaded cookies
            
        Raises:
            APIError: If load operation fails
        """
        try:
            with open(COOKIE_FILE_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            raise APIError(f"Failed to load cookies: {str(e)}")

    def get_available_tasks(self, cookies: str, feature: str) -> Optional[Dict[str, Any]]:
        """Get available tasks for a feature.
        
        Args:
            cookies: Like4Like cookie string
            feature: Feature type to get tasks for
            
        Returns:
            dict: Task data if available, None if no tasks
            
        Raises:
            APIError: If task fetch fails
        """
        try:
            response = make_request(
                method="GET",
                url=f"{LIKE4LIKE_BASE_URL}{LIKE4LIKE_API['GET_TASKS']}?feature={feature}",
                cookies={"Cookie": cookies},
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            
            if SUCCESS_CODES['LIKE4LIKE_SUCCESS'] not in response.text:
                return None
                
            data = json.loads(response.text)
            return data.get("data", {}).get("tasks")
            
        except Exception as e:
            raise APIError(f"Failed to fetch tasks: {str(e)}")

    def validate_task(self, cookies: str, task_data: Dict[str, Any]) -> bool:
        """Validate a completed task.
        
        Args:
            cookies: Like4Like cookie string
            task_data: Task validation data
            
        Returns:
            bool: True if validated successfully
            
        Raises:
            APIError: If validation fails
        """
        try:
            response = make_request(
                method="POST",
                url=f"{LIKE4LIKE_BASE_URL}{LIKE4LIKE_API['VALIDATE_TASK']}",
                cookies={"Cookie": cookies},
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data=task_data
            )
            
            success = all(code in response.text for code in SUCCESS_CODES.values())
            if success:
                # Update credits from response
                credits_match = re.search(r'"credits":"(.*?)"', response.text)
                if credits_match:
                    self.credits = credits_match.group(1)
                    
            return success
            
        except Exception as e:
            raise APIError(f"Task validation failed: {str(e)}")

    def exchange_credits(self, cookies: str, feature: str, target_data: Dict[str, Any]) -> bool:
        """Exchange credits for a service.
        
        Args:
            cookies: Like4Like cookie string
            feature: Feature type to exchange for
            target_data: Exchange target data
            
        Returns:
            bool: True if exchange successful
            
        Raises:
            APIError: If exchange fails
        """
        try:
            response = make_request(
                method="POST",
                url=f"{LIKE4LIKE_BASE_URL}{LIKE4LIKE_API['ENTER_LINK']}",
                cookies={"Cookie": cookies},
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "feature": feature,
                    **target_data
                }
            )
            
            return '"uradio":"1"' in response.text
            
        except Exception as e:
            raise APIError(f"Credit exchange failed: {str(e)}")