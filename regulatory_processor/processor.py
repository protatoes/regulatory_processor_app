"""Document processing module for EU SmPC and PL documents - Refactored Version.

This module provides backward compatibility while delegating to the new modular structure.
"""

# Import all public APIs from the new modular structure
from .config import (
    DirectoryNames, FileMarkers, SectionTypes,
    ProcessingError, ValidationError, DocumentError, MappingError,
    ProcessingResult, ProcessingStats, ProcessingConfig
)

from .date_formatter import (
    DateFormatterSystem, initialize_date_formatter, 
    get_date_formatter, format_date_for_country
)

from .file_manager import (
    load_mapping_table, get_country_code_mapping, 
    extract_country_code_from_filename, identify_document_country_and_language,
    find_mapping_rows_for_language, generate_output_filename, convert_to_pdf
)

from .document_utils import (
    copy_paragraph, is_hex_gray_color, is_run_gray_shaded, is_run_hyperlink,
    find_target_text_runs, find_target_text_range, find_runs_to_remove,
    create_hyperlink_run, build_replacement_text_by_country, get_replacement_components,
    update_section_10_date, update_annex_iiib_date, update_local_representatives
)

from .document_splitter import (
    split_annexes, split_annexes_enhanced, split_annexes_three_headers_xml,
    find_header_positions, validate_header_order, extract_section_xml
)

from .processor_core import (
    FileManager, DocumentUpdater, DocumentProcessor,
    process_folder, process_folder_enhanced
)

# Re-export all public functions and classes for backward compatibility
__all__ = [
    # Configuration and constants
    'DirectoryNames', 'FileMarkers', 'SectionTypes',
    'ProcessingError', 'ValidationError', 'DocumentError', 'MappingError',
    'ProcessingResult', 'ProcessingStats', 'ProcessingConfig',
    
    # Date formatting
    'DateFormatterSystem', 'initialize_date_formatter', 
    'get_date_formatter', 'format_date_for_country',
    
    # File management
    'load_mapping_table', 'get_country_code_mapping', 
    'extract_country_code_from_filename', 'identify_document_country_and_language',
    'find_mapping_rows_for_language', 'generate_output_filename', 'convert_to_pdf',
    
    # Document utilities
    'copy_paragraph', 'is_hex_gray_color', 'is_run_gray_shaded', 'is_run_hyperlink',
    'find_target_text_runs', 'find_target_text_range', 'find_runs_to_remove',
    'create_hyperlink_run', 'build_replacement_text_by_country', 'get_replacement_components',
    'update_section_10_date', 'update_annex_iiib_date', 'update_local_representatives',
    
    # Document splitting
    'split_annexes', 'split_annexes_enhanced', 'split_annexes_three_headers_xml',
    'find_header_positions', 'validate_header_order', 'extract_section_xml',
    
    # Core processors
    'FileManager', 'DocumentUpdater', 'DocumentProcessor',
    'process_folder', 'process_folder_enhanced'
]