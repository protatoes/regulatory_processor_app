"""File and mapping table utilities for regulatory document processing."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from docx2pdf import convert

from .config import MappingError, ProcessingConfig
from .date_formatter import get_date_formatter, initialize_date_formatter
from .mapping_table import MappingTable


def load_mapping_table(
    file_path: str, config: Optional[ProcessingConfig] = None
) -> Optional[MappingTable]:
    """Load the mapping workbook, validate columns, and initialize date formatter."""

    cfg = config or ProcessingConfig()
    path = Path(file_path)
    if not path.exists():
        print(f"❌ Error: Mapping file not found: {file_path}")
        return None

    try:
        table = MappingTable.from_excel(path, cfg)
    except MappingError as exc:
        print(f"❌ Mapping validation error: {exc}")
        return None
    except Exception as exc:  # pragma: no cover - defensive
        print(f"❌ Unexpected error loading mapping file: {exc}")
        return None

    # Initialize the date formatter subsystem
    print("🔧 Initializing DateFormatterSystem...")
    try:
        initialize_date_formatter(str(path))
        formatter = get_date_formatter()
        available_countries = formatter.get_available_countries()
        print(f"✅ DateFormatterSystem initialized with {len(available_countries)} countries")
    except Exception as exc:
        print(f"⚠️ Warning: Date formatter could not be initialized: {exc}")

    return table


def get_country_code_mapping() -> Dict[str, Tuple[str, str]]:
    """Return a mapping of two-letter codes to (language, country)."""

    return {
        "bg": ("Bulgarian", "Bulgaria"),
        "hr": ("Croatian", "Croatia"),
        "cs": ("Czech", "Czech Republic"),
        "da": ("Danish", "Denmark"),
        "nl": ("Dutch", "Netherlands"),
        "en": ("English", "Ireland"),
        "et": ("Estonian", "Estonia"),
        "fi": ("Finnish", "Finland"),
        "fr": ("French", "France"),
        "de": ("German", "Germany"),
        "el": ("Greek", "Greece"),
        "hu": ("Hungarian", "Hungary"),
        "is": ("Icelandic", "Iceland"),
        "it": ("Italian", "Italy"),
        "lv": ("Latvian", "Latvia"),
        "lt": ("Lithuanian", "Lithuania"),
        "mt": ("Maltese", "Malta"),
        "no": ("Norwegian", "Norway"),
        "pl": ("Polish", "Poland"),
        "pt": ("Portuguese", "Portugal"),
        "ro": ("Romanian", "Romania"),
        "sk": ("Slovak", "Slovakia"),
        "sl": ("Slovenian", "Slovenia"),
        "es": ("Spanish", "Spain"),
        "sv": ("Swedish", "Sweden"),
    }


def extract_country_code_from_filename(file_path: str) -> Optional[str]:
    """Extract a two-letter country code from the document filename."""

    try:
        filename = Path(file_path).stem
        pattern1 = r"ema-combined-h-\d+-([a-z]{2})-annotated"
        match = re.search(pattern1, filename, re.IGNORECASE)
        if match:
            return match.group(1).lower()

        pattern2 = r"ema-combined-h-\d+-([a-z]{2})[-_]"
        match = re.search(pattern2, filename, re.IGNORECASE)
        if match:
            return match.group(1).lower()

        return None
    except Exception:
        return None


def identify_document_country_and_language(
    file_path: str,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Identify both country and language from a document filename."""

    country_code = extract_country_code_from_filename(file_path)
    if country_code:
        country_mapping = get_country_code_mapping()
        if country_code in country_mapping:
            language_name, country_name = country_mapping[country_code]
            return country_code, language_name, country_name
    return country_code, None, None


def find_mapping_rows_for_language(
    mapping_source: Union[MappingTable, pd.DataFrame], language_name: str
) -> List:
    """Return mapping rows for a given language from either table type."""

    if isinstance(mapping_source, MappingTable):
        return mapping_source.for_language(language_name)

    # Fallback for legacy code paths still expecting a dataframe
    language_matches = mapping_source[
        mapping_source["Language"].str.lower() == language_name.lower()
    ]
    return [language_matches.iloc[i] for i in range(len(language_matches))]


def generate_output_filename(base_name: str, language: str, country: str, doc_type: str) -> str:
    """Generate compliant filename according to specifications."""

    country_clean = country.replace("/", "_").replace(" ", "_")

    if doc_type == "combined":
        return f"{base_name}_{country_clean}.docx"
    if doc_type == "annex_i":
        return f"Annex_I_EU_SmPC_{language}_{country_clean}.docx"
    if doc_type == "annex_iiib":
        return f"Annex_IIIB_EU_PL_{language}_{country_clean}.docx"
    return f"{base_name}_{doc_type}.docx"


def convert_to_pdf(doc_path: str, output_dir: str) -> str:
    """Convert a Word document to PDF with multiple fallback methods."""

    pdf_output_path = Path(output_dir) / Path(doc_path).with_suffix(".pdf").name

    # Method 1: Try docx2pdf (primary method)
    try:
        convert(doc_path, str(pdf_output_path))
        return str(pdf_output_path)
    except Exception as exc:
        print(f"   ⚠️ docx2pdf conversion failed: {exc}")

    # Method 2: Try LibreOffice (if available)
    try:
        result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), doc_path],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0 and pdf_output_path.exists():
            print("   ✅ LibreOffice conversion successful")
            return str(pdf_output_path)
        print(f"   ⚠️ LibreOffice conversion failed: {result.stderr}")
    except Exception as exc:
        print(f"   ⚠️ LibreOffice conversion failed: {exc}")

    # Method 3: Try system-level LibreOffice command
    try:
        cmd = f'cd "{output_dir}" && libreoffice --headless --convert-to pdf "{doc_path}"'
        os.system(cmd)
        if pdf_output_path.exists():
            print("   ✅ System LibreOffice conversion successful")
            return str(pdf_output_path)
    except Exception as exc:
        print(f"   ⚠️ System LibreOffice conversion failed: {exc}")

    print(f"   ❌ All PDF conversion methods failed for: {doc_path}")
    return ""


__all__ = [
    "load_mapping_table",
    "get_country_code_mapping",
    "extract_country_code_from_filename",
    "identify_document_country_and_language",
    "find_mapping_rows_for_language",
    "generate_output_filename",
    "convert_to_pdf",
]
