"""Core utility functions for the regulatory processor."""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from .config import ProcessingConfig
from .exceptions import ValidationError


# =============================================================================
# COUNTRY AND LANGUAGE MAPPING
# =============================================================================

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
        
        # Single pattern to capture country code after the base structure
        pattern = r'ema-combined-h-\d+-([a-z]{2})'
        match = re.search(pattern, filename, re.IGNORECASE)
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


# =============================================================================
# FILE NAMING AND PATH UTILITIES
# =============================================================================

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


# =============================================================================
# MAPPING TABLE UTILITIES
# =============================================================================

def load_mapping_table(file_path: str) -> Optional[pd.DataFrame]:
    """Load the Excel mapping table."""
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ Error: Mapping file not found: {file_path}")
            return None

        df = pd.read_excel(path)

        print(f"✅ Successfully loaded mapping table: {path.name}")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")

        return df

    except Exception as e:
        print(f"❌ Error loading Excel file: {type(e).__name__}: {str(e)}")
        return None


# =============================================================================
# TEXT NORMALIZATION UTILITIES
# =============================================================================

def normalize_text_for_matching(text: str) -> str:
    """Normalize text for header matching by removing inconsistencies."""
    # Convert to lowercase
    normalized = text.lower()

    # Remove extra whitespace and normalize spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    # Remove common punctuation that might vary
    normalized = re.sub(r'[.,;:!?""''""()]', '', normalized)

    # Remove common formatting artifacts
    normalized = re.sub(r'[\r\n\t]', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized


def contains_as_words(text: str, search_term: str) -> bool:
    """Check if search_term exists as complete words in text, not just as substring."""
    # Escape special regex characters in search term
    escaped_term = re.escape(search_term)

    # Use word boundaries to ensure complete word matching
    pattern = r'\b' + escaped_term + r'\b'

    return bool(re.search(pattern, text, re.IGNORECASE))


def are_similar_headers(text1: str, text2: str) -> bool:
    """Check if two texts are similar annex headers that could be confused."""
    # Comprehensive annex header base words from mapping data
    annex_base_words = [
        'bijlage', 'annexe', 'anhang', 'lisa', 'παραρτημα', 'pielikums',
        'priedas', 'anexo', 'prilog', 'priloga', 'liite', 'bilaga',
        'allegato', 'annex', 'anness', 'bilag', 'viðauki', 'vedlegg',
        'příloha', 'aneks', 'príloha', 'приложение', 'melléklet', 'anexa'
    ]

    # Roman numeral patterns
    roman_patterns = [
        r'[ivx]+',          # Standard: i, ii, iii, iv, v
        r'[ιυχ]+',          # Greek: ι, ιι, ιιι
        r'\d+',             # Arabic numbers: 1, 2, 3 (backup)
    ]

    # Build comprehensive patterns
    all_patterns = []

    for base_word in annex_base_words:
        for roman_pattern in roman_patterns:
            # Pattern 1: Word first (e.g., "ANNEXE I", "BIJLAGE II")
            all_patterns.append(rf'{re.escape(base_word)}\s*\.?\s*{roman_pattern}\.?')

            # Pattern 2: Number first (e.g., "I LISA", "II LISA")
            all_patterns.append(rf'{roman_pattern}\.?\s+{re.escape(base_word)}')

            # Pattern 3: Number with period first (e.g., "I. MELLÉKLET")
            all_patterns.append(rf'{roman_pattern}\.\s*{re.escape(base_word)}')

    # Check if both texts match any of the same patterns
    for pattern in all_patterns:
        if (re.search(pattern, text1, re.IGNORECASE) and
            re.search(pattern, text2, re.IGNORECASE)):
            return True

    # Additional check: if both contain the same base word, they're similar
    text1_lower = text1.lower()
    text2_lower = text2.lower()

    for base_word in annex_base_words:
        if base_word.lower() in text1_lower and base_word.lower() in text2_lower:
            return True

    return False


def is_header_match(paragraph_text: str, header_text: str) -> bool:
    """Check if a paragraph text matches a header with precise word-boundary matching."""
    para_normalized = normalize_text_for_matching(paragraph_text)
    header_normalized = normalize_text_for_matching(header_text)

    # Exact match after normalization
    if para_normalized == header_normalized:
        return True

    # Check if header is contained in paragraph (word boundary matching)
    if contains_as_words(para_normalized, header_normalized):
        return True

    # For very similar headers, be more strict
    if are_similar_headers(para_normalized, header_normalized):
        return False

    # Check if paragraph starts with header (common case)
    if para_normalized.startswith(header_normalized + " "):
        return True

    return False


# =============================================================================
# SECTION IDENTIFICATION UTILITIES
# =============================================================================

def is_section_header(text: str) -> bool:
    """Check if text appears to be a section header (like "7.", "8.", etc.)"""
    text_lower = text.strip().lower()
    # Look for patterns like "7.", "section 7", etc.
    return bool(re.match(r'^\s*\d+\.', text) or re.match(r'^\s*section\s+\d+', text_lower))


def contains_country_local_rep_entry(text: str) -> bool:
    """Check if paragraph contains a country-specific local representative entry."""
    text_stripped = text.strip()
    if not text_stripped:
        return False

    # Look for patterns like "Germany:", "France:", "Ireland:", etc.
    # Match country name at start of line followed by colon
    return bool(re.match(r'^[A-Za-z\s]+:', text_stripped))


def should_keep_local_rep_entry(para_text: str, target_country: str, applicable_reps: str) -> bool:
    """Determine if a local representative entry should be kept based on the target country."""
    # Check if the paragraph contains the target country
    return target_country.lower() in para_text.lower()