"""Configuration, constants, and exception classes for document processing."""

from typing import List, NamedTuple
from dataclasses import dataclass


class DirectoryNames:
    SPLIT_DOCS = "split_docs"
    PDF_DOCS = "pdf_docs"
    BACKUP_SUFFIX = ".orig"


class FileMarkers:
    ANNEX_MARKER = "_Annex_"
    TEMP_FILE_PREFIX = "~"
    ANNEX_PREFIX = "Annex"


class SectionTypes:
    SMPC = "SmPC"
    PL = "PL"


# Custom Exceptions
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


# Result Types
class ProcessingResult(NamedTuple):
    success: bool
    message: str
    output_files: List[str] = []
    errors: List[str] = []


@dataclass
class ProcessingStats:
    """Tracks processing statistics throughout the workflow."""
    input_files_found: int = 0
    input_files_processed: int = 0
    variants_processed: int = 0
    variants_successful: int = 0
    output_files_created: int = 0
    errors_encountered: int = 0
    
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.variants_processed == 0:
            return 0.0
        return (self.variants_successful / self.variants_processed) * 100


@dataclass
class ProcessingConfig:
    """Configuration settings for document processing."""
    create_backups: bool = True
    convert_to_pdf: bool = True
    overwrite_existing: bool = False
    log_level: str = "INFO"
    country_delimiter: str = ";"