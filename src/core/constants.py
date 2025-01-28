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
FACEBOOK_BASE_URL = "https://web.facebook.com"
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

# Feature types
FEATURE_TYPES = {
    "FACEBOOK_USER_SUB": "facebookusersub",
    "FACEBOOK_SUB": "facebooksub",
    "TWITTER_FAV": "twitterfav"
}