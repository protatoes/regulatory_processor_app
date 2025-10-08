# Module Documentation: config.py

## Overview
Configuration classes and constants module providing centralized configuration management for the regulatory processor. This module defines all configuration classes, constants, enums, and result data structures used throughout the application.

**File Size**: 119 lines
**Key Features**: Configuration dataclasses, constants, result structures, URL validation config

## Constants and Enums

### DirectoryNames
**Purpose**: Standard directory names used throughout the application
**Type**: Static class with string constants

**Constants**:
- `SPLIT_DOCS = "split_docs"` - Directory for split annex documents
- `PDF_DOCS = "pdf_docs"` - Directory for PDF conversions
- `BACKUP_SUFFIX = ".orig"` - Suffix for backup files

### FileMarkers
**Purpose**: File naming patterns and markers for document identification
**Type**: Static class with string constants

**Constants**:
- `ANNEX_MARKER = "_Annex_"` - Marker in filenames indicating annex documents
- `TEMP_FILE_PREFIX = "~"` - Prefix for temporary files (to be excluded)
- `ANNEX_PREFIX = "Annex"` - Prefix for annex document names

### SectionTypes
**Purpose**: Document section type constants
**Type**: Static class with string constants

**Constants**:
- `SMPC = "SmPC"` - Summary of Product Characteristics section
- `PL = "PL"` - Package Leaflet section

## Configuration Classes

### ProcessingConfig
**Purpose**: Main configuration settings for document processing operations
**Type**: `@dataclass` with default values

**Attributes**:
- `create_backups: bool = True` - Whether to create .orig backup files
- `convert_to_pdf: bool = True` - Whether to attempt PDF conversion
- `overwrite_existing: bool = False` - Whether to overwrite existing output files
- `log_level: str = "INFO"` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `country_delimiter: str = ";"` - Delimiter for multi-country processing
- `skip_pdf_in_background: bool = True` - Skip PDF conversion in ThreadPoolExecutor context

**Usage**: Controls behavior of DocumentProcessor and related components

### URLValidationConfig
**Purpose**: Configuration for URL validation and testing in hyperlink processing
**Type**: `@dataclass` with default values

**Attributes**:
- `enable_format_validation: bool = True` - Enable URL format checking
- `enable_accessibility_testing: bool = False` - Enable HTTP accessibility testing (disabled by default)
- `accessibility_timeout: int = 5` - Timeout in seconds for accessibility tests
- `max_concurrent_tests: int = 5` - Maximum concurrent accessibility tests
- `auto_fix_urls: bool = True` - Attempt to auto-fix common URL format issues

**Usage**: Controls behavior of hyperlink validation in `hyperlinks.py`

### HyperlinkProcessingConfig
**Purpose**: Configuration for hyperlink processing in document updates
**Type**: `@dataclass` with nested configuration

**Attributes**:
- `enable_enhanced_hyperlinks: bool = True` - Use enhanced hyperlink creation
- `enable_url_validation: bool = True` - Validate URLs before creating hyperlinks
- `fallback_to_styled_text: bool = True` - Fall back to styled text if hyperlink creation fails
- `log_hyperlink_errors: bool = True` - Log hyperlink processing errors
- `url_validation_config: URLValidationConfig = None` - Nested URL validation configuration

**Post-Init**: Automatically creates `URLValidationConfig()` if not provided

**Usage**: Controls hyperlink behavior in document content updates

## Result and Status Classes

### ProcessingResult
**Purpose**: Result of document processing operations with comprehensive status information
**Type**: `@dataclass` with default factory lists

**Attributes**:
- `success: bool` - Overall success flag
- `message: str` - Human-readable result message
- `output_files: List[str] = field(default_factory=list)` - List of created file paths
- `errors: List[str] = field(default_factory=list)` - List of error messages
- `pending_pdf_conversions: List[Tuple[str, str]] = field(default_factory=list)` - Queued PDF conversions

**Usage**: Returned by all major processing operations for status reporting

### ProcessingStats
**Purpose**: Tracks processing statistics throughout the workflow
**Type**: `@dataclass` with computed properties

**Attributes**:
- `input_files_found: int = 0` - Number of processable documents discovered
- `input_files_processed: int = 0` - Number of documents actually processed
- `variants_processed: int = 0` - Total number of country variants processed
- `variants_successful: int = 0` - Number of successful variant processes
- `output_files_created: int = 0` - Total output files created
- `errors_encountered: int = 0` - Total errors encountered

**Methods**:
- `success_rate() -> float` - Calculate overall success percentage

**Usage**: Provides detailed metrics for process reporting and analysis

## URL Processing Result Classes

### URLValidationResult
**Purpose**: Result of URL format validation with detailed information
**Type**: `@dataclass`

**Attributes**:
- `is_valid: bool` - Whether URL format is valid
- `url: str` - Original URL string
- `protocol: str` - Detected protocol (http, https, mailto)
- `error_message: str = None` - Error description if validation failed
- `normalized_url: str = None` - Auto-corrected URL if applicable

**Usage**: Returned by `hyperlinks.py` validation functions

### URLAccessibilityResult
**Purpose**: Result of URL accessibility testing (HTTP requests)
**Type**: `@dataclass`

**Attributes**:
- `is_accessible: bool` - Whether URL is accessible via HTTP
- `url: str` - Tested URL
- `status_code: int = None` - HTTP status code if available
- `response_time_ms: int = None` - Response time in milliseconds
- `error_message: str = None` - Error description if test failed
- `redirect_url: str = None` - Final URL after redirects

**Usage**: Returned by `hyperlinks.py` accessibility testing functions

## Dependencies
- `dataclasses` - For configuration and result classes
- `typing` - Type hints for List, Tuple, NamedTuple
- No external dependencies - pure Python configuration module

## Design Patterns

### Dataclass Pattern
**Benefit**: Automatic `__init__`, `__repr__`, and `__eq__` methods
**Usage**: All configuration and result classes use `@dataclass` decorator

### Default Factory Pattern
**Benefit**: Avoids mutable default arguments
**Usage**: `field(default_factory=list)` for list attributes

### Nested Configuration
**Benefit**: Hierarchical configuration with automatic initialization
**Usage**: `HyperlinkProcessingConfig` contains `URLValidationConfig`

### Computed Properties
**Benefit**: Dynamic calculation of derived values
**Usage**: `ProcessingStats.success_rate()` calculates percentage from counters

## Integration Points

### ProcessingConfig Usage
- **DocumentProcessor**: Controls backup creation, PDF conversion, logging
- **FileManager**: Controls backup behavior
- **Background Processing**: Controls PDF conversion in threading contexts

### Result Classes Usage
- **ProcessingResult**: Returned by all major processing functions
- **ProcessingStats**: Maintained by DocumentProcessor for progress tracking
- **URL Results**: Used by hyperlink processing for validation feedback

### Constants Usage
- **DirectoryNames**: Used by FileManager for output directory creation
- **FileMarkers**: Used by FileManager for document filtering
- **SectionTypes**: Used by content update functions for section identification

## Configuration Best Practices

### Default Values
All configuration classes provide sensible defaults for immediate usability:
- PDF conversion enabled by default
- Backups enabled by default
- URL validation enabled by default
- Accessibility testing disabled by default (to avoid network dependencies)

### Thread Safety
Configuration objects are immutable after creation, making them thread-safe for background processing.

### Extensibility
Dataclass design allows easy addition of new configuration options without breaking existing code.

## Usage Examples

### Basic Processing Configuration
```python
config = ProcessingConfig(
    create_backups=True,
    convert_to_pdf=False,  # Disable for testing
    log_level="DEBUG"
)
```

### Hyperlink Configuration
```python
hyperlink_config = HyperlinkProcessingConfig(
    enable_enhanced_hyperlinks=True,
    enable_url_validation=True,
    url_validation_config=URLValidationConfig(
        enable_accessibility_testing=True,
        accessibility_timeout=10
    )
)
```

### Result Processing
```python
result = process_folder_enhanced(folder, mapping, config)
if result.success:
    print(f"Created {len(result.output_files)} files")
else:
    print(f"Processing failed: {result.message}")
    for error in result.errors:
        print(f"Error: {error}")
```