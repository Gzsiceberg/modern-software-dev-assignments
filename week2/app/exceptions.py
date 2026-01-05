from __future__ import annotations


class AppError(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppError):
    """Exception raised when input validation fails."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=400)


class DatabaseError(AppError):
    """Exception raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)


class ServiceUnavailableError(AppError):
    """Exception raised when an external service is unavailable."""

    def __init__(self, message: str = "Service unavailable"):
        super().__init__(message, status_code=503)
