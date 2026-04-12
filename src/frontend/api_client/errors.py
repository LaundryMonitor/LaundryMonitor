class FrontendAPIError(Exception):
    """Base error type for frontend API communication."""


class BackendUnavailableError(FrontendAPIError):
    """Raised when the frontend cannot reach the backend."""


class BackendResponseError(FrontendAPIError):
    """Raised when the backend returns an unexpected response."""
