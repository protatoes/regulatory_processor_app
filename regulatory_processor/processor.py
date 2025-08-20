"""Document processing module for EU SmPC and PL documents.

This module contains helper functions to load the mapping Excel file,
update the Annex I (SmPC) and Annex IIIB (Package Leaflet) sections
of combined SmPC Word documents, split the updated documents into
separate Annex I and Annex IIIB files, and convert those files to
PDF using LibreOffice.

Complete implementation with all required functionality:
- National reporting system updates (Section 4.8 SmPC, Section 4 PL)
- Date updates (Section 10 Annex I, Section 6 Annex IIIB)
- Local representatives update (Section 6 Annex IIIB)
- Multi-file generation for languages with multiple countries
- Proper file naming conventions
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, NamedTuple, Union
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.shared import RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx2pdf import convert

# ============================================================================= 
# CONSTANTS AND CONFIGURATION
# =============================================================================

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
    country_delimiter: str = ", "

# ============================================================================= 
# DATE FORMATTING SYSTEM
# =============================================================================

class DateFormatterSystem:
    """Enhanced date formatting system with locale support."""
    
    def __init__(self, mapping_file_path: str):
        self.mapping_df = pd.read_excel(mapping_file_path)
        self.country_formats = self._load_country_formats()
        
    def _load_country_formats(self) -> Dict[str, Dict[str, str]]:
        """Load date formats from the mapping table."""
        formats = {}
        for _, row in self.mapping_df.iterrows():
            country = row['Country']
            formats[country] = {
                'annex_i': row.get('Annex I Date Format', ''),
                'annex_iiib': row.get('Annex IIIB Date Format', '')
            }
        return formats
    
    def format_date(self, date: datetime, country: str, annex_type: str) -> str:
        """Format a date according to country specifications."""
        if country not in self.country_formats:
            return date.strftime("%d %B %Y")  # Default format
            
        format_string = self.country_formats[country].get(annex_type, '')
        return self._parse_custom_format(date, format_string)
    
    def _parse_custom_format(self, date: datetime, format_string: str) -> str:
        """Parse custom format string and return formatted date."""
        if not format_string or format_string.lower() == 'nan':
            return date.strftime("%d %B %Y")
        
        # Handle common patterns
        if format_string == "dd month yyyy":
            return date.strftime("%d %B %Y")
        elif format_string == "month yyyy":
            return date.strftime("%B %Y")
        elif format_string == "dd. MMM yyyy":
            return date.strftime("%d. %b %Y")
        elif format_string == "MMM yyyy":
            return date.strftime("%b %Y")
        else:
            return date.strftime("%d %B %Y")
    
    def get_available_countries(self) -> List[str]:
        """Get list of available countries."""
        return list(self.country_formats.keys())
    
    def preview_format(self, country: str, sample_date: datetime = None) -> Dict[str, str]:
        """Preview date formatting for a country."""
        if sample_date is None:
            sample_date = datetime.now()
        
        if country not in self.country_formats:
            return {'error': f'Country {country} not found'}
        
        return {
            'annex_i_example': self.format_date(sample_date, country, 'annex_i'),
            'annex_iiib_example': self.format_date(sample_date, country, 'annex_iiib')
        }

# Global date formatter instance
_date_formatter: Optional[DateFormatterSystem] = None

def initialize_date_formatter(mapping_file_path: str) -> DateFormatterSystem:
    """Initialize the global date formatter."""
    global _date_formatter
    _date_formatter = DateFormatterSystem(mapping_file_path)
    return _date_formatter

def get_date_formatter() -> DateFormatterSystem:
    """Get the global date formatter instance."""
    global _date_formatter
    if _date_formatter is None:
        raise RuntimeError("Date formatter not initialized")
    return _date_formatter

def format_date_for_country(country: str, annex_type: str, date: Optional[datetime] = None) -> str:
    """Format a date using the enhanced date formatter."""
    if date is None:
        date = datetime.now()
    
    try:
        formatter = get_date_formatter()
        return formatter.format_date(date, country, annex_type)
    except Exception:
        return date.strftime("%d %B %Y")  # Fallback

# ============================================================================= 
# CORE UTILITY FUNCTIONS
# =============================================================================

def load_mapping_table(file_path: str) -> Optional[pd.DataFrame]:
    """Load the Excel mapping table and initialize the date formatter."""
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ Error: Mapping file not found: {file_path}")
            return None
            
        df = pd.read_excel(path)
        
        # Initialize the date formatter
        print(f"🔧 Initializing DateFormatterSystem...")
        try:
            initialize_date_formatter(file_path)
            formatter = get_date_formatter()
            available_countries = formatter.get_available_countries()
            print(f"✅ DateFormatterSystem initialized with {len(available_countries)} countries")
        except Exception as e:
            print(f"❌ Error initializing DateFormatterSystem: {e}")
            return None
        
        print(f"✅ Successfully loaded mapping table: {path.name}")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")
        
        return df
            
    except Exception as e:
        print(f"❌ Error loading Excel file: {type(e).__name__}: {str(e)}")
        return None

def get_country_code_mapping() -> Dict[str, Tuple[str, str]]:
    """Return a mapping of two-letter codes to (language, country)."""
    return {
        'bg': ('Bulgarian', 'Bulgaria'), 'hr': ('Croatian', 'Croatia'),
        'cs': ('Czech', 'Czech Republic'), 'da': ('Danish', 'Denmark'),
        'nl': ('Dutch', 'Netherlands'), 'en': ('English', 'Ireland'),
        'et': ('Estonian', 'Estonia'), 'fi': ('Finnish', 'Finland'),
        'fr': ('French', 'France'), 'de': ('German', 'Germany'),
        'el': ('Greek', 'Greece'), 'hu': ('Hungarian', 'Hungary'),
        'is': ('Icelandic', 'Iceland'), 'it': ('Italian', 'Italy'),
        'lv': ('Latvian', 'Latvia'), 'lt': ('Lithuanian', 'Lithuania'),
        'mt': ('Maltese', 'Malta'), 'no': ('Norwegian', 'Norway'),
        'pl': ('Polish', 'Poland'), 'pt': ('Portuguese', 'Portugal'),
        'ro': ('Romanian', 'Romania'), 'sk': ('Slovak', 'Slovakia'),
        'sl': ('Slovenian', 'Slovenia'), 'es': ('Spanish', 'Spain'),
        'sv': ('Swedish', 'Sweden')
    }

def extract_country_code_from_filename(file_path: str) -> Optional[str]:
    """Extract country code from filename."""
    try:
        filename = Path(file_path).stem
        pattern1 = r'ema-combined-h-\d+-([a-z]{2})-annotated'
        match = re.search(pattern1, filename, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        
        pattern2 = r'ema-combined-h-\d+-([a-z]{2})[-_]'
        match = re.search(pattern2, filename, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        
        return None
    except Exception:
        return None

def identify_document_country_and_language(file_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Identify both country and language from a document filename."""
    country_code = extract_country_code_from_filename(file_path)
    if country_code:
        country_mapping = get_country_code_mapping()
        if country_code in country_mapping:
            language_name, country_name = country_mapping[country_code]
            return country_code, language_name, country_name
    return country_code, None, None

def find_mapping_rows_for_language(mapping_df: pd.DataFrame, language_name: str) -> List[pd.Series]:
    """Find all mapping rows for a given language."""
    language_matches = mapping_df[mapping_df['Language'].str.lower() == language_name.lower()]
    return [language_matches.iloc[i] for i in range(len(language_matches))]

def generate_output_filename(base_name: str, language: str, country: str, doc_type: str) -> str:
    """Generate compliant filename according to specifications."""
    country_clean = country.replace('/', '_').replace(' ', '_')
    
    if doc_type == "combined":
        return f"{base_name}_{country_clean}.docx"
    elif doc_type == "annex_i":
        return f"Annex_I_EU_SmPC_{language}_{country_clean}.docx"
    elif doc_type == "annex_iiib":
        return f"Annex_IIIB_EU_PL_{language}_{country_clean}.docx"
    else:
        return f"{base_name}_{doc_type}.docx"

def convert_to_pdf(doc_path: str, output_dir: str) -> str:
    """Convert a Word document to PDF using docx2pdf."""
    try:
        pdf_output_path = Path(output_dir) / Path(doc_path).with_suffix(".pdf").name
        convert(doc_path, str(pdf_output_path))
        return str(pdf_output_path)
    except Exception as e:
        raise RuntimeError(f"Failed to convert {doc_path} to PDF: {e}")

def copy_paragraph(dest_doc: Document, source_para: Paragraph) -> None:
    """Copy a paragraph from one document to another, preserving runs."""
    new_para = dest_doc.add_paragraph()
    new_para.style = source_para.style
    for run in source_para.runs:
        new_run = new_para.add_run(run.text)
        new_run.bold = run.bold
        new_run.italic = run.italic
        new_run.underline = run.underline
        new_run.style = run.style

# ============================================================================= 
# DOCUMENT UPDATE FUNCTIONS
# =============================================================================

def get_replacement_components(mapping_row: pd.Series, section_type: str, 
                             cached_components: Optional[List] = None, 
                             country_delimiter: str = ", ") -> List:
    """Build replacement text components from mapping data."""
    components = []
    
    # Get line columns for this section type
    line_columns = [col for col in mapping_row.index 
                   if col.startswith('Line ') and section_type in col]
    
    if not line_columns:
        return components
    
    # Get hyperlinks
    hyperlinks_col = f'Hyperlinks {section_type}'
    hyperlinks_str = str(mapping_row.get(hyperlinks_col, '')).strip()
    hyperlinks = [h.strip() for h in hyperlinks_str.split(',') if h.strip() and h.strip().lower() != 'nan']
    
    # Sort line columns by number
    def extract_line_number(col_name):
        match = re.search(r'Line (\d+)', col_name)
        return int(match.group(1)) if match else 999
    
    sorted_columns = sorted(line_columns, key=extract_line_number)
    
    # Find Line 1 to get countries
    line_1_col = None
    for col in sorted_columns:
        if extract_line_number(col) == 1:
            line_1_col = col
            break
    
    if not line_1_col:
        return components
    
    line_1_text = str(mapping_row.get(line_1_col, '')).strip()
    if not line_1_text or line_1_text.lower() == 'nan':
        return components
    
    countries = [c.strip() for c in line_1_text.split(country_delimiter) if c.strip()]
    
    if not countries:
        return components
    
    # Process each line
    for col in sorted_columns:
        line_num = extract_line_number(col)
        content = str(mapping_row.get(col, '')).strip()
        
        if not content or content.lower() == 'nan':
            continue
        
        # Split content by countries using positional matching
        parts = [p.strip() for p in content.split(country_delimiter)]
        
        for i, country in enumerate(countries):
            if i < len(parts) and parts[i]:
                text = parts[i]
                
                # Add hyperlink if available
                hyperlink = hyperlinks[i] if i < len(hyperlinks) else None
                
                components.append({
                    'line': line_num,
                    'country': country,
                    'text': text,
                    'hyperlink': hyperlink
                })
    
    return components

def run_annex_update_v2(doc: Document, mapping_row: pd.Series, section_type: str, 
                       cached_components: Optional[List] = None, 
                       country_delimiter: str = ", ") -> Tuple[bool, Optional[List]]:
    """Update national reporting systems in SmPC or PL sections."""
    
    target_col = f'Original text national reporting - {section_type}'
    target_string = str(mapping_row.get(target_col, '')).strip()
    
    if ":" in target_string:
        target_string = target_string.split(':', 1)[-1].strip()

    if not target_string or target_string.lower() == 'nan':
        return False, None

    components = get_replacement_components(mapping_row, section_type, cached_components, country_delimiter)
    
    if not components:
        return False, None
    
    # Find and replace the target text
    found = False
    for para in doc.paragraphs:
        if target_string.lower() in para.text.lower():
            # Clear paragraph and rebuild with components
            para.clear()
            
            # Group components by line
            lines = {}
            for comp in components:
                line_num = comp['line']
                if line_num not in lines:
                    lines[line_num] = []
                lines[line_num].append(comp)
            
            # Build replacement text
            for line_num in sorted(lines.keys()):
                line_components = lines[line_num]
                line_texts = []
                
                for comp in line_components:
                    if comp['hyperlink']:
                        # Add hyperlink (simplified for this implementation)
                        line_texts.append(f"{comp['text']} ({comp['hyperlink']})")
                    else:
                        line_texts.append(comp['text'])
                
                line_text = country_delimiter.join(line_texts)
                
                if line_num > 1:
                    para.add_run('\n')
                para.add_run(line_text)
            
            found = True
            break
    
    return found, components

def update_section_10_date(doc: Document, mapping_row: pd.Series) -> bool:
    """Update date in Annex I Section 10."""
    country = mapping_row.get('Country', '')
    date_header = mapping_row.get('Annex I Date Text', 'Date of first authorisation/renewal of the authorisation')
    
    if not country:
        return False
    
    try:
        formatted_date = format_date_for_country(country, 'annex_i')
    except Exception:
        date_format = mapping_row.get('Annex I Date Format', '')
        formatted_date = datetime.now().strftime("%d %B %Y")
    
    found = False
    for para in doc.paragraphs:
        text_lower = para.text.lower()
        
        if ('10.' in text_lower and ('first authorisation' in text_lower or 
            'date of first' in text_lower or 
            date_header.lower() in text_lower or
            'date of revision' in text_lower)):
            
            para.clear()
            run = para.add_run(f"{date_header}\n{formatted_date}")
            run.bold = False
            found = True
            break
    
    return found

def update_annex_iiib_date(doc: Document, mapping_row: pd.Series) -> bool:
    """Update date in Annex IIIB Section 6."""
    country = mapping_row.get('Country', '')
    date_text = mapping_row.get('Annex IIIB Date Text', 'This leaflet was last revised in')
    
    if not country:
        return False
    
    try:
        formatted_date = format_date_for_country(country, 'annex_iiib')
    except Exception:
        formatted_date = datetime.now().strftime("%d %B %Y")
    
    found = False
    for para in doc.paragraphs:
        text_lower = para.text.lower()
        
        if (date_text.lower() in text_lower or
            'leaflet was last revised' in text_lower or
            'dernière approbation' in text_lower or
            'última revisión' in text_lower):
            
            para.clear()
            run = para.add_run(f"{date_text} {formatted_date}")
            run.bold = False
            found = True
            break
    
    return found

def update_local_representatives(doc: Document, mapping_row: pd.Series) -> bool:
    """Update local representatives in Section 6 of Annex IIIB."""
    local_rep_text = str(mapping_row.get('Local Representative', '')).strip()
    bold_countries_str = str(mapping_row.get('Country names to be bolded - Local Reps', '')).strip()
    
    if not local_rep_text or local_rep_text.lower() == 'nan':
        return False
    
    bold_countries = [c.strip() for c in bold_countries_str.split(',') 
                     if c.strip() and c.strip().lower() != 'nan']
    
    found = False
    in_section_6 = False
    
    for idx, para in enumerate(doc.paragraphs):
        text_lower = para.text.lower()
        
        # Check if we're entering Section 6
        if ('6.' in text_lower and 'contents of the pack' in text_lower) or \
           ('section 6' in text_lower) or \
           ('contenu de l\'emballage' in text_lower):
            in_section_6 = True
            continue
        
        # Look for existing local rep text to replace
        if in_section_6 and ('marketing authorisation holder' in text_lower or
                            'local representative' in text_lower or
                            'représentant local' in text_lower):
            
            para.clear()
            
            # Process the local rep text line by line
            lines = local_rep_text.split('\n')
            
            for i, line in enumerate(lines):
                if not line.strip():
                    para.add_run('\n')
                    continue
                
                # Check if this line contains a country to be bolded
                should_bold = any(country in line for country in bold_countries)
                
                run = para.add_run(line)
                run.bold = should_bold
                
                if i < len(lines) - 1:
                    para.add_run('\n')
            
            found = True
            break
    
    return found

def split_annexes(source_path: str, output_dir: str, language: str, country: str, mapping_row: pd.Series) -> Tuple[str, str]:
    """Split a combined SmPC document into Annex I and Annex IIIB documents."""
    doc = Document(source_path)
    
    # Create new documents
    annex_i_doc = Document()
    annex_iiib_doc = Document()
    
    current_section = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        # Determine which section we're in
        if 'ANNEX I' in text.upper() or 'SUMMARY OF PRODUCT CHARACTERISTICS' in text.upper():
            current_section = 'annex_i'
        elif 'ANNEX III' in text.upper() or 'PACKAGE LEAFLET' in text.upper():
            current_section = 'annex_iiib'
        
        # Copy paragraph to appropriate document
        if current_section == 'annex_i':
            copy_paragraph(annex_i_doc, para)
        elif current_section == 'annex_iiib':
            copy_paragraph(annex_iiib_doc, para)
    
    # Generate output paths
    base_name = Path(source_path).stem
    annex_i_filename = generate_output_filename(base_name, language, country, "annex_i")
    annex_iiib_filename = generate_output_filename(base_name, language, country, "annex_iiib")
    
    annex_i_path = os.path.join(output_dir, annex_i_filename)
    annex_iiib_path = os.path.join(output_dir, annex_iiib_filename)
    
    # Save documents
    annex_i_doc.save(annex_i_path)
    annex_iiib_doc.save(annex_iiib_path)
    
    return annex_i_path, annex_iiib_path

# ============================================================================= 
# ENHANCED PROCESSOR CLASSES
# =============================================================================

class FileManager:
    """Handles file operations and path management."""
    
    def __init__(self, base_folder: Path, config: ProcessingConfig):
        self.base_folder = base_folder
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.FileManager")
    
    def setup_output_directories(self) -> Tuple[Path, Path]:
        """Create and return paths for output directories."""
        split_dir = self.base_folder / DirectoryNames.SPLIT_DOCS
        pdf_dir = self.base_folder / DirectoryNames.PDF_DOCS
        
        try:
            os.makedirs(split_dir, exist_ok=True)
            os.makedirs(pdf_dir, exist_ok=True)
            return split_dir, pdf_dir
        except OSError as e:
            raise ProcessingError(f"Failed to create output directories: {e}")
    
    def discover_processable_documents(self) -> List[Path]:
        """Find all valid Word documents that can be processed."""
        if not self.base_folder.is_dir():
            raise ValidationError(f"Folder does not exist: {self.base_folder}")
        
        documents = []
        for file_path in self.base_folder.iterdir():
            if self._is_processable_document(file_path):
                documents.append(file_path)
        
        return documents
    
    def _is_processable_document(self, file_path: Path) -> bool:
        """Check if a file is a valid document for processing."""
        if file_path.suffix.lower() != ".docx":
            return False
        if file_path.name.startswith(FileMarkers.TEMP_FILE_PREFIX):
            return False
        if FileMarkers.ANNEX_MARKER in file_path.name:
            return False
        if file_path.name.startswith(FileMarkers.ANNEX_PREFIX):
            return False
        return True
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """Create a backup of the original file."""
        if not self.config.create_backups:
            return None
            
        backup_path = file_path.with_suffix(file_path.suffix + DirectoryNames.BACKUP_SUFFIX)
        if backup_path.exists():
            return backup_path
            
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            return None

class DocumentUpdater:
    """Handles document modification operations."""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.DocumentUpdater")
    
    def apply_all_updates(self, doc: Document, mapping_row: pd.Series) -> Tuple[bool, List[str]]:
        """Apply all required updates to a document."""
        updates_applied = []
        total_success = False
        
        try:
            # 1. Update national reporting systems
            smpc_success, smpc_components = run_annex_update_v2(doc, mapping_row, SectionTypes.SMPC)
            if smpc_success:
                updates_applied.append("SmPC national reporting")
                total_success = True
            
            pl_success, _ = run_annex_update_v2(doc, mapping_row, SectionTypes.PL, smpc_components)
            if pl_success:
                updates_applied.append("PL national reporting")
                total_success = True
            
            # 2. Update dates
            annex_i_date_success = update_section_10_date(doc, mapping_row)
            if annex_i_date_success:
                updates_applied.append("Annex I dates")
                total_success = True
            
            annex_iiib_date_success = update_annex_iiib_date(doc, mapping_row)
            if annex_iiib_date_success:
                updates_applied.append("Annex IIIB dates")
                total_success = True
            
            # 3. Update local representatives
            local_rep_success = update_local_representatives(doc, mapping_row)
            if local_rep_success:
                updates_applied.append("Local representatives")
                total_success = True
                
            return total_success, updates_applied
            
        except Exception as e:
            raise DocumentError(f"Failed to apply document updates: {e}")

class DocumentProcessor:
    """Main document processing orchestrator."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        self.stats = ProcessingStats()
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def process_folder(self, folder_path: str, mapping_path: str) -> ProcessingResult:
        """Main entry point for processing a folder of documents."""
        try:
            self.logger.info("=" * 80)
            self.logger.info("🚀 STARTING ENHANCED DOCUMENT PROCESSING")
            self.logger.info("=" * 80)
            
            # Validate inputs
            folder = self._validate_folder_path(folder_path)
            mapping_df = self._load_and_validate_mapping(mapping_path)
            
            # Setup processing environment
            file_manager = FileManager(folder, self.config)
            split_dir, pdf_dir = file_manager.setup_output_directories()
            
            # Discover documents to process
            documents = file_manager.discover_processable_documents()
            self.stats.input_files_found = len(documents)
            
            if not documents:
                return ProcessingResult(
                    success=False,
                    message="No valid documents found for processing"
                )
            
            # Process each document
            output_files = []
            for document_path in documents:
                try:
                    result = self._process_single_document(
                        document_path, mapping_df, file_manager, split_dir, pdf_dir
                    )
                    output_files.extend(result.output_files)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {document_path.name}: {e}")
                    self.stats.errors_encountered += 1
            
            # Generate final report
            return self._generate_final_result(output_files)
            
        except Exception as e:
            self.logger.error(f"Fatal error in process_folder: {e}")
            return ProcessingResult(
                success=False,
                message=f"Processing failed: {e}",
                errors=[str(e)]
            )
    
    def _validate_folder_path(self, folder_path: str) -> Path:
        """Validate and return folder path."""
        folder = Path(folder_path).resolve()
        if not folder.is_dir():
            raise ValidationError(f"Invalid directory: {folder_path}")
        return folder
    
    def _load_and_validate_mapping(self, mapping_path: str) -> pd.DataFrame:
        """Load and validate mapping file."""
        try:
            mapping_df = load_mapping_table(mapping_path)
            if mapping_df is None or mapping_df.empty:
                raise MappingError(f"Could not load mapping file: {mapping_path}")
            
            self.logger.info(f"Mapping loaded: {len(mapping_df)} configurations")
            return mapping_df
            
        except Exception as e:
            raise MappingError(f"Failed to load mapping file: {e}")
    
    def _process_single_document(
        self,
        document_path: Path,
        mapping_df: pd.DataFrame,
        file_manager: FileManager,
        split_dir: Path,
        pdf_dir: Path
    ) -> ProcessingResult:
        """Process a single document with all its variants."""
        
        self.logger.info("=" * 60)
        self.logger.info(f"📄 PROCESSING: {document_path.name}")
        self.logger.info("=" * 60)
        
        self.stats.input_files_processed += 1
        
        try:
            # Identify document language and country
            country_code, language_name, country_name = identify_document_country_and_language(str(document_path))
            
            if not language_name:
                error_msg = f"Cannot identify language for {document_path.name}"
                self.logger.error(error_msg)
                return ProcessingResult(success=False, message=error_msg)
            
            self.logger.info(f"Document identified - Language: {language_name}, Country: {country_name}")
            
            # Find mapping rows for this language
            mapping_rows = find_mapping_rows_for_language(mapping_df, language_name)
            if not mapping_rows:
                error_msg = f"No mapping found for language: {language_name}"
                self.logger.error(error_msg)
                return ProcessingResult(success=False, message=error_msg)
            
            self.logger.info(f"Found {len(mapping_rows)} variant(s) to process")
            
            # Create backup
            file_manager.create_backup(document_path)
            
            # Process each variant
            output_files = []
            variant_success_count = 0
            
            for i, mapping_row in enumerate(mapping_rows, 1):
                country = mapping_row['Country']
                self.logger.info(f"🌍 Processing variant {i}/{len(mapping_rows)}: {country}")
                
                try:
                    result = self._process_document_variant(
                        document_path, mapping_row, split_dir, pdf_dir
                    )
                    
                    if result.success:
                        variant_success_count += 1
                        self.stats.variants_successful += 1
                        output_files.extend(result.output_files)
                        self.logger.info(f"✅ Variant {i} completed successfully")
                    else:
                        self.logger.warning(f"⚠️ Variant {i} completed with issues: {result.message}")
                    
                    self.stats.variants_processed += 1
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing variant {i} ({country}): {e}")
                    self.stats.errors_encountered += 1
            
            # Document summary
            success_rate = (variant_success_count / len(mapping_rows)) * 100 if mapping_rows else 0
            self.logger.info(f"📊 Document Summary: {variant_success_count}/{len(mapping_rows)} variants successful ({success_rate:.1f}%)")
            
            return ProcessingResult(
                success=variant_success_count > 0,
                message=f"Processed {variant_success_count}/{len(mapping_rows)} variants successfully",
                output_files=output_files
            )
            
        except Exception as e:
            self.logger.error(f"Error processing document {document_path.name}: {e}")
            return ProcessingResult(success=False, message=str(e), errors=[str(e)])
    
    def _process_document_variant(
        self,
        document_path: Path,
        mapping_row: pd.Series,
        split_dir: Path,
        pdf_dir: Path
    ) -> ProcessingResult:
        """Process a single document variant."""
        
        country = mapping_row['Country']
        language = mapping_row['Language']
        
        try:
            # Load document
            doc = Document(str(document_path))
            
            # Apply updates
            updater = DocumentUpdater(self.config)
            updates_made, updates_applied = updater.apply_all_updates(doc, mapping_row)
            
            if not updates_made:
                return ProcessingResult(
                    success=False,
                    message=f"No updates applied for {country} variant"
                )
            
            # Save and process updated document
            return self._save_and_split_document(
                doc, document_path, mapping_row, split_dir, pdf_dir, updates_applied
            )
            
        except Exception as e:
            raise DocumentError(f"Failed to process variant for {country}: {e}")
    
    def _save_and_split_document(
        self,
        doc: Document,
        original_path: Path,
        mapping_row: pd.Series,
        split_dir: Path,
        pdf_dir: Path,
        updates_applied: List[str]
    ) -> ProcessingResult:
        """Save updated document and split into annexes."""
        
        country = mapping_row['Country']
        language = mapping_row['Language']
        output_files = []
        
        try:
            # Generate output filename
            base_name = original_path.stem
            output_filename = generate_output_filename(base_name, language, country, "combined")
            output_path = original_path.parent / output_filename
            
            # Save updated document
            doc.save(str(output_path))
            output_files.append(str(output_path))
            self.logger.info(f"💾 Saved combined document: {output_filename}")
            
            # Split into annexes
            self.logger.info("🔀 Splitting into separate annexes...")
            annex_i_path, annex_iiib_path = split_annexes(
                str(output_path), str(split_dir), language, country, mapping_row
            )
            
            output_files.extend([annex_i_path, annex_iiib_path])
            self.logger.info(f"✅ Split completed")
            
            # Convert to PDF if enabled
            if self.config.convert_to_pdf:
                try:
                    self.logger.info("📄 Converting to PDF...")
                    pdf_annex_i = convert_to_pdf(annex_i_path, str(pdf_dir))
                    pdf_annex_iiib = convert_to_pdf(annex_iiib_path, str(pdf_dir))
                    
                    output_files.extend([pdf_annex_i, pdf_annex_iiib])
                    self.logger.info("✅ PDF conversion completed")
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ PDF conversion failed: {e}")
                    # Continue processing even if PDF conversion fails
            
            self.stats.output_files_created += len(output_files)
            
            return ProcessingResult(
                success=True,
                message=f"Successfully processed {country} variant with updates: {', '.join(updates_applied)}",
                output_files=output_files
            )
            
        except Exception as e:
            raise DocumentError(f"Failed to save and split document: {e}")
    
    def _generate_final_result(self, output_files: List[str]) -> ProcessingResult:
        """Generate final processing result with statistics."""
        
        self.logger.info("=" * 80)
        self.logger.info("✅ ENHANCED PROCESSING COMPLETE")
        self.logger.info("=" * 80)
        
        self.logger.info("📊 Final Statistics:")
        self.logger.info(f"   Input files found: {self.stats.input_files_found}")
        self.logger.info(f"   Input files processed: {self.stats.input_files_processed}")
        self.logger.info(f"   Total variants processed: {self.stats.variants_processed}")
        self.logger.info(f"   Successful variants: {self.stats.variants_successful}")
        self.logger.info(f"   Success rate: {self.stats.success_rate():.1f}%")
        self.logger.info(f"   Output files created: {self.stats.output_files_created}")
        self.logger.info(f"   Errors encountered: {self.stats.errors_encountered}")
        
        success = self.stats.variants_successful > 0
        message = f"Processed {self.stats.variants_successful}/{self.stats.variants_processed} variants successfully"
        
        return ProcessingResult(
            success=success,
            message=message,
            output_files=output_files
        )

# ============================================================================= 
# BACKWARDS COMPATIBILITY INTERFACE
# =============================================================================

def process_folder(folder: str, mapping_path: str) -> None:
    """
    Backwards compatible entry point for processing folders.
    
    This function maintains the same interface as the original implementation
    while using the enhanced processing system under the hood.
    """
    try:
        processor = DocumentProcessor()
        result = processor.process_folder(folder, mapping_path)
        
        if not result.success:
            # Log the error but don't raise exception to maintain backwards compatibility
            logging.error(f"Processing failed: {result.message}")
            if result.errors:
                for error in result.errors:
                    logging.error(f"Error detail: {error}")
    
    except Exception as e:
        # Maintain backwards compatibility by logging errors instead of raising
        logging.error(f"Fatal processing error: {e}")
        raise  # Re-raise to maintain original behavior

def process_folder_enhanced(
    folder: str, 
    mapping_path: str, 
    config: Optional[ProcessingConfig] = None
) -> ProcessingResult:
    """
    Enhanced entry point that returns detailed results.
    
    Args:
        folder: Path to folder containing Word documents
        mapping_path: Path to Excel mapping file
        config: Optional processing configuration
        
    Returns:
        ProcessingResult with detailed success/failure information
    """
    processor = DocumentProcessor(config)
    return processor.process_folder(folder, mapping_path)