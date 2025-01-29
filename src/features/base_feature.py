"""Base feature implementation with common functionality."""

import time
from typing import Dict, Optional


class BaseFeature:
    """Base class for all Like4Like features."""

    def __init__(self):
        """Initialize base feature."""
        self.last_request_time = 0
        self.min_request_interval = 3.0  # Minimum seconds between requests
        self.detect_count = 0  # Track consecutive bot detections

    def _enforce_rate_limit(self) -> None:
        """Enforce minimum time between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def _handle_bot_detection(self, max_retries: int = 3) -> None:
        """Handle bot detection with exponential backoff.
        
        Args:
            max_retries: Maximum number of retry attempts
        """
        # If we've had bot detections, increase delay exponentially
        if self.detect_count > 0:
            backoff_delay = min(300, 30 * (2 ** (self.detect_count - 1)))  # Max 5 min delay
            time.sleep(backoff_delay)
            
        # Increment counter if we still have retries
        if self.detect_count < max_retries:
            self.detect_count += 1