"""CLI menu system and command handling."""

import sys
import time
from typing import Tuple, Optional

from ...core.exceptions import AuthenticationError, FeatureError
from ...auth.facebook import FacebookAuth
from ...auth.like4like import Like4LikeAuth
from ...services.credits import CreditsService
from ...services.browser import BrowserService
from ...features.facebook.follow import FacebookFollowFeature
from ...features.twitter.like import TwitterLikeFeature
from ...i18n.manager import i18n
from .display import DisplayManager

class MenuManager:
    """Manage CLI menu system and user interactions."""

    def __init__(self):
        """Initialize menu manager with required services."""
        self.display = DisplayManager()
        self.facebook_auth = FacebookAuth()
        self.like4like_auth = Like4LikeAuth()
        self.credits_service = CreditsService()
        self.browser_service = BrowserService()
        
        # Feature modules
        self.facebook_feature = FacebookFollowFeature()
        self.twitter_feature = TwitterLikeFeature()
        
        # Share credits service with features
        self.facebook_feature.credits_service = self.credits_service
        self.twitter_feature.credits_service = self.credits_service
        
        # State
        self.fb_cookies = None
        self.l4l_cookies = None
        self.user_info = None

    def ensure_like4like_login(self) -> str:
        """Ensure Like4Like login is available.
        
        Returns:
            str: Like4Like cookie string
            
        Raises:
            AuthenticationError: If login fails
        """
        if not self.l4l_cookies or not self.like4like_auth.validate_cookies(self.l4l_cookies):
            self.display.show_notice(i18n.get_text('login.browser_login.steps.like4like'))
            
            with self.browser_service as browser:
                self.l4l_cookies = self.like4like_auth.get_cookies_from_browser(browser.driver)
                
            if not self.l4l_cookies:
                raise AuthenticationError("Like4Like login failed")
            
            # Save the new cookies
            cookies = self.like4like_auth.load_cookies()
            cookies["Like4Like"] = self.l4l_cookies
            self.like4like_auth.save_cookies(cookies)
            
        return self.l4l_cookies

    def ensure_facebook_login(self) -> str:
        """Ensure Facebook login is available.
        
        Returns:
            str: Facebook cookie string
            
        Raises:
            AuthenticationError: If login fails
        """
        if not self.fb_cookies:
            self.display.show_notice(i18n.get_text('login.browser_login.steps.facebook'))
            
            with self.browser_service as browser:
                self.fb_cookies = self.facebook_auth.get_cookies_from_browser(browser.driver)
                
            if not self.fb_cookies:
                raise AuthenticationError("Facebook login failed")
                
            # Validate and get user info
            name, user_id = self.facebook_auth.validate_user(self.fb_cookies)
            self.user_info = {"name": name, "id": user_id}
            
            # Update stored cookies
            cookies = self.like4like_auth.load_cookies()
            cookies["Facebook"] = self.fb_cookies
            self.like4like_auth.save_cookies(cookies)
            
            # Show connection status
            self.display.show_status(self.credits_service.total_credits, name, user_id)
            time.sleep(2.5)
            
        return self.fb_cookies

    def handle_profile_exchange(self) -> None:
        """Handle profile exchange feature."""
        self.ensure_facebook_login()
        
        fblink = self.display.prompt("")
        self.display.show_notice(i18n.get_text('actions.enter_credits'))
        
        try:
            credits = int(self.display.prompt(""))
            self.display.show_notice(i18n.get_text('actions.processing_exchange'))
            
            if self.credits_service.exchange_for_followers(
                self.l4l_cookies,
                fblink,
                credits
            ):
                self.display.show_success(i18n.get_text('status.exchange_success'))
            else:
                self.display.show_error(i18n.get_text('errors.exchange_failed'))
                
        except ValueError:
            self.display.show_error(i18n.get_text('errors.invalid_credits'))
        except Exception as e:
            self.display.show_error(str(e))

    def handle_follow_mission(self) -> None:
        """Handle follow mission feature."""
        self.ensure_facebook_login()
        
        self.display.show_notice(i18n.get_text('actions.enter_delay'))
        try:
            delay = int(self.display.prompt(""))
            self.display.show_notice(i18n.get_text('actions.running_mission'))
            
            while True:
                try:
                    success = self.facebook_feature.execute_follow_cycle(
                        self.l4l_cookies,
                        self.fb_cookies
                    )
                    
                    # Update credits display
                    credits = self.credits_service.get_balance(self.l4l_cookies)
                    self.display.show_status(credits)
                    
                    # Show progress stats
                    stats = self.credits_service.get_statistics()
                    self.display.show_progress(
                        i18n.get_text('status.mission_progress'),
                        int(stats['success_count']),
                        int(stats['failed_count'])
                    )
                    
                    time.sleep(delay)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.display.show_error(str(e))
                    break
                    
        except ValueError:
            self.display.show_error(i18n.get_text('errors.invalid_delay'))

    def handle_twitter_likes(self) -> None:
        """Handle Twitter likes feature."""
        self.display.show_notice(i18n.get_text('actions.enter_delay'))
        try:
            delay = int(self.display.prompt(""))
            self.display.show_notice(i18n.get_text('actions.running_mission'))
            
            while True:
                try:
                    success = self.twitter_feature.execute_like_cycle(self.l4l_cookies)
                    
                    # Update credits display
                    credits = self.credits_service.get_balance(self.l4l_cookies)
                    self.display.show_status(credits)
                    
                    # Show progress stats
                    stats = self.credits_service.get_statistics()
                    self.display.show_progress(
                        i18n.get_text('status.mission_progress'),
                        int(stats['success_count']),
                        int(stats['failed_count'])
                    )
                    
                    time.sleep(delay)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.display.show_error(str(e))
                    break
                    
        except ValueError:
            self.display.show_error(i18n.get_text('errors.invalid_delay'))

    def handle_delete_links(self) -> None:
        """Handle link deletion feature."""
        self.display.show_notice(i18n.get_text('actions.removing_links'))
        # TODO: Implement link deletion
        self.display.show_success(i18n.get_text('actions.links_removed'))

    def select_language(self) -> None:
        """Handle language selection."""
        self.display.show_language_menu()
        choice = self.display.prompt("")
        
        if choice == "1":
            i18n.current_lang = "en"
            i18n.save_language_preference()
        elif choice == "2":
            i18n.current_lang = "id"
            i18n.save_language_preference()
        else:
            self.display.show_error(i18n.get_text('errors.invalid_choice'))
            i18n.current_lang = "en"
            i18n.save_language_preference()

    def run(self) -> None:
        """Run the main menu loop."""
        try:
            # Initial setup
            self.select_language()
            self.display.show_banner()
            
            # Load and validate Like4Like session
            cookies = self.like4like_auth.load_cookies()
            self.l4l_cookies = cookies.get("Like4Like")
            self.fb_cookies = cookies.get("Facebook")
            
            # Ensure we have valid Like4Like session
            self.l4l_cookies = self.ensure_like4like_login()
            
            # Get initial credits
            credits = self.credits_service.get_balance(self.l4l_cookies)
            self.display.show_status(credits)
            
            while True:
                self.display.show_menu()
                choice = self.display.prompt("")
                
                if choice == "1":
                    self.handle_profile_exchange()
                elif choice == "2":
                    self.handle_follow_mission()
                elif choice == "3":
                    self.handle_delete_links()
                elif choice == "4":
                    self.handle_profile_exchange()  # Same as 1 but different feature type
                elif choice == "5":
                    self.handle_twitter_likes()
                elif choice == "6":
                    sys.exit(0)
                elif choice == "7":
                    self.select_language()
                else:
                    self.display.show_error(i18n.get_text('errors.invalid_choice'))
                    
        except Exception as e:
            self.display.show_error(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)