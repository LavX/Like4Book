"""Global constants for the Like4Book application."""

import os

# Session timeout values
DEFAULT_TIMEOUT = 60  # seconds
BROWSER_WAIT_TIMEOUT = 600  # seconds

# Delays
DEFAULT_DELAY = 5.5  # seconds
LONG_DELAY = 10.5  # seconds
SHORT_DELAY = 2.5  # seconds

# URLs
LIKE4LIKE_BASE_URL = "https://www.like4like.org"

# File paths
DATA_DIR = os.path.join('src', 'data')
os.makedirs(DATA_DIR, exist_ok=True)  # Create data directory if it doesn't exist
COOKIE_FILE_PATH = os.path.join(DATA_DIR, "cookies.json")

# API endpoints
LIKE4LIKE_API = {
    "USER_INFO": "/api/get-user-info.php",
    "GET_TASKS": "/api/get-tasks.php",
    "START_TASK": "/api/start-task.php",
    "VALIDATE_TASK": "/api/validate-task.php",
    "ARCHIVE_TASK": "/api/archive-task.php",
    "DELETE_TASK": "/api/delete-task.php",
    "ENTER_LINK": "/api/enterlink.php"
}

# HTTP Headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9"
}

# Status codes
SUCCESS_CODES = {
    "LIKE4LIKE_SUCCESS": '"success":true,',
    "LIKE4LIKE_CREDITS": '"credits"'
}

# Feature display names
FEATURE_NAMES = {
    "3": "Twitter Follow",
    "4": "Twitter Like",
    "5": "Twitter Retweet",
    "6": "Facebook Follow",
    "7": "Facebook Subscribe",
    "8": "Facebook Like",
    "9": "Facebook Share",
    "10": "Facebook Comment",
    "11": "Instagram Follow",
    "12": "Instagram Like",
    "13": "Instagram Comment",
    "14": "TikTok Follow",
    "15": "TikTok Like",
    "16": "Pinterest Follow",
    "17": "Pinterest Repin",
    "18": "SoundCloud Like",
    "19": "SoundCloud Follow",
    "20": "MySpace Connect",
    "21": "ReverbNation Fan",
    "22": "OK.ru Join"
}

# Feature types
FEATURE_TYPES = {
    # Twitter features
    "TWITTER_FAV": "twitterfav",
    "TWITTER_FOLLOW": "twitterfol",
    "TWITTER_RETWEET": "twitterret",
    
    # Instagram features
    "INSTAGRAM_FOLLOW": "instagramfol",
    "INSTAGRAM_LIKE": "instagramlik",
    "INSTAGRAM_COMMENT": "instagramcom",
    
    # Facebook features
    "FACEBOOK_FOLLOW": "facebookfol",
    "FACEBOOK_PROFILE_FOLLOW": "facebookproffol",
    "FACEBOOK_LIKE": "facebooklik",
    "FACEBOOK_SHARE": "facebooksha",
    "FACEBOOK_COMMENT": "facebookcom",
    
    # TikTok features
    "TIKTOK_FOLLOW": "tiktokfol",
    "TIKTOK_LIKE": "tiktoklik",
    
    # Pinterest features
    "PINTEREST_FOLLOW": "pinterestfol",
    "PINTEREST_REPIN": "pinterestpin",
    
    # SoundCloud features
    "SOUNDCLOUD_LIKE": "soundcloudlik",
    "SOUNDCLOUD_FOLLOW": "soundcloudfol",
    
    # MySpace feature
    "MYSPACE_CONNECT": "myspacecon",
    
    # ReverbNation feature
    "REVERBNATION_FAN": "reverbnationfan",
    
    # OK.ru feature
    "OKRU_JOIN": "okrujoi"
}