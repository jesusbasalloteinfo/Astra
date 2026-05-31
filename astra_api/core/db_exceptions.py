"""
Custom exceptions for database-related errors in astra_api.
"""

class ObjectAlreadyExistsError(Exception):
    """Raised when an object already exists in the database."""
    pass

class ObjectNotFoundError(Exception):
    """Raised when an object cannot be found in the database."""
    pass

class ObjectFailureError(Exception):
    """Raised when a generic database operation failure occurs."""
    pass
