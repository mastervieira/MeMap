class AppException(Exception):
    """Base class for all application exceptions."""
    pass

class APIException(AppException):
    """Exception for handling API-related errors."""
    pass

class DatabaseException(AppException):
    """Exception for handling database-related errors."""
    pass

class UIException(AppException):
    """Exception for handling UI-related errors."""
    pass
