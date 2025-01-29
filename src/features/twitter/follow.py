"""Twitter follow feature implementation."""

import json
import time
import datetime
from typing import Optional, Dict

from ...core.constants import LIKE4LIKE_BASE_URL, SUCCESS_CODES, FEATURE_TYPES
from ...core.exceptions import FeatureError
from ...services.credits import CreditsService
from ...utils.http import create_session, make_request

class TwitterFollowFeature:
    """Handle Twitter follow operations through Like4Like."""

    def __init__(self):
        """Initialize Twitter follow feature."""
        self.session = create_session()
        self.credits_service = CreditsService()

    def get_follow_task(self, cookies: str) -> Optional[Dict]:
        """Get a Twitter follow task from Like4Like.
        
        Args:
            cookies: Like4Like cookie string
            
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
                url=f"{LIKE4LIKE_BASE_URL}/user/earn-twitter.php",
                session=self.session,
                cookies={"Cookie": cookies}
            )

            # Update headers for task request
            self.session.headers.update({
                "Referer": f"{LIKE4LIKE_BASE_URL}/user/earn-twitter.php",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors"
            })

            # Get task
            response = make_request(
                method="GET",
                url=f"{LIKE4LIKE_BASE_URL}/api/get-tasks.php?feature={FEATURE_TYPES['TWITTER_FOLLOW']}",
                session=self.session,
                cookies={"Cookie": cookies}
            )

            if SUCCESS_CODES['LIKE4LIKE_SUCCESS'] in response.text and "twitter.com" in response.text:
                tasks = json.loads(response.text)["data"]["tasks"]
                return tasks[0] if tasks else None
            elif "tasks" not in response.text:
                raise FeatureError("Bot detection triggered")
            else:
                return None

        except Exception as e:
            raise FeatureError(f"Failed to get Twitter follow task: {str(e)}")

    def start_task(self, cookies: str, task: Dict) -> bool:
        """Start a Twitter follow task.
        
        Args:
            cookies: Like4Like cookie string
            task: Task data
            
        Returns:
            bool: True if task started successfully
            
        Raises:
            FeatureError: If task start fails
        """
        try:
            timestamp = str(datetime.datetime.now().timestamp() * 1000).split(".")[0]
            
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
                    "vrsta": "follow",
                    "idcod": task["taskId"],
                    "feature": FEATURE_TYPES['TWITTER_FOLLOW'],
                    "_": timestamp
                }
            )
            
            return SUCCESS_CODES['LIKE4LIKE_SUCCESS'] in response.text
            
        except Exception as e:
            raise FeatureError(f"Failed to start task: {str(e)}")

    def validate_task(self, cookies: str, task: Dict) -> bool:
        """Validate a completed Twitter follow task.
        
        Args:
            cookies: Like4Like cookie string
            task: Task data
            
        Returns:
            bool: True if validation successful
            
        Raises:
            FeatureError: If validation fails
        """
        try:
            # Wait for follow action to register
            time.sleep(5)
            
            self.session.headers.update({
                "Referer": f"{LIKE4LIKE_BASE_URL}/user/earn-twitter.php",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": f"{LIKE4LIKE_BASE_URL}"
            })
            
            data = {
                "url": f"https://twitter.com/intent/follow?screen_name={task['idlink']}",
                "idlinka": task["idlink"],
                "idzad": task["taskId"],
                "addon": "false",
                "version": "",
                "idclana": task["code3"],
                "cnt": "true",
                "vrsta": "follow",
                "feature": FEATURE_TYPES['TWITTER_FOLLOW']
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

    def execute_follow_cycle(self, cookies: str) -> bool:
        """Execute a complete Twitter follow cycle.
        
        Args:
            cookies: Like4Like cookie string
            
        Returns:
            bool: True if cycle completed successfully
            
        Raises:
            FeatureError: If cycle fails
        """
        try:
            # Get task
            task = self.get_follow_task(cookies)
            if not task:
                return False
                
            # Start task
            if not self.start_task(cookies, task):
                return False
                
            # Validate task
            return self.validate_task(cookies, task)
            
        except Exception as e:
            raise FeatureError(f"Follow cycle failed: {str(e)}")