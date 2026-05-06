"""Exceptions raised by datalogic-sdk."""


class DatalogicError(Exception):
    """Base exception for SDK errors."""


class DatalogicValidationError(DatalogicError, ValueError):
    """Raised when a request model contains invalid data."""


class DatalogicAPIError(DatalogicError):
    """Raised when the Datalogics API returns a non-success response."""

    def __init__(self, message: str, *, status_code: int, response_body: str):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
