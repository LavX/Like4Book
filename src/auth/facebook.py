"""Facebook authentication and interaction module."""

import re
import time
import json
from typing import Tuple, Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..core.constants import FACEBOOK_BASE_URL, BROWSER_WAIT_TIMEOUT
from ..core.exceptions import AuthenticationError, BrowserError
from ..config.settings import settings
from ..utils.http import create_session, make_request

class FacebookAuth:
    """Handle Facebook authentication and user operations."""

    def __init__(self):
        """Initialize Facebook authentication handler."""
        self.session = create_session()
        self.user_info = None

    def get_cookies_from_browser(self, driver: uc.Chrome) -> Optional[str]:
        """Get Facebook cookies after manual login.
        
        Args:
            driver: Undetected Chrome driver instance
            
        Returns:
            str: Cookie string if successful, None otherwise
            
        Raises:
            AuthenticationError: If login process fails
        """
        try:
            driver.get(FACEBOOK_BASE_URL)
            
            # Wait for successful login by checking for multiple possible elements
            WebDriverWait(driver, BROWSER_WAIT_TIMEOUT).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[role='feed']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Home']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-pagelet='Stories']"))
                )
            )
            
            # Additional delay to ensure cookies are set
            time.sleep(5)
            
            # Double check we're actually logged in
            cookies = driver.get_cookies()
            if not cookies or "c_user" not in [cookie['name'] for cookie in cookies]:
                raise AuthenticationError("Facebook login not detected")
                
            cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            return cookie_str
            
        except Exception as e:
            raise AuthenticationError(f"Facebook cookie extraction failed: {str(e)}")

    def validate_user(self, cookies: str) -> Tuple[str, str]:
        """Validate Facebook credentials and extract user information.
        
        Args:
            cookies: Facebook cookie string
            
        Returns:
            tuple: (user_name, user_id)
            
        Raises:
            AuthenticationError: If validation fails
        """
        try:
            headers = {
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-fetch-user": "?1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "accept-language": "en-US,en;q=0.9",
                "sec-fetch-dest": "document",
                "Host": "www.facebook.com"
            }
            
            response = make_request(
                method="GET",
                url=f"{FACEBOOK_BASE_URL}/me",
                cookies={"cookie": cookies},
                headers=headers
            )
            
            user_match = re.search(r'{"ACCOUNT_ID":"(\d+)","USER_ID":".*?","NAME":"(.*?)"', response.text)
            if not user_match:
                raise AuthenticationError("Could not extract user information")
                
            name, user_id = user_match.group(2), user_match.group(1)
            
            # Validate extracted info
            if not name or user_id == "0":
                raise AuthenticationError("Invalid user information")
                
            self.user_info = {"name": name, "id": user_id}
            return name, user_id
            
        except Exception as e:
            raise AuthenticationError(f"Facebook validation failed: {str(e)}")

    def follow_user(self, cookies: str, target_id: str) -> bool:
        """Follow a Facebook user/page.
        
        Args:
            cookies: Facebook cookie string
            target_id: ID of user/page to follow
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            AuthenticationError: If following fails
        """
        try:
            # Get required tokens first
            headers = {
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-fetch-user": "?1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "accept-language": "en-US,en;q=0.9",
                "sec-fetch-dest": "document",
                "Host": "www.facebook.com"
            }
            
            response = make_request(
                method="GET",
                url=f"{FACEBOOK_BASE_URL}/{target_id}",
                cookies={"cookie": cookies},
                headers=headers
            )
            
            # Extract required tokens for follow request
            tokens = {
                "lsd": re.search(r'"LSD",\[\],{"token":"(.*?)"', response.text),
                "actor_id": re.search(r'"actorID":"(\d+)"', response.text),
                "haste_session": re.search(r'"haste_session":"(.*?)"', response.text),
                "fb_dtsg": re.search(r'"DTSGInitData",\[\],{"token":"(.*?)",', response.text),
                "jazoest": re.search(r'&jazoest=(\d+)"', response.text),
                "subscribee_id": re.search(r'"userID":"(\d+)",', response.text)
            }
            
            # Verify all tokens were found
            missing_tokens = [k for k, v in tokens.items() if not v]
            if missing_tokens:
                raise AuthenticationError(f"Missing required tokens: {', '.join(missing_tokens)}")
            
            # Extract values from regex matches
            tokens = {k: v.group(1) for k, v in tokens.items()}
            
            # Make follow request
            follow_response = make_request(
                method="POST",
                url=f"{FACEBOOK_BASE_URL}/api/graphql/",
                cookies={"cookie": cookies},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-FB-Friendly-Name": "CometUserFollowMutation",
                    "Origin": FACEBOOK_BASE_URL,
                    "Referer": f"{FACEBOOK_BASE_URL}/{target_id}"
                },
                data={
                    "__a": "1",
                    "fb_dtsg": tokens["fb_dtsg"],
                    "jazoest": tokens["jazoest"],
                    "lsd": tokens["lsd"],
                    "variables": json.dumps({
                        "input": {
                            "subscribee_id": tokens["subscribee_id"],
                            "actor_id": tokens["actor_id"],
                            "client_mutation_id": "1"
                        }
                    })
                }
            )
            
            return '"data":{"actor_subscribe":{"subscribee":' in follow_response.text
            
        except Exception as e:
            raise AuthenticationError(f"Follow operation failed: {str(e)}")