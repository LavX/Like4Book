"""HTTP utilities for making requests."""

import requests
from typing import Optional, Dict, Any
from requests.exceptions import RequestException

from ..core.constants import DEFAULT_HEADERS
from ..core.exceptions import APIError

def create_session() -> requests.Session:
    """Create a new requests session with default configuration.
    
    Returns:
        requests.Session: Configured session object
    """
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session

def make_request(
    method: str,
    url: str,
    session: Optional[requests.Session] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    allow_redirects: bool = True
) -> requests.Response:
    """Make an HTTP request with error handling.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Target URL
        session: Optional session to use
        headers: Optional additional headers
        cookies: Optional cookies
        data: Optional request data
        params: Optional URL parameters
        timeout: Request timeout in seconds
        allow_redirects: Whether to follow redirects
        
    Returns:
        requests.Response: Response object
        
    Raises:
        APIError: If request fails
    """
    try:
        session = session or create_session()
        
        if headers:
            session.headers.update(headers)
            
        response = session.request(
            method=method,
            url=url,
            cookies=cookies,
            data=data,
            params=params,
            timeout=timeout,
            allow_redirects=allow_redirects
        )
        
        # Raise for 4XX/5XX status codes
        response.raise_for_status()
        
        return response
        
    except RequestException as e:
        raise APIError(f"Request failed: {str(e)}") from e
    except Exception as e:
        raise APIError(f"Unexpected error during request: {str(e)}") from e

def update_session_headers(
    session: requests.Session,
    headers: Dict[str, str]
) -> requests.Session:
    """Update session headers while preserving existing ones.
    
    Args:
        session: Session to update
        headers: New headers to add/update
        
    Returns:
        requests.Session: Updated session
    """
    session.headers.update(headers)
    return session