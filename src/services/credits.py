"""Credit management service for handling Like4Like credits."""

from typing import Dict, Optional
import json

from ..core.exceptions import CreditExchangeError
from ..core.constants import FEATURE_TYPES
from ..auth.like4like import Like4LikeAuth

class CreditsService:
    """Service for managing Like4Like credits."""

    def __init__(self):
        """Initialize credits service."""
        self.like4like = Like4LikeAuth()
        self.total_credits = "0"
        self.success_count = 0
        self.failed_count = 0

    def get_balance(self, cookies: str, max_retries: int = 3, delay: float = 2.0) -> str:
        """Get current credit balance with retry logic.
        
        Args:
            cookies: Like4Like cookie string
            max_retries: Maximum number of retry attempts (default: 3)
            delay: Base delay between retries in seconds (default: 2.0)
            
        Returns:
            str: Current credit balance
            
        Raises:
            CreditExchangeError: If balance check fails after all retries
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # Exponential backoff delay
                    retry_delay = delay * (2 ** (attempt - 1))
                    time.sleep(retry_delay)
                
                self.total_credits = self.like4like.get_credits(cookies)
                return self.total_credits
                
            except Exception as e:
                last_error = e
                
                # If this was the last attempt, raise the error
                if attempt == max_retries - 1:
                    raise CreditExchangeError(
                        f"Failed to get credit balance after {max_retries} attempts: {str(last_error)}"
                    )

    def calculate_followers(self, credits: str, cost_per_follower: int) -> int:
        """Calculate potential followers based on credits and cost.
        
        Args:
            credits: Total available credits
            cost_per_follower: Credit cost per follower
            
        Returns:
            int: Number of potential followers
        """
        try:
            return int(float(credits) / float(cost_per_follower))
        except (ValueError, ZeroDivisionError):
            return 0

    def record_success(self) -> None:
        """Record a successful credit operation."""
        self.success_count += 1

    def record_failure(self) -> None:
        """Record a failed credit operation."""
        self.failed_count += 1

    def get_statistics(self) -> Dict[str, str]:
        """Get credit operation statistics.
        
        Returns:
            dict: Statistics including total credits and success/failure counts
        """
        return {
            "total_credits": self.total_credits,
            "success_count": str(self.success_count),
            "failed_count": str(self.failed_count)
        }

    def validate_credit_cost(self, cost: int) -> bool:
        """Validate if a credit cost is acceptable.
        
        Args:
            cost: Credit cost to validate
            
        Returns:
            bool: True if cost is valid
        """
        try:
            cost_float = float(cost)
            return 0 < cost_float <= float(self.total_credits)
        except ValueError:
            return False

    def calculate_exchange_rate(self, credits: str, target_amount: int) -> Optional[int]:
        """Calculate credits needed per item for a target amount.
        
        Args:
            credits: Available credits
            target_amount: Desired number of items
            
        Returns:
            int: Credits needed per item, None if not possible
        """
        try:
            available = float(credits)
            if available <= 0 or target_amount <= 0:
                return None
                
            rate = available / target_amount
            return int(rate) if rate >= 1 else None
            
        except (ValueError, ZeroDivisionError):
            return None