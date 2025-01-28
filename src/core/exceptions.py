"""Custom exceptions for the Like4Book application."""

class Like4BookError(Exception):
    """Base exception for Like4Book application."""
    pass

class AuthenticationError(Like4BookError):
    """Raised when authentication fails."""
    pass

class CookieError(Like4BookError):
    """Raised when there are issues with cookies."""
    pass

class BrowserError(Like4BookError):
    """Raised when browser operations fail."""
    pass

class APIError(Like4BookError):
    """Raised when API requests fail."""
    pass

class ValidationError(Like4BookError):
    """Raised when validation fails."""
    pass

class CreditExchangeError(Like4BookError):
    """Raised when credit exchange fails."""
    pass

class TaskError(Like4BookError):
    """Raised when task operations fail."""
    pass

class ConfigurationError(Like4BookError):
    """Raised when configuration is invalid."""
    pass

class FeatureError(Like4BookError):
    """Raised when a feature operation fails."""
    pass

class LanguageError(Like4BookError):
    """Raised when language-related operations fail."""
    pass