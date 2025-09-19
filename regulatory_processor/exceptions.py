"""Custom exceptions for the regulatory processor."""


class ProcessingError(Exception):
    """Base exception for document processing errors."""
    pass


class ValidationError(ProcessingError):
    """Raised when input validation fails."""
    pass


class DocumentError(ProcessingError):
    """Raised when document operations fail."""
    pass


class MappingError(ProcessingError):
    """Raised when mapping file operations fail."""
    pass