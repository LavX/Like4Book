"""CLI menu system and command handling."""

import sys
import time
import json
from typing import Tuple, Optional, Dict, Any

from ...core.exceptions import AuthenticationError, FeatureError
from ...auth.like4like import Like4LikeAuth
from ...services.credits import CreditsService
from ...services.browser import BrowserService
from ...i18n.manager import i18n
from .display import DisplayManager

# Import Twitter features
from ...features.twitter.follow import TwitterFollowFeature
from ...features.twitter.like import TwitterLikeFeature
from ...features.twitter.retweet import TwitterRetweetFeature

# Import Facebook features
from ...features.facebook.follow import FacebookFollowFeature
from ...features.facebook.subscribe import FacebookSubscribeFeature
from ...features.facebook.like import FacebookLikeFeature
from ...features.facebook.share import FacebookShareFeature
from ...features.facebook.comment import FacebookCommentFeature

# Import Instagram features
from ...features.instagram.follow import InstagramFollowFeature
from ...features.instagram.like import InstagramLikeFeature
from ...features.instagram.comment import InstagramCommentFeature

# Import TikTok features
from ...features.tiktok.follow import TikTokFollowFeature
from ...features.tiktok.like import TikTokLikeFeature

# Import Pinterest features
from ...features.pinterest.follow import PinterestFollowFeature
from ...features.pinterest.repin import PinterestRepinFeature

# Import SoundCloud features
from ...features.soundcloud.follow import SoundCloudFollowFeature
from ...features.soundcloud.like import SoundCloudLikeFeature

# Import other platform features
from ...features.myspace.connect import MySpaceConnectFeature
from ...features.reverbnation.fan import ReverbNationFanFeature
from ...features.okru.join import OkruJoinFeature

from ...core.constants import FEATURE_TYPES, FEATURE_NAMES

class MenuManager:
    """Manage CLI menu system and user interactions."""

    def __init__(self):
        """Initialize menu manager with required services."""
        self.display = DisplayManager()
        self.like4like_auth = Like4LikeAuth()
        self.credits_service = CreditsService()
        self.browser_service = BrowserService()
        
        # Initialize all feature objects
        # Twitter features
        self.twitter_follow = TwitterFollowFeature()
        self.twitter_like = TwitterLikeFeature()
        self.twitter_retweet = TwitterRetweetFeature()
        
        # Facebook features
        self.facebook_follow = FacebookFollowFeature()
        self.facebook_subscribe = FacebookSubscribeFeature()
        self.facebook_like = FacebookLikeFeature()
        self.facebook_share = FacebookShareFeature()
        self.facebook_comment = FacebookCommentFeature()

        # Instagram features
        self.instagram_follow = InstagramFollowFeature()
        self.instagram_like = InstagramLikeFeature()
        self.instagram_comment = InstagramCommentFeature()

        # TikTok features
        self.tiktok_follow = TikTokFollowFeature()
        self.tiktok_like = TikTokLikeFeature()

        # Pinterest features
        self.pinterest_follow = PinterestFollowFeature()
        self.pinterest_repin = PinterestRepinFeature()

        # SoundCloud features
        self.soundcloud_like = SoundCloudLikeFeature()
        self.soundcloud_follow = SoundCloudFollowFeature()

        # Other platforms
        self.myspace_connect = MySpaceConnectFeature()
        self.reverbnation_fan = ReverbNationFanFeature()
        self.okru_join = OkruJoinFeature()

        # Share credits service with all features
        feature_objects = [
            self.twitter_follow, self.twitter_like, self.twitter_retweet,
            self.facebook_follow, self.facebook_subscribe, self.facebook_like,
            self.facebook_share, self.facebook_comment,
            self.instagram_follow, self.instagram_like, self.instagram_comment,
            self.tiktok_follow, self.tiktok_like,
            self.pinterest_follow, self.pinterest_repin,
            self.soundcloud_like, self.soundcloud_follow,
            self.myspace_connect, self.reverbnation_fan, self.okru_join
        ]
        
        for feature in feature_objects:
            feature.credits_service = self.credits_service
        
        # Map menu choices to features
        self.feature_map = {
            # Twitter Features
            "3": (self.twitter_follow, 'execute_follow_cycle'),
            "4": (self.twitter_like, 'execute_like_cycle'),
            "5": (self.twitter_retweet, 'execute_retweet_cycle'),
            # Facebook Features
            "6": (self.facebook_follow, 'execute_follow_cycle'),
            "7": (self.facebook_subscribe, 'execute_subscribe_cycle'),
            "8": (self.facebook_like, 'execute_like_cycle'),
            "9": (self.facebook_share, 'execute_share_cycle'),
            "10": (self.facebook_comment, 'execute_comment_cycle'),
            # Instagram Features
            "11": (self.instagram_follow, 'execute_follow_cycle'),
            "12": (self.instagram_like, 'execute_like_cycle'),
            "13": (self.instagram_comment, 'execute_comment_cycle'),
            # TikTok Features
            "14": (self.tiktok_follow, 'execute_follow_cycle'),
            "15": (self.tiktok_like, 'execute_like_cycle'),
            # Pinterest Features
            "16": (self.pinterest_follow, 'execute_follow_cycle'),
            "17": (self.pinterest_repin, 'execute_repin_cycle'),
            # SoundCloud Features
            "18": (self.soundcloud_like, 'execute_like_cycle'),
            "19": (self.soundcloud_follow, 'execute_follow_cycle'),
            # Other Platforms
            "20": (self.myspace_connect, 'execute_connect_cycle'),
            "21": (self.reverbnation_fan, 'execute_fan_cycle'),
            "22": (self.okru_join, 'execute_join_cycle')
        }
        
        # State
        self.l4l_cookies = None

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

    def handle_profile_exchange(self) -> None:
        """Handle profile exchange feature."""
        profile_link = self.display.prompt("")
        self.display.show_notice(i18n.get_text('actions.enter_credits'))
        
        try:
            credits = int(self.display.prompt(""))
            self.display.show_notice(i18n.get_text('actions.processing_exchange'))
            
            if self.credits_service.exchange_for_followers(
                self.l4l_cookies,
                profile_link,
                credits
            ):
                self.display.show_success(i18n.get_text('status.exchange_success'))
            else:
                self.display.show_error(i18n.get_text('errors.exchange_failed'))
                
        except ValueError:
            self.display.show_error(i18n.get_text('errors.invalid_credits'))
        except Exception as e:
            self.display.show_error(str(e))

    def handle_feature_mission(self, feature_obj, cycle_method: str) -> None:
        """Generic handler for any feature mission.
        
        Args:
            feature_obj: Feature instance to execute
            cycle_method: Name of the cycle method to call
        """
        self.display.show_notice(i18n.get_text('actions.enter_delay'))
        try:
            delay = int(self.display.prompt(""))
            self.display.show_notice(i18n.get_text('actions.running_mission'))
            self._execute_mission_cycle(feature_obj, cycle_method, delay)
        except ValueError:
            self.display.show_error(i18n.get_text('errors.invalid_delay'))

    def _execute_mission_cycle(self, feature_obj, cycle_method: str, delay: int) -> None:
        """Execute a mission cycle with retry logic and bot detection.
        
        Args:
            feature_obj: Feature instance to execute
            cycle_method: Name of the cycle method to call
            delay: Initial delay between tasks in seconds
        """
        consecutive_failures = 0
        current_delay = delay
        
        while True:
            try:
                # Get previous credits to compare
                previous_credits = self.credits_service.get_balance(self.l4l_cookies)
                
                # Execute the cycle method
                getattr(feature_obj, cycle_method)(self.l4l_cookies)
                
                # Wait for action to register with current delay
                time.sleep(current_delay)
                
                # Get new credits balance
                new_credits = self.credits_service.get_balance(self.l4l_cookies)
                
                # Check if credits changed
                if new_credits <= previous_credits:
                    consecutive_failures += 1
                    current_delay += 5  # Increase delay by 5 seconds on failure
                    self.display.show_notice(f"Task failed. Increasing delay to {current_delay} seconds.")
                    
                    if consecutive_failures >= 3:
                        self.display.show_error("Bot detection triggered. Stopping mission.")
                        break
                else:
                    consecutive_failures = 0  # Reset failure count on success
                    current_delay = delay  # Reset delay to original value
                
                # Update credits display
                self.display.show_status(new_credits)
                
                # Show progress stats
                stats = self.credits_service.get_statistics()
                self.display.show_progress(
                    i18n.get_text('status.mission_progress'),
                    int(stats['success_count']),
                    int(stats['failed_count'])
                )
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                consecutive_failures += 1
                current_delay += 5
                self.display.show_error(f"{str(e)}. Increasing delay to {current_delay} seconds.")
                
                if consecutive_failures >= 3:
                    self.display.show_error("Too many errors. Stopping mission.")
                    break
                    
                time.sleep(current_delay)

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

    def handle_all_features(self) -> None:
        """Run each feature continuously until bot detection, then skip for 10 minutes."""
        self.display.show_notice(i18n.get_text('actions.enter_delay'))
        try:
            delay = int(self.display.prompt(""))
            self.display.show_notice("Running all features mission, use CTRL + C if stuck and CTRL + Z to stop!")
            
            current_feature_index = 0
            feature_items = list(self.feature_map.items())
            skipped_features = set()  # Track features to skip
            
            while True:
                if current_feature_index >= len(feature_items):
                    current_feature_index = 0  # Reset to start if we've gone through all features
                    
                    # Remove features from skip list after 10 minutes
                    if len(skipped_features) > 0:
                        time.sleep(600)  # Wait 10 minutes
                        skipped_features.clear()
                        continue
                
                choice, (feature_obj, method) = feature_items[current_feature_index]
                
                # Skip if feature is in cooldown
                if feature_obj in skipped_features:
                    current_feature_index += 1
                    continue
                    
                # Show which feature we're starting
                feature_name = FEATURE_NAMES.get(choice, f"Feature {choice}")
                self.display.show_notice(f"Starting {feature_name} mission...")
                
                # Run the feature repeatedly until bot detection
                consecutive_failures = 0
                current_delay = delay
                last_error = None
                
                while consecutive_failures < 3:
                    try:
                        # Get previous credits to compare
                        previous_credits = self.credits_service.get_balance(self.l4l_cookies)
                        
                        # Execute the feature
                        getattr(feature_obj, method)(self.l4l_cookies)
                        time.sleep(current_delay)
                        
                        # Get new credits balance
                        new_credits = self.credits_service.get_balance(self.l4l_cookies)
                        
                        # Check if credits changed
                        if new_credits <= previous_credits:
                            consecutive_failures += 1
                            current_delay += 5
                            feature_name = FEATURE_NAMES.get(choice, f"Feature {choice}")
                            self.display.show_notice(f"{feature_name} failed. Increasing delay to {current_delay} seconds.")
                        else:
                            consecutive_failures = 0
                            current_delay = delay
                            
                            # Show progress with feature name
                            feature_name = FEATURE_NAMES.get(choice, f"Feature {choice}")
                            self.display.show_status(new_credits)
                            stats = self.credits_service.get_statistics()
                            progress_msg = f"{i18n.get_text('status.mission_progress')} [Current: {feature_name}]"
                            self.display.show_progress(
                                progress_msg,
                                int(stats['success_count']),
                                int(stats['failed_count'])
                            )
                            
                    except KeyboardInterrupt:
                        return
                    except Exception as e:
                        error_msg = str(e)
                        if "Task response body:" in error_msg:
                            try:
                                # Extract just the JSON response
                                response_start = error_msg.index('{"success"')
                                raw_response = error_msg[response_start:]
                                parsed = json.loads(raw_response)
                                # Skip immediately on permanent errors
                                if "Invalid call" in parsed.get("error", ""):
                                    self.display.show_error(parsed["error"].replace("<br>", ""))
                                    skipped_features.add(feature_obj)
                                    break
                                # For other errors, show cleaned message
                                error_msg = parsed.get("error", "").replace("<br>", "\n").strip()
                            except (ValueError, json.JSONDecodeError, KeyError):
                                pass
                        consecutive_failures += 1
                        current_delay += 5
                        last_error = error_msg
                        feature_name = FEATURE_NAMES.get(choice, f"Feature {choice}")
                        self.display.show_error(f"Error in {feature_name}: {error_msg}")
                
                # After 3 failures, add to skip list and move to next if not already skipped
                if consecutive_failures >= 3 and feature_obj not in skipped_features:
                    error_msg = last_error if last_error else "Maximum interaction count reached"
                    # Clean up the display of JSON response if present
                    if "Task response body:" in error_msg:
                        try:
                            response_start = error_msg.index('{"success"')
                            raw_response = error_msg[response_start:]
                            parsed = json.loads(raw_response)
                            error_msg = parsed.get("error", error_msg).replace("<br>", "\n").strip()
                        except (ValueError, json.JSONDecodeError, KeyError):
                            pass
                    feature_name = FEATURE_NAMES.get(choice, f"Feature {choice}")
                    self.display.show_notice(f"{feature_name} blocked: {error_msg}")
                    self.display.show_notice("Skipping for 10 minutes.")
                    skipped_features.add(feature_obj)
                
                current_feature_index += 1
                    
        except ValueError:
            self.display.show_error(i18n.get_text('errors.invalid_delay'))
        except KeyboardInterrupt:
            return

    def run(self) -> None:
        """Run the main menu loop."""
        try:
            # Initial setup
            self.select_language()
            self.display.show_banner()
            
            # Load and validate Like4Like session
            cookies = self.like4like_auth.load_cookies()
            self.l4l_cookies = cookies.get("Like4Like")
            
            # Ensure we have valid Like4Like session
            self.l4l_cookies = self.ensure_like4like_login()
            
            # Get initial credits
            credits = self.credits_service.get_balance(self.l4l_cookies)
            self.display.show_status(credits)
            
            while True:
                self.display.show_menu()
                choice = self.display.prompt("")
                
                # Run All Features
                if choice == "0":
                    self.handle_all_features()
                # Profile Management
                elif choice == "1":
                    self.handle_profile_exchange()
                elif choice == "2":
                    self.handle_profile_exchange()  # Same as 1 but different type
                
                # Feature missions
                elif choice in self.feature_map:
                    feature_obj, method = self.feature_map[choice]
                    self.handle_feature_mission(feature_obj, method)
                
                # Management
                elif choice == "23":
                    self.handle_delete_links()
                elif choice == "24":
                    self.select_language()
                elif choice == "25":
                    sys.exit(0)
                else:
                    self.display.show_error(i18n.get_text('errors.invalid_choice'))
                    
        except Exception as e:
            self.display.show_error(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)