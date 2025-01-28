"""Facebook follow feature implementation."""

import json
import time
from typing import Optional, Dict, Tuple

from ...core.constants import LIKE4LIKE_BASE_URL, SUCCESS_CODES, FEATURE_TYPES
from ...core.exceptions import FeatureError
from ...services.credits import CreditsService
from ...auth.facebook import FacebookAuth
from ...utils.http import create_session, make_request

class FacebookFollowFeature:
    """Handle Facebook follow operations through Like4Like."""

    def __init__(self):
        """Initialize Facebook follow feature."""
        self.session = create_session()
        self.credits_service = CreditsService()
        self.facebook_auth = FacebookAuth()
        self.current_task = None

    def get_follow_task(self, cookies: str, feature: str = FEATURE_TYPES['FACEBOOK_USER_SUB']) -> Optional[Dict]:
        """Get a Facebook follow task from Like4Like.
        
        Args:
            cookies: Like4Like cookie string
            feature: Feature type (user/page follow)
            
        Returns:
            dict: Task data if available, None if no tasks
            
        Raises:
            FeatureError: If task fetch fails
        """
        try:
            # Set up initial headers
            self.session.headers.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Sec-Fetch-Mode": "navigate",
                "Upgrade-Insecure-Requests": "1",
                "Host": "www.like4like.org",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1"
            })

            # Get initial page
            response = make_request(
                method="GET",
                url=f"{LIKE4LIKE_BASE_URL}/user/earn-facebook-subscribes.php",
                session=self.session,
                cookies={"Cookie": cookies}
            )

            # Update headers for task request
            self.session.headers.update({
                "Referer": f"{LIKE4LIKE_BASE_URL}/user/earn-facebook-subscribes.php",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors"
            })

            # Get task
            response = make_request(
                method="GET",
                url=f"{LIKE4LIKE_BASE_URL}/api/get-tasks.php?feature={feature}",
                session=self.session,
                cookies={"Cookie": cookies}
            )

            if SUCCESS_CODES['LIKE4LIKE_SUCCESS'] in response.text and "www.facebook.com" in response.text:
                tasks = json.loads(response.text)["data"]["tasks"]
                self.current_task = tasks[0] if tasks else None
                return self.current_task
            elif "tasks" not in response.text:
                raise FeatureError("Bot detection triggered")
            else:
                return None

        except Exception as e:
            raise FeatureError(f"Failed to get Facebook follow task: {str(e)}")

    def start_task(self, cookies: str, task: Dict) -> bool:
        """Start a Facebook follow task.
        
        Args:
            cookies: Like4Like cookie string
            task: Task data
            
        Returns:
            bool: True if task started successfully
            
        Raises:
            FeatureError: If task start fails
        """
        try:
            self.session.headers.update({
                "Content-Type": "application/json; charset=utf-8"
            })
            
            response = make_request(
                method="GET",
                url=f"{LIKE4LIKE_BASE_URL}/api/start-task.php",
                session=self.session,
                cookies={"Cookie": cookies},
                params={
                    "idzad": task["idlink"],
                    "vrsta": "subscribe",
                    "idcod": task["taskId"],
                    "feature": "facebooksub"
                }
            )
            
            if SUCCESS_CODES['LIKE4LIKE_SUCCESS'] in response.text:
                return self.verify_follow_url(cookies, task["idlink"])
            return False
            
        except Exception as e:
            raise FeatureError(f"Failed to start task: {str(e)}")

    def verify_follow_url(self, cookies: str, target_id: str) -> bool:
        """Verify Facebook follow URL is valid.
        
        Args:
            cookies: Like4Like cookie string
            target_id: Facebook profile/page ID
            
        Returns:
            bool: True if URL is valid
            
        Raises:
            FeatureError: If verification fails
        """
        try:
            data = {
                "url": f"https://www.facebook.com/{target_id}"
            }
            
            response = make_request(
                method="POST",
                url=f"{LIKE4LIKE_BASE_URL}/checkurl.php",
                session=self.session,
                cookies={"Cookie": cookies},
                data=data
            )
            
            return "https://www.facebook.com/" in response.text
            
        except Exception as e:
            raise FeatureError(f"URL verification failed: {str(e)}")

    def execute_follow(self, fb_cookies: str, target_id: str) -> bool:
        """Execute Facebook follow action.
        
        Args:
            fb_cookies: Facebook cookie string
            target_id: Profile/page to follow
            
        Returns:
            bool: True if follow successful
            
        Raises:
            FeatureError: If follow action fails
        """
        try:
            success = self.facebook_auth.follow_user(fb_cookies, target_id)
            time.sleep(5.5)  # Wait for follow to register
            return success
            
        except Exception as e:
            raise FeatureError(f"Follow action failed: {str(e)}")

    def validate_task(self, cookies: str, task: Dict) -> bool:
        """Validate a completed Facebook follow task.
        
        Args:
            cookies: Like4Like cookie string
            task: Task data
            
        Returns:
            bool: True if validation successful
            
        Raises:
            FeatureError: If validation fails
        """
        try:
            self.session.headers.update({
                "Referer": f"{LIKE4LIKE_BASE_URL}/user/earn-facebook-subscribes.php",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": f"{LIKE4LIKE_BASE_URL}"
            })
            
            data = {
                "url": f"https://www.facebook.com/{task['idlink']}",
                "idlinka": task["idlink"],
                "idzad": task["taskId"],
                "addon": "false",
                "version": "",
                "idclana": task["code3"],
                "cnt": "true",
                "vrsta": "subscribe",
                "feature": "facebooksub"
            }
            
            response = make_request(
                method="POST",
                url=f"{LIKE4LIKE_BASE_URL}/api/validate-task.php",
                session=self.session,
                cookies={"Cookie": cookies},
                data=data
            )
            
            success = all(code in response.text for code in SUCCESS_CODES.values())
            
            if success:
                self.credits_service.record_success()
            else:
                self.credits_service.record_failure()
                
            return success
            
        except Exception as e:
            self.credits_service.record_failure()
            raise FeatureError(f"Task validation failed: {str(e)}")

    def execute_follow_cycle(self, l4l_cookies: str, fb_cookies: str) -> bool:
        """Execute a complete Facebook follow cycle.
        
        Args:
            l4l_cookies: Like4Like cookie string
            fb_cookies: Facebook cookie string
            
        Returns:
            bool: True if cycle completed successfully
            
        Raises:
            FeatureError: If cycle fails
        """
        try:
            # Get task
            task = self.get_follow_task(l4l_cookies)
            if not task:
                return False
                
            # Start task
            if not self.start_task(l4l_cookies, task):
                return False
                
            # Execute follow
            if not self.execute_follow(fb_cookies, task["idlink"]):
                return False
                
            # Validate task
            return self.validate_task(l4l_cookies, task)
            
        except Exception as e:
            raise FeatureError(f"Follow cycle failed: {str(e)}")