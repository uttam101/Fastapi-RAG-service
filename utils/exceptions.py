class ServiceError(Exception):
    """Base class for service-level errors."""
    status_code = 500

    def __init__(self, message: str = "Internal service error"):
        super().__init__(message)
        self.message = message


class ValidationError(ServiceError):
    status_code = 400


class NotFoundError(ServiceError):
    status_code = 404


class ExternalServiceError(ServiceError):
    status_code = 502
