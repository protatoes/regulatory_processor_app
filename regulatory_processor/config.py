"""Configuration classes and constants for the regulatory processor."""

from dataclasses import dataclass
from typing import NamedTuple, List


# =============================================================================
# CONSTANTS AND ENUMS
# =============================================================================

class DirectoryNames:
    """Standard directory names used throughout the application."""
    SPLIT_DOCS = "split_docs"
    PDF_DOCS = "pdf_docs"
    BACKUP_SUFFIX = ".orig"


class FileMarkers:
    """File naming patterns and markers."""
    ANNEX_MARKER = "_Annex_"
    TEMP_FILE_PREFIX = "~"
    ANNEX_PREFIX = "Annex"


class SectionTypes:
    """Document section type constants."""
    SMPC = "SmPC"
    PL = "PL"


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================

@dataclass
class ProcessingConfig:
    """Configuration settings for document processing."""
    create_backups: bool = True
    convert_to_pdf: bool = True
    overwrite_existing: bool = False
    log_level: str = "INFO"
    country_delimiter: str = ";"


@dataclass
class URLValidationConfig:
    """Configuration for URL validation and testing."""
    enable_format_validation: bool = True
    enable_accessibility_testing: bool = False  # Disabled by default
    accessibility_timeout: int = 5
    max_concurrent_tests: int = 5
    auto_fix_urls: bool = True


@dataclass
class HyperlinkProcessingConfig:
    """Configuration for hyperlink processing in document updates."""
    enable_enhanced_hyperlinks: bool = True
    enable_url_validation: bool = True
    fallback_to_styled_text: bool = True
    log_hyperlink_errors: bool = True
    url_validation_config: URLValidationConfig = None

    def __post_init__(self):
        if self.url_validation_config is None:
            self.url_validation_config = URLValidationConfig()


# =============================================================================
# RESULT AND STATUS CLASSES
# =============================================================================

class ProcessingResult(NamedTuple):
    """Result of document processing operations."""
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
class URLValidationResult:
    """Result of URL format validation."""
    is_valid: bool
    url: str
    protocol: str
    error_message: str = None
    normalized_url: str = None


@dataclass
class URLAccessibilityResult:
    """Result of URL accessibility testing."""
    is_accessible: bool
    url: str
    status_code: int = None
    response_time_ms: int = None
    error_message: str = None
    redirect_url: str = None