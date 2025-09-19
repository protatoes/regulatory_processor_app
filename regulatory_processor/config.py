"""Configuration and shared data structures for regulatory document processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


class DirectoryNames:
    """Common directory names used across the processing pipeline."""

    SPLIT_DOCS = "split_docs"
    PDF_DOCS = "pdf_docs"
    BACKUP_SUFFIX = ".orig"


class FileMarkers:
    """Filename markers and prefixes that influence processing decisions."""

    ANNEX_MARKER = "_Annex_"
    TEMP_FILE_PREFIX = "~"
    ANNEX_PREFIX = "Annex"


class SectionTypes:
    """Logical document sections handled by the processor."""

    SMPC = "SmPC"
    PL = "PL"


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class ProcessingError(Exception):
    """Base exception for document processing errors."""


class ValidationError(ProcessingError):
    """Raised when input validation fails."""


class DocumentError(ProcessingError):
    """Raised when document manipulation operations fail."""


class MappingError(ProcessingError):
    """Raised when mapping file operations fail."""


# ---------------------------------------------------------------------------
# Core result and stats containers
# ---------------------------------------------------------------------------


@dataclass
class ProcessingResult:
    """Represents the outcome of a processing operation."""

    success: bool
    message: str
    output_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_output(self, *paths: str) -> None:
        """Append generated output paths to the result."""

        self.output_files.extend(path for path in paths if path)

    def add_warning(self, warning: str) -> None:
        """Record a non-fatal warning message."""

        if warning:
            self.warnings.append(warning)

    def merge(self, other: "ProcessingResult") -> None:
        """Merge another result object into this one."""

        self.output_files.extend(other.output_files)
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


@dataclass
class ProcessingStats:
    """Tracks aggregate statistics for a processing run."""

    input_files_found: int = 0
    input_files_processed: int = 0
    documents_skipped: int = 0
    variants_processed: int = 0
    variants_successful: int = 0
    output_files_created: int = 0
    backups_created: int = 0
    annex_i_created: int = 0
    annex_iiib_created: int = 0
    pdfs_created: int = 0
    pdf_failures: int = 0
    warnings_logged: int = 0
    errors_encountered: int = 0

    def success_rate(self) -> float:
        """Return the percentage of successful variants processed."""

        if self.variants_processed == 0:
            return 0.0
        return (self.variants_successful / self.variants_processed) * 100

    # Convenience helpers -------------------------------------------------

    def record_variant(self, success: bool) -> None:
        """Update counters for a processed variant."""

        self.variants_processed += 1
        if success:
            self.variants_successful += 1
        else:
            self.errors_encountered += 1

    def record_backup(self) -> None:
        """Increment the backup counter."""

        self.backups_created += 1

    def record_pdf_result(self, success: bool) -> None:
        """Increment PDF counters based on conversion outcome."""

        if success:
            self.pdfs_created += 1
        else:
            self.pdf_failures += 1

    def record_warning(self, count: int = 1) -> None:
        """Increment the warning counter."""

        self.warnings_logged += max(count, 0)

    def record_outputs(self, count: int) -> None:
        """Increment output file counter by ``count`` if positive."""

        if count > 0:
            self.output_files_created += count


@dataclass
class ProcessingConfig:
    """Runtime configuration for document processing."""

    create_backups: bool = True
    convert_to_pdf: bool = True
    overwrite_existing: bool = False
    log_level: str = "INFO"
    country_delimiter: str = ";"
    strict_filename_matching: bool = True
    allowed_pdf_engines: Sequence[str] = ("docx2pdf", "libreoffice")

    def normalized_log_level(self) -> str:
        """Return the uppercase log level string for logging configuration."""

        return self.log_level.upper()
