"""File management utilities for regulatory document processing."""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from docx2pdf import convert

from .date_formatter import initialize_date_formatter, get_date_formatter


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
        
        return df
    except Exception as e:
        print(f"❌ Error loading mapping table: {e}")
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
    """Convert a Word document to PDF with multiple fallback methods."""
    pdf_output_path = Path(output_dir) / Path(doc_path).with_suffix(".pdf").name
    
    # Method 1: Try docx2pdf (primary method)
    try:
        convert(doc_path, str(pdf_output_path))
        return str(pdf_output_path)
    except Exception as e:
        print(f"   ⚠️ docx2pdf conversion failed: {e}")
    
    # Method 2: Try LibreOffice (if available)
    try:
        result = subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf',
            '--outdir', str(output_dir), doc_path
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and pdf_output_path.exists():
            print(f"   ✅ LibreOffice conversion successful")
            return str(pdf_output_path)
        else:
            print(f"   ⚠️ LibreOffice conversion failed: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️ LibreOffice conversion failed: {e}")
    
    # Method 3: Try system-level LibreOffice command
    try:
        cmd = f'cd "{output_dir}" && libreoffice --headless --convert-to pdf "{doc_path}"'
        os.system(cmd)
        if pdf_output_path.exists():
            print(f"   ✅ System LibreOffice conversion successful")
            return str(pdf_output_path)
    except Exception as e:
        print(f"   ⚠️ System LibreOffice conversion failed: {e}")
    
    print(f"   ❌ All PDF conversion methods failed for: {doc_path}")
    return ""