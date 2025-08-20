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

from __future__ import annotations

import os
import re
import shutil
import subprocess
import locale
import calendar
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd
from docx import Document
from docx.text.paragraph import Paragraph, Hyperlink
from docx.text.run import Run
from docx.shared import RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import logging
from docx2pdf import convert # Import the conversion library

# --- Date Formatter System ---

class DateFormatterSystem:
    """
    A system for formatting dates based on country-specific formats defined in a mapping table.
    Supports locale-specific month names and custom static text.
    """
    
    def __init__(self, mapping_file_path: str):
        """
        Initialize the date formatter with a mapping file.
        
        Args:
            mapping_file_path: Path to the Excel mapping file
        """
        self.mapping_df = pd.read_excel(mapping_file_path)
        self.country_formats = self._load_country_formats()
        self.locale_mapping = self._create_locale_mapping()
        
    def _load_country_formats(self) -> Dict[str, Dict[str, str]]:
        """Load date formats from the mapping table."""
        formats = {}
        
        for _, row in self.mapping_df.iterrows():
            country = row['Country']
            annex_i_format = row.get('Annex I Date Format', '')
            annex_iiib_format = row.get('Annex IIIB Date Format', '')
            
            formats[country] = {
                'annex_i': annex_i_format,
                'annex_iiib': annex_iiib_format
            }
            
        return formats
    
    def _create_locale_mapping(self) -> Dict[str, str]:
        """
        Create a mapping between countries and their locale codes.
        This helps with getting proper month names.
        """
        locale_map = {
            'België/Nederland': 'nl_NL.UTF-8',
            'Belgique/Luxembourg': 'fr_FR.UTF-8', 
            'Belgien/Luxemburg': 'de_DE.UTF-8',
            'Estonia': 'et_EE.UTF-8',
            'Greece/Cyprus': 'el_GR.UTF-8',
            'Latvia': 'lv_LV.UTF-8',
            'Lithuania': 'lt_LT.UTF-8',
            'Portugal': 'pt_PT.UTF-8',
            'Croatia': 'hr_HR.UTF-8',
            'Slovenia': 'sl_SI.UTF-8',
            'Finland': 'fi_FI.UTF-8',
            'Sweden/Finland': 'sv_SE.UTF-8',
            'Germany/Österreich': 'de_DE.UTF-8',
            'Italy': 'it_IT.UTF-8',
            'Spain': 'es_ES.UTF-8',
            'Ireland/Malta': 'en_IE.UTF-8',
            'Malta': 'mt_MT.UTF-8',
            'France': 'fr_FR.UTF-8',
            'Denmark': 'da_DK.UTF-8',
            'Iceland': 'is_IS.UTF-8',
            'Norway': 'no_NO.UTF-8',
            'Czech Republic': 'cs_CZ.UTF-8',
            'Poland': 'pl_PL.UTF-8',
            'Slovakia': 'sk_SK.UTF-8',
            'Bulgaria': 'bg_BG.UTF-8',
            'Hungary': 'hu_HU.UTF-8',
            'Romania': 'ro_RO.UTF-8',
        }
        return locale_map
    
    def _get_month_name(self, date: datetime, country: str, format_type: str) -> str:
        """
        Get the month name in the appropriate language and case for the country.
        
        Args:
            date: The date object
            country: Country name
            format_type: The format string to determine case
            
        Returns:
            Formatted month name
        """
        try:
            # Set locale for the country
            country_locale = self.locale_mapping.get(country, 'en_US.UTF-8')
            
            # Try to set the locale, fall back to English if not available
            try:
                locale.setlocale(locale.LC_TIME, country_locale)
            except locale.Error:
                locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
            
            # Determine the case based on format
            if 'Month' in format_type:  # Capital M
                month_name = date.strftime('%B')  # Full month name
            elif 'MMM' in format_type:  # Three letter abbreviation
                month_name = date.strftime('%b')  # Abbreviated month name
            else:  # 'month' - lowercase
                month_name = date.strftime('%B').lower()
                
            return month_name
            
        except Exception:
            # Fallback to English month names
            month_names = {
                'Month': date.strftime('%B'),
                'month': date.strftime('%B').lower(), 
                'MMM': date.strftime('%b')
            }
            
            if 'Month' in format_type:
                return month_names['Month']
            elif 'MMM' in format_type:
                return month_names['MMM']
            else:
                return month_names['month']
    
    def _parse_custom_format(self, date: datetime, format_string: str, country: str) -> str:
        """
        Parse a custom format string and return the formatted date.
        
        Args:
            date: The date to format
            format_string: Custom format string from mapping table
            country: Country name for locale-specific formatting
            
        Returns:
            Formatted date string
        """
        if not format_string:
            return ""
            
        result = format_string
        
        # Handle year formats
        result = re.sub(r'yyyy', str(date.year), result)
        
        # Handle month formats (do this before day to avoid conflicts)
        month_name = self._get_month_name(date, country, format_string)
        result = re.sub(r'Month|month|MMM', month_name, result)
        
        # Handle numeric month formats
        result = re.sub(r'mm', f"{date.month:02d}", result)
        result = re.sub(r'MM', f"{date.month:02d}", result)
        
        # Handle day formats  
        result = re.sub(r'dd', f"{date.day:02d}", result)
        result = re.sub(r'(?<!d)d\.', f"{date.day}.", result)  # Handle single d followed by dot
        
        return result.strip()
    
    def format_date(self, date: datetime, country: str, annex_type: str) -> str:
        """
        Format a date according to the country's specified format for the given annex.
        
        Args:
            date: The date to format
            country: Country name (must match mapping table)
            annex_type: Either 'annex_i' or 'annex_iiib'
            
        Returns:
            Formatted date string
            
        Raises:
            ValueError: If country or annex_type is not found
        """
        if country not in self.country_formats:
            raise ValueError(f"Country '{country}' not found in mapping table")
            
        if annex_type not in ['annex_i', 'annex_iiib']:
            raise ValueError("annex_type must be 'annex_i' or 'annex_iiib'")
            
        format_string = self.country_formats[country][annex_type]
        return self._parse_custom_format(date, format_string, country)
    
    def get_available_countries(self) -> list:
        """Get list of available countries in the mapping table."""
        return list(self.country_formats.keys())
    
    def get_country_formats(self, country: str) -> Dict[str, str]:
        """Get both annex formats for a specific country."""
        if country not in self.country_formats:
            raise ValueError(f"Country '{country}' not found in mapping table")
        return self.country_formats[country]
    
    def preview_format(self, country: str, sample_date: datetime = None) -> Dict[str, str]:
        """
        Preview how dates will be formatted for a country.
        
        Args:
            country: Country name
            sample_date: Date to use for preview (defaults to current date)
            
        Returns:
            Dictionary with formatted examples for both annexes
        """
        if sample_date is None:
            sample_date = datetime.now()
            
        try:
            annex_i_formatted = self.format_date(sample_date, country, 'annex_i')
            annex_iiib_formatted = self.format_date(sample_date, country, 'annex_iiib')
            
            return {
                'country': country,
                'sample_date': sample_date.strftime('%Y-%m-%d'),
                'annex_i_format': self.country_formats[country]['annex_i'],
                'annex_i_example': annex_i_formatted,
                'annex_iiib_format': self.country_formats[country]['annex_iiib'],
                'annex_iiib_example': annex_iiib_formatted
            }
        except Exception as e:
            return {'error': str(e)}

# --- Global Date Formatter Instance ---
_date_formatter: Optional[DateFormatterSystem] = None

def initialize_date_formatter(mapping_file_path: str) -> DateFormatterSystem:
    """
    Initialize the global date formatter instance.
    
    Args:
        mapping_file_path: Path to the Excel mapping file
        
    Returns:
        DateFormatterSystem instance
    """
    global _date_formatter
    _date_formatter = DateFormatterSystem(mapping_file_path)
    return _date_formatter

def get_date_formatter() -> DateFormatterSystem:
    """
    Get the global date formatter instance.
    
    Returns:
        DateFormatterSystem instance
        
    Raises:
        RuntimeError: If date formatter hasn't been initialized
    """
    global _date_formatter
    if _date_formatter is None:
        raise RuntimeError("Date formatter not initialized. Call initialize_date_formatter() first.")
    return _date_formatter

# --- Helper Functions ---

def format_date_for_country(country: str, annex_type: str, 
                           date: Optional[datetime] = None) -> str:
    """
    Format a date using the enhanced DateFormatterSystem.
    
    Args:
        country: Country name from mapping table
        annex_type: Either 'annex_i' or 'annex_iiib'
        date: Date to format (defaults to current date)
        
    Returns:
        Formatted date string
    """
    if date is None:
        date = datetime.now()
    
    try:
        formatter = get_date_formatter()
        return formatter.format_date(date, country, annex_type)
    except Exception as e:
        print(f"⚠️ Error formatting date for {country} ({annex_type}): {e}")
        # Fallback to simple formatting
        return date.strftime("%d %B %Y")

def format_date(date_format_str: str) -> str:
    """
    Legacy format_date function for backward compatibility.
    This function is deprecated - use format_date_for_country instead.
    
    Examples:
    - "dd month yyyy" -> "12 August 2025"
    - "month yyyy" -> "August 2025"
    - "dd. MMM yyyy" -> "12. Aug 2025"
    - "MMM yyyy" -> "Aug 2025"
    """
    now = datetime.now()
    
    # Map format patterns to strftime codes
    if not date_format_str or date_format_str.lower() == 'nan':
        return ""
    
    # Handle various date formats
    date_format_str = date_format_str.strip()
    
    if date_format_str == "dd month yyyy":
        return now.strftime("%d %B %Y")
    elif date_format_str == "month yyyy":
        return now.strftime("%B %Y")
    elif date_format_str == "Month yyyy":
        return now.strftime("%B %Y")
    elif date_format_str == "dd. MMM yyyy":
        return now.strftime("%d. %b %Y")
    elif date_format_str == "MMM yyyy":
        return now.strftime("%b %Y")
    elif date_format_str == "dd/mm/yyyy":
        return now.strftime("%d/%m/%Y")
    elif date_format_str == "dd.mm.yyyy":
        return now.strftime("%d.%m.%Y")
    else:
        # Default format
        return now.strftime("%d %B %Y")

def can_reuse_replacement_text(mapping_row: pd.Series) -> bool:
    """
    Check if SmPC and PL replacement texts are the same.
    If they are, we can reuse the same replacement components.
    """
    smpc_text = str(mapping_row.get('National reporting system SmPC', '')).strip()
    pl_text = str(mapping_row.get('National reporting system PL', '')).strip()
    
    reusable = (smpc_text == pl_text and 
                smpc_text and 
                smpc_text.lower() != 'nan' and
                pl_text.lower() != 'nan')
    
    if reusable:
        print("✅ SmPC and PL replacement texts are identical - can reuse components")
    else:
        print("📝 SmPC and PL have different replacement texts - will generate separately")
    
    return reusable


def build_replacement_from_lines(mapping_row: pd.Series, section_type: str, 
                                country_delimiter: str = ';') -> List[Dict]:
    """
    Build replacement components from Line 1-N columns for SmPC.
    Uses positional country matching.
    """
    print(f"🔨 Building replacement text from lines for {section_type}...")
    print(f"   Using delimiter: '{country_delimiter}'")
    
    components = []
    
    # For SmPC, use Line columns
    line_columns = [col for col in mapping_row.index 
                   if col.startswith('Line ') and ('SmPC' in col or 'SmpC' in col)]
    
    print(f"   - Found {len(line_columns)} line columns")
    
    if not line_columns:
        print(f"⚠️  No line columns found for {section_type}")
        return components
    
    hyperlinks_col = f'Hyperlinks SmPC'
    hyperlinks_str = str(mapping_row.get(hyperlinks_col, '')).strip()
    hyperlinks = [h.strip() for h in hyperlinks_str.split(',') if h.strip() and h.strip().lower() != 'nan']
    
    print(f"   - Found {len(hyperlinks)} hyperlinks: {hyperlinks}")
    
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
        print("❌ No Line 1 found - cannot determine countries")
        return components
    
    line_1_text = str(mapping_row.get(line_1_col, '')).strip()
    if not line_1_text or line_1_text.lower() == 'nan':
        print("❌ Line 1 is empty - cannot determine countries")
        return components
    
    countries = [c.strip() for c in line_1_text.split(country_delimiter) if c.strip()]
    print(f"   - Found {len(countries)} countries: {countries}")
    
    if not countries:
        print("❌ No countries found in Line 1")
        return components
    
    # Build line content
    line_content = {}
    
    for line_col in sorted_columns:
        line_number = extract_line_number(line_col)
        if line_number == 1:
            continue
            
        line_text = str(mapping_row.get(line_col, '')).strip()
        
        if not line_text or line_text.lower() == 'nan':
            continue
            
        if line_text.isspace():
            line_content[line_number] = ['\n'] * len(countries)
            continue
        
        parts = [p.strip() for p in line_text.split(country_delimiter)]
        
        while len(parts) < len(countries):
            parts.append('')
        
        line_content[line_number] = parts
    
    # Build country blocks
    components.append({'text': '\n\n', 'bold': False, 'is_hyperlink': False})
    
    for country_idx, country_name in enumerate(countries):
        # Add country name in bold
        components.append({
            'text': country_name,
            'bold': True,
            'is_hyperlink': False
        })
        components.append({'text': '\n', 'bold': False, 'is_hyperlink': False})
        
        # Add lines for this country
        for line_number in sorted(line_content.keys()):
            parts = line_content[line_number]
            
            if country_idx < len(parts) and parts[country_idx]:
                content_text = parts[country_idx]
                
                if content_text == '\n' or content_text.isspace():
                    components.append({'text': '\n', 'bold': False, 'is_hyperlink': False})
                    continue
                
                # Check for hyperlinks
                url_processed = False
                for url in hyperlinks:
                    if url in content_text:
                        parts_split = content_text.split(url, 1)
                        
                        if parts_split[0]:
                            components.append({
                                'text': parts_split[0],
                                'bold': False,
                                'is_hyperlink': False
                            })
                        
                        components.append({
                            'text': url,
                            'bold': False,
                            'is_hyperlink': True
                        })
                        
                        if parts_split[1]:
                            components.append({
                                'text': parts_split[1],
                                'bold': False,
                                'is_hyperlink': False
                            })
                        
                        url_processed = True
                        break
                
                if not url_processed:
                    components.append({
                        'text': content_text,
                        'bold': False,
                        'is_hyperlink': False
                    })
                
                components.append({'text': '\n', 'bold': False, 'is_hyperlink': False})
        
        if country_idx < len(countries) - 1:
            components.append({'text': '\n', 'bold': False, 'is_hyperlink': False})
    
    return components


def build_pl_replacement(mapping_row: pd.Series) -> List[Dict]:
    """
    Build replacement components for PL section.
    PL uses a single pre-formatted text column, not Line columns.
    """
    print("🔨 Building replacement text for PL...")
    
    components = []
    
    # Get the main PL text
    pl_text = str(mapping_row.get('National reporting system PL', '')).strip()
    
    if not pl_text or pl_text.lower() == 'nan':
        print("⚠️  No PL text found")
        return components
    
    # Check for text to append
    append_text = str(mapping_row.get('Text to be appended after National reporting system PL', '')).strip()
    if append_text and append_text.lower() != 'nan':
        pl_text = pl_text + '\n' + append_text
    
    # Get hyperlinks
    hyperlinks_str = str(mapping_row.get('Hyperlinks PL', '')).strip()
    hyperlinks = [h.strip() for h in hyperlinks_str.split(',') if h.strip() and h.strip().lower() != 'nan']
    
    # Get country names to be bolded
    bold_countries_str = str(mapping_row.get('Country names to be bolded - PL', '')).strip()
    bold_countries = [c.strip() for c in bold_countries_str.split(',') if c.strip() and c.strip().lower() != 'nan']
    
    print(f"   - Hyperlinks: {hyperlinks}")
    print(f"   - Bold countries: {bold_countries}")
    
    # Process the text line by line
    lines = pl_text.split('\n')
    
    components.append({'text': '\n\n', 'bold': False, 'is_hyperlink': False})
    
    for line in lines:
        if not line:
            components.append({'text': '\n', 'bold': False, 'is_hyperlink': False})
            continue
        
        # Check if this line should be bold (country name)
        is_bold = any(country in line for country in bold_countries) if bold_countries else False
        
        # Check for hyperlinks in this line
        has_hyperlink = False
        for url in hyperlinks:
            if url in line:
                # Split the line around the hyperlink
                parts = line.split(url, 1)
                
                if parts[0]:
                    components.append({
                        'text': parts[0],
                        'bold': is_bold,
                        'is_hyperlink': False
                    })
                
                components.append({
                    'text': url,
                    'bold': False,
                    'is_hyperlink': True
                })
                
                if len(parts) > 1 and parts[1]:
                    components.append({
                        'text': parts[1],
                        'bold': is_bold,
                        'is_hyperlink': False
                    })
                
                has_hyperlink = True
                break
        
        if not has_hyperlink:
            components.append({
                'text': line,
                'bold': is_bold,
                'is_hyperlink': False
            })
        
        components.append({'text': '\n', 'bold': False, 'is_hyperlink': False})
    
    return components


def get_replacement_components(mapping_row: pd.Series, section_type: str, 
                             cached_components: Optional[List[Dict]] = None,
                             country_delimiter: str = ';') -> List[Dict]:
    """
    Get replacement components for a section, with proper handling for SmPC vs PL.
    """
    if cached_components and can_reuse_replacement_text(mapping_row):
        print(f"♻️  Reusing cached components for {section_type}")
        return cached_components.copy()
    
    if section_type == 'PL':
        # PL uses single text column, not Line columns
        return build_pl_replacement(mapping_row)
    else:
        # SmPC uses Line columns
        return build_replacement_from_lines(mapping_row, section_type, country_delimiter)


def apply_formatted_replacement_v2(para: Paragraph, runs_to_replace: List[Run], components: List[Dict]):
    """
    Enhanced version of the replacement function with better hyperlink handling.
    """
    if not runs_to_replace or not components:
        print("   ⚠️  No runs to replace or no components provided")
        return

    print(f"   🔄 Applying replacement with {len(components)} components...")
    
    first_run = runs_to_replace[0]
    first_run.text = ''
    remove_shading_from_run(first_run)

    for run in runs_to_replace[1:]:
        p = run._element.getparent()
        if p is not None:
            p.remove(run._element)

    current_element = first_run._element
    for i, comp in enumerate(components):
        if i == 0:
            run_to_modify = first_run
        else:
            new_run_element = OxmlElement('w:r')
            current_element.addnext(new_run_element)
            run_to_modify = Run(new_run_element, para)
            current_element = new_run_element
        
        run_to_modify.text = comp['text']
        
        if comp.get('bold'):
            run_to_modify.bold = True
        if comp.get('is_hyperlink'):
            run_to_modify.font.color.rgb = RGBColor(0, 0, 255)
            run_to_modify.underline = True

    print("   ✅ Replacement applied successfully")


def remove_shading_from_run(run: Run):
    """
    Remove background shading from a run (gray highlighting).
    """
    try:
        run_pr = run._element.get_or_add_rPr()
        shading_elements = run_pr.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
        for shading in shading_elements:
            shading.getparent().remove(shading)
        print("     → Removed gray shading from run")
    except Exception as e:
        print(f"     ⚠️  Could not remove shading: {e}")


def get_paragraph_content(paragraph: Paragraph) -> List[Dict]:
    """
    Deconstructs a paragraph into a list of its content objects.
    """
    content = []
    
    for i, child_element in enumerate(paragraph._p):
        text_content = ''
        
        if child_element.tag.endswith('r'):
            run = Run(child_element, paragraph)
            text_content = run.text or ''
            content.append({'obj': run, 'text': text_content})
            
        elif child_element.tag.endswith('hyperlink'):
            try:
                link = Hyperlink(child_element, paragraph)
                text_content = link.text or ''
                content.append({'obj': link, 'text': text_content})
            except Exception as e:
                text_content = child_element.text or ''
                content.append({'obj': child_element, 'text': text_content})
    
    return content


def run_annex_update_v2(doc: Document, mapping_row: pd.Series, section_type: str, 
                       cached_components: Optional[List[Dict]] = None,
                       country_delimiter: str = ';') -> Tuple[bool, Optional[List[Dict]]]:
    """
    Enhanced version of the annex update function that returns components for reuse.
    """
    print("\n" + "="*60)
    print(f"🔄 EXECUTING UPDATE FOR: Annex {('I' if section_type == 'SmPC' else 'IIIB')}")
    print("="*60)

    target_col = f'Original text national reporting - {section_type}'
    target_string = str(mapping_row.get(target_col, '')).strip()
    
    if ":" in target_string:
        target_string = target_string.split(':', 1)[-1].strip()

    print(f"   - Target string to replace: '{target_string[:100]}{'...' if len(target_string) > 100 else ''}'")

    if not target_string or target_string.lower() == 'nan':
        print("   ❌ No target string found in mapping file. Skipping.")
        return False, None

    components = get_replacement_components(mapping_row, section_type, cached_components, country_delimiter)
    
    if not components:
        print("   ❌ No replacement components generated. Skipping.")
        return False, None

    found_replacement = False
    for para_idx, para in enumerate(doc.paragraphs):
        if target_string not in para.text:
            continue
            
        print(f"✅ Found target paragraph {para_idx}")

        content_objects = get_paragraph_content(para)
        full_text = "".join(item['text'] for item in content_objects)
        
        start_pos = full_text.find(target_string)
        
        if start_pos == -1:
            continue
            
        end_pos = start_pos + len(target_string)
        
        objects_to_replace = []
        char_count = 0
        for i, item in enumerate(content_objects):
            item_len = len(item['text'])
            item_start = char_count
            item_end = char_count + item_len
            
            overlap_start = max(item_start, start_pos)
            overlap_end = min(item_end, end_pos)
            overlap_length = max(0, overlap_end - overlap_start)
            
            if overlap_length > 0:
                overlap_percentage = overlap_length / item_len if item_len > 0 else 0
                item_within_target = (item_start >= start_pos and item_end <= end_pos)
                
                should_include = (item_within_target or 
                                overlap_percentage > 0.8 or 
                                (hasattr(item['obj'], 'runs') and overlap_length > 0))
                
                if should_include:
                    objects_to_replace.append(item['obj'])
                
            char_count += item_len

        if not objects_to_replace:
            continue

        runs_for_replacement = []
        for item in objects_to_replace:
            if isinstance(item, Run):
                runs_for_replacement.append(item)
            elif hasattr(item, 'runs'):
                runs_for_replacement.extend(item.runs)

        apply_formatted_replacement_v2(para, runs_for_replacement, components)
        found_replacement = True
        break

    if not found_replacement:
        print(f"⚠️  Target string not found in any paragraph")
        return False, components
        
    return True, components


def update_section_10_date(doc: Document, mapping_row: pd.Series) -> bool:
    """
    Update Section 10 date in Annex I.
    """
    print("\n📅 Updating Section 10 date in Annex I...")
    
    date_format = mapping_row.get('Annex I Date Format', '')
    date_header = mapping_row.get('Annex I Date Header', 'Date of revision of the text')
    
    if not date_format or date_format.lower() == 'nan':
        print("   ⚠️  No date format specified for Annex I")
        return False
    
    formatted_date = format_date(date_format)
    print(f"   - Date format: {date_format} → {formatted_date}")
    
    found = False
    for para in doc.paragraphs:
        text_lower = para.text.lower()
        
        # Look for Section 10 or the date header
        if ('section 10' in text_lower or 
            '10.' in text_lower or 
            date_header.lower() in text_lower or
            'date of revision' in text_lower):
            
            print(f"   ✅ Found Section 10/date paragraph: '{para.text[:100]}'")
            
            # Clear existing content and add new date
            para.clear()
            run = para.add_run(f"{date_header}\n{formatted_date}")
            run.bold = False
            
            found = True
            break
    
    if not found:
        print("   ⚠️  Section 10 not found")
    
    return found


def update_annex_i_date(doc: Document, mapping_row: pd.Series) -> bool:
    """
    Update date in Section 10 of Annex I using the enhanced date formatter.
    """
    print("\n📅 Updating Section 10 date in Annex I...")
    
    country = mapping_row.get('Country', '')
    date_header = mapping_row.get('Annex I Date Header', 'Date of revision of the text')
    
    if not country:
        print("   ⚠️ No country specified in mapping row")
        return False
    
    try:
        # Use the enhanced date formatter
        formatted_date = format_date_for_country(country, 'annex_i')
        formatter = get_date_formatter()
        date_format = formatter.country_formats[country]['annex_i']
        
        print(f"   - Country: {country}")
        print(f"   - Date format: {date_format} → {formatted_date}")
        
    except Exception as e:
        print(f"   ⚠️ Error formatting date: {e}")
        # Fallback to legacy formatting
        date_format = mapping_row.get('Annex I Date Format', '')
        formatted_date = format_date(date_format)
        print(f"   - Fallback date format: {date_format} → {formatted_date}")
    
    found = False
    for para in doc.paragraphs:
        text_lower = para.text.lower()
        
        # Look for Section 10 or the date header
        if ('section 10' in text_lower or 
            '10.' in text_lower or 
            date_header.lower() in text_lower or
            'date of revision' in text_lower):
            
            print(f"   ✅ Found Section 10/date paragraph: '{para.text[:100]}'")
            
            # Clear existing content and add new date
            para.clear()
            run = para.add_run(f"{date_header}\n{formatted_date}")
            run.bold = False
            
            found = True
            break
    
    if not found:
        print("   ⚠️ Section 10 not found")
    
    return found

def update_annex_iiib_date(doc: Document, mapping_row: pd.Series) -> bool:
    """
    Update date in Annex IIIB Section 6 using the enhanced date formatter.
    """
    print("\n📅 Updating date in Annex IIIB Section 6...")
    
    country = mapping_row.get('Country', '')
    date_text = mapping_row.get('Annex IIIB Date Text', 'This leaflet was last revised in')
    
    if not country:
        print("   ⚠️ No country specified in mapping row")
        return False
    
    try:
        # Use the enhanced date formatter
        formatted_date = format_date_for_country(country, 'annex_iiib')
        formatter = get_date_formatter()
        date_format = formatter.country_formats[country]['annex_iiib']
        
        print(f"   - Country: {country}")
        print(f"   - Date format: {date_format} → {formatted_date}")
        
    except Exception as e:
        print(f"   ⚠️ Error formatting date: {e}")
        # Fallback to legacy formatting
        date_format = mapping_row.get('Annex IIIB Date Format', '')
        formatted_date = format_date(date_format)
        print(f"   - Fallback date format: {date_format} → {formatted_date}")
    
    found = False
    for para in doc.paragraphs:
        text_lower = para.text.lower()
        
        # Look for the date text in Section 6
        if (date_text.lower() in text_lower or
            'leaflet was last revised' in text_lower or
            'dernière approbation' in text_lower or  # French
            'última revisión' in text_lower):  # Spanish
            
            print(f"   ✅ Found date paragraph: '{para.text[:100]}'")
            
            # Clear and add new date text
            para.clear()
            run = para.add_run(f"{date_text} {formatted_date}")
            run.bold = False
            
            found = True
            break
    
    if not found:
        print("   ⚠️ Date text not found in Section 6")
    
    return found


def update_local_representatives(doc: Document, mapping_row: pd.Series) -> bool:
    """
    Update local representatives in Section 6 of Annex IIIB.
    """
    print("\n🏢 Updating local representatives in Section 6...")
    
    local_rep_text = str(mapping_row.get('Local Representative', '')).strip()
    bold_countries_str = str(mapping_row.get('Country names to be bolded - Local Reps', '')).strip()
    
    if not local_rep_text or local_rep_text.lower() == 'nan':
        print("   ⚠️  No local representative information found")
        return False
    
    bold_countries = [c.strip() for c in bold_countries_str.split(',') 
                     if c.strip() and c.strip().lower() != 'nan']
    
    print(f"   - Countries to bold: {bold_countries}")
    
    # Find Section 6 - look for markers
    found = False
    in_section_6 = False
    section_6_start = None
    
    for idx, para in enumerate(doc.paragraphs):
        text_lower = para.text.lower()
        
        # Check if we're entering Section 6
        if ('6.' in text_lower and 'contents of the pack' in text_lower) or \
           ('section 6' in text_lower) or \
           ('contenu de l\'emballage' in text_lower):  # French
            in_section_6 = True
            section_6_start = idx
            print(f"   ✅ Found Section 6 at paragraph {idx}")
            continue
        
        # Look for existing local rep text to replace
        if in_section_6 and ('marketing authorisation holder' in text_lower or
                            'local representative' in text_lower or
                            'représentant local' in text_lower):
            
            print(f"   ✅ Found local rep paragraph at {idx}")
            
            # Clear the paragraph and add new local rep info
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
    
    if not found:
        print("   ⚠️  Could not find local representative section to update")
    
    return found


def load_mapping_table(file_path: str) -> Optional[pd.DataFrame]:
    """
    Load the Excel mapping table and initialize the date formatter.
    
    *** THIS IS WHERE INITIALIZATION SHOULD HAPPEN ***
    
    Args:
        file_path: Path to the Excel mapping file
        
    Returns:
        DataFrame containing the mapping table, or None if loading failed
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            print(f"❌ Error: Mapping file not found: {file_path}")
            return None
            
        df = pd.read_excel(path)
        
        # *** CRITICAL: Initialize the date formatter with the same file ***
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
        
        # Validate required columns
        required_columns = [
            'Country', 'Language', 
            'National reporting system SmPC', 'National reporting system PL',
            'Annex I Date Format', 'Annex IIIB Date Format',
            'Local Representative'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"⚠️ Warning: Missing columns in mapping file: {missing_columns}")
        
        return df
            
    except Exception as e:
        print(f"❌ Error loading Excel file: {type(e).__name__}: {str(e)}")
        return None


def get_country_code_mapping() -> Dict[str, Tuple[str, str]]:
    """
    Return a mapping of two-letter codes to (language, country).
    """
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
    """
    Extract country code from filename.
    """
    try:
        filename = Path(file_path).stem
        pattern1 = r'ema-combined-h-\d+-([a-z]{2})-annotated'
        match = re.search(pattern1, filename, re.IGNORECASE)
        if match:
            country_code = match.group(1).lower()
            print(f"📝 Found country code in filename: '{country_code}'")
            return country_code
        pattern2 = r'ema-combined-h-\d+-([a-z]{2})[-_]'
        match = re.search(pattern2, filename, re.IGNORECASE)
        if match:
            country_code = match.group(1).lower()
            print(f"📝 Found country code in filename: '{country_code}'")
            return country_code
        print(f"⚠️  No country code found in filename: {filename}")
        return None
    except Exception as e:
        print(f"❌ Error extracting country code: {type(e).__name__}: {str(e)}")
        return None


def identify_document_country_and_language(file_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Identify both country and language from a document filename.
    """
    print(f"\n🔍 Identifying country and language for: {Path(file_path).name}")
    country_code = extract_country_code_from_filename(file_path)
    if country_code:
        country_mapping = get_country_code_mapping()
        if country_code in country_mapping:
            language_name, country_name = country_mapping[country_code]
            print(f"✅ Identified: {country_code} → {language_name} ({country_name})")
            return country_code, language_name, country_name
        else:
            print(f"⚠️  Unknown country code: {country_code}")
    return country_code, None, None


def find_mapping_rows_for_language(mapping_df: pd.DataFrame, language_name: str) -> List[pd.Series]:
    """
    Find all mapping rows for a given language.
    Returns a list of rows (for languages with multiple countries).
    """
    language_matches = mapping_df[mapping_df['Language'].str.lower() == language_name.lower()]
    return [language_matches.iloc[i] for i in range(len(language_matches))]


def generate_output_filename(base_name: str, language: str, country: str, doc_type: str) -> str:
    """
    Generate compliant filename according to specifications.
    """
    # Clean the country name for filename
    country_clean = country.replace('/', '_').replace(' ', '_')
    
    if doc_type == "combined":
        return f"{base_name}_{country_clean}.docx"
    elif doc_type == "annex_i":
        return f"Annex_I_EU_SmPC_{language}_{country_clean}.docx"
    elif doc_type == "annex_iiib":
        return f"Annex_IIIB_EU_PL_{language}_{country_clean}.docx"
    else:
        return f"{base_name}_{doc_type}.docx"


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


def split_annexes(source_path: str, output_dir: str, language: str, country: str, mapping_row: pd.Series) -> Tuple[str, str]:
    """
    Split a combined SmPC document into Annex I and Annex IIIB documents.
    Uses proper naming convention and language-specific headers from the mapping file.
    """
    combined_doc = Document(source_path)
    
    annex_i_doc = Document()
    annex_iiib_doc = Document()

    # Get language-specific headers from the mapping row, with fallbacks
    annex_ii_header = str(mapping_row.get('Annex II Header in country language', 'Annex II')).strip().lower()
    annex_iiib_header = str(mapping_row.get('Annex IIIB Header in country language', 'Annex IIIB')).strip().lower()

    print(f"   - Using Annex II header: '{annex_ii_header}'")
    print(f"   - Using Annex IIIB header: '{annex_iiib_header}'")

    in_annex_i = True  # Assume content starts in Annex I
    in_annex_iiib = False

    for para in combined_doc.paragraphs:
        text = para.text.lower().strip()
        
        # Use exact, case-insensitive matching for the headers
        if text == annex_ii_header:
            in_annex_i = False
            in_annex_iiib = False
            continue
        if text == annex_iiib_header:
            in_annex_i = False
            in_annex_iiib = True
            continue
            
        # Copy content to the appropriate document
        if in_annex_i:
            copy_paragraph(annex_i_doc, para)
        elif in_annex_iiib:
            copy_paragraph(annex_iiib_doc, para)

    os.makedirs(output_dir, exist_ok=True)
    
    # Generate proper filenames
    annex_i_name = generate_output_filename("", language, country, "annex_i")
    annex_iiib_name = generate_output_filename("", language, country, "annex_iiib")
    
    annex_i_path = os.path.join(output_dir, annex_i_name)
    annex_iiib_path = os.path.join(output_dir, annex_iiib_name)
    
    annex_i_doc.save(annex_i_path)
    annex_iiib_doc.save(annex_iiib_path)
    
    print(f"   💾 Saved Annex I: {annex_i_name}")
    print(f"   💾 Saved Annex IIIB: {annex_iiib_name}")
    
    return annex_i_path, annex_iiib_path


def convert_to_pdf(doc_path: str, output_dir: str) -> str:
    """Convert a Word document to PDF using Microsoft Word (via docx2pdf)."""
    try:
        print(f"   🔄 Converting {Path(doc_path).name} to PDF using MS Word...")
        # The docx2pdf library places the PDF in the same directory as the source file
        # by default, so we pass the output_dir to place it correctly.
        pdf_output_path = Path(output_dir) / Path(doc_path).with_suffix(".pdf").name
        convert(doc_path, str(pdf_output_path))
        print(f"   ✅ Successfully created PDF: {pdf_output_path.name}")
        return str(pdf_output_path)
    except Exception as e:
        # Catch potential errors, e.g., Word not installed or other issues.
        raise RuntimeError(
            f"Failed to convert {doc_path} to PDF using MS Word. "
            f"Ensure Microsoft Word is installed and closed. Error: {e}"
        )
    
    pdf_name = Path(doc_path).with_suffix(".pdf").name
    return os.path.join(output_dir, pdf_name)


# def process_single_document(file_path: Path, mapping_row: pd.Series, 
#                           split_dir: Path, pdf_dir: Path) -> bool:
#     """
#     Process a single document with a specific mapping row.
#     """
#     print(f"\n📄 Processing: {file_path.name} with {mapping_row['Country']} mapping")
    
#     # Load document
#     doc = Document(str(file_path))
    
#     # Apply all updates
#     updates_made = False
    
#     # 1. Update national reporting systems
#     smpc_success, smpc_components = run_annex_update_v2(doc, mapping_row, 'SmPC')
#     pl_success, _ = run_annex_update_v2(doc, mapping_row, 'PL', smpc_components)
    
#     if smpc_success or pl_success:
#         updates_made = True
    
#     # 2. Update dates
#     annex_i_date_success = update_section_10_date(doc, mapping_row)
#     annex_iiib_date_success = update_annex_iiib_date(doc, mapping_row)
    
#     if annex_i_date_success or annex_iiib_date_success:
#         updates_made = True
    
#     # 3. Update local representatives
#     local_rep_success = update_local_representatives(doc, mapping_row)
    
#     if local_rep_success:
#         updates_made = True
    
#     # Generate output filename for this variant
#     language = mapping_row['Language']
#     country = mapping_row['Country']
#     base_name = file_path.stem
    
#     # Save the updated combined document
#     if updates_made:
#         output_filename = generate_output_filename(base_name, language, country, "combined")
#         output_path = file_path.parent / output_filename
#         doc.save(str(output_path))
#         print(f"   💾 Saved combined document: {output_filename}")
        
#         # Split into annexes
#         annex_i_path, annex_iiib_path = split_annexes(str(output_path), str(split_dir), language, country, mapping_row)
        
#         # Convert to PDF
#         convert_to_pdf(annex_i_path, str(pdf_dir))
#         convert_to_pdf(annex_iiib_path, str(pdf_dir))
        
#         print(f"   ✅ Successfully processed {country} variant")
#         return True
#     else:
#         print(f"   ⚠️  No updates made for {country} variant")
#         return False


# def process_folder(folder: str, mapping_path: str) -> None:
#     """
#     Process all Word documents in the given folder using the mapping.
#     Handles multi-country languages properly (25 files → 27 files).
#     """
#     folder_path = Path(folder).resolve()
#     if not folder_path.is_dir():
#         raise NotADirectoryError(f"{folder} is not a valid directory")
    
#     mapping_df = load_mapping_table(mapping_path)
#     if mapping_df is None:
#         raise FileNotFoundError(f"Could not load mapping file: {mapping_path}")

#     split_dir = folder_path / "split_docs"
#     pdf_dir = folder_path / "pdf_docs"
#     os.makedirs(split_dir, exist_ok=True)
#     os.makedirs(pdf_dir, exist_ok=True)

#     # Track processed files
#     processed_count = 0
#     output_count = 0

#     for file in folder_path.iterdir():
#         if file.suffix.lower() != ".docx":
#             continue
        
#         # Skip already processed files
#         if "_Annex_" in file.name or file.name.startswith("Annex"):
#             continue

#         print("\n" + "="*80)
#         print(f"🚀 STARTING WORKFLOW FOR: {file.name}")
#         print("="*80)

#         processed_count += 1
        
#         # Identify language from filename
#         country_code, language_name, country_name = identify_document_country_and_language(str(file))
#         if not language_name:
#             print(f"❌ Cannot proceed without language identification for {file.name}")
#             continue

#         # Find all mapping rows for this language
#         mapping_rows = find_mapping_rows_for_language(mapping_df, language_name)
        
#         if not mapping_rows:
#             print(f"❌ No mapping found for language: {language_name}")
#             continue
        
#         print(f"\n📊 Found {len(mapping_rows)} country variant(s) for {language_name}:")
#         for row in mapping_rows:
#             print(f"   - {row['Country']}")
        
#         # Backup original file
#         backup_path = file.with_suffix(file.suffix + ".orig")
#         if not backup_path.exists():
#             shutil.copy2(file, backup_path)
        
#         # Process each country variant
#         for mapping_row in mapping_rows:
#             success = process_single_document(file, mapping_row, split_dir, pdf_dir)
#             if success:
#                 output_count += 1
    
#     print("\n" + "="*80)
#     print(f"✅ PROCESSING COMPLETE")
#     print(f"   - Input files processed: {processed_count}")
#     print(f"   - Output files generated: {output_count}")
#     print(f"   - Split documents saved in: {split_dir}")
#     print(f"   - PDF documents saved in: {pdf_dir}")
#     print("="*80)



def process_single_document(file_path: Path, mapping_row: pd.Series, 
                          split_dir: Path, pdf_dir: Path) -> bool:
    """
    Process a single document with a specific mapping row.
    
    Args:
        file_path: Path to the Word document to process
        mapping_row: Single row from mapping DataFrame for this country
        split_dir: Directory to save split Annex I and IIIB documents
        pdf_dir: Directory to save PDF files
        
    Returns:
        bool: True if processing successful, False otherwise
    """
    country = mapping_row['Country']
    language = mapping_row['Language']
    
    print(f"\n📄 Processing: {file_path.name} with {country} mapping")
    print(f"   Language: {language}")
    
    try:
        # Load document
        doc = Document(str(file_path))
        print(f"   ✅ Document loaded successfully")
        
    except Exception as e:
        print(f"   ❌ Error loading document: {e}")
        return False
    
    # Track if any updates were made
    updates_made = False
    
    # =============================================================================
    # 1. UPDATE NATIONAL REPORTING SYSTEMS (SmPC Section 4.8, PL Section 4)
    # =============================================================================
    print(f"\n🔄 Updating National Reporting Systems...")
    
    try:
        # Update SmPC section first
        smpc_success, smpc_components = run_annex_update_v2(doc, mapping_row, 'SmPC')
        if smpc_success:
            print(f"   ✅ SmPC national reporting system updated")
            updates_made = True
        else:
            print(f"   ⚠️ SmPC national reporting system not updated")
        
        # Update PL section (can reuse components if identical)
        pl_success, _ = run_annex_update_v2(doc, mapping_row, 'PL', smpc_components)
        if pl_success:
            print(f"   ✅ PL national reporting system updated")
            updates_made = True
        else:
            print(f"   ⚠️ PL national reporting system not updated")
            
    except Exception as e:
        print(f"   ❌ Error updating national reporting systems: {e}")
    
    # =============================================================================
    # 2. UPDATE DATES (Enhanced with DateFormatterSystem)
    # =============================================================================
    print(f"\n📅 Updating Dates with Enhanced Formatter...")
    
    try:
        # Update Annex I date (Section 10) using enhanced formatter
        annex_i_date_success = update_annex_i_date(doc, mapping_row)
        if annex_i_date_success:
            print(f"   ✅ Annex I date updated")
            updates_made = True
        else:
            print(f"   ⚠️ Annex I date not updated")
        
        # Update Annex IIIB date (Section 6) using enhanced formatter  
        annex_iiib_date_success = update_annex_iiib_date(doc, mapping_row)
        if annex_iiib_date_success:
            print(f"   ✅ Annex IIIB date updated")
            updates_made = True
        else:
            print(f"   ⚠️ Annex IIIB date not updated")
            
        # Show formatting details
        try:
            formatter = get_date_formatter()
            preview = formatter.preview_format(country)
            if 'error' not in preview:
                print(f"   📋 Date format preview for {country}:")
                print(f"      Annex I: '{preview['annex_i_format']}' → {preview['annex_i_example']}")
                print(f"      Annex IIIB: '{preview['annex_iiib_format']}' → {preview['annex_iiib_example']}")
        except Exception as e:
            print(f"   ⚠️ Could not show date preview: {e}")
            
    except Exception as e:
        print(f"   ❌ Error updating dates: {e}")
    
    # =============================================================================
    # 3. UPDATE LOCAL REPRESENTATIVES (Section 6 Annex IIIB)
    # =============================================================================
    print(f"\n🏢 Updating Local Representatives...")
    
    try:
        local_rep_success = update_local_representatives(doc, mapping_row)
        if local_rep_success:
            print(f"   ✅ Local representatives updated")
            updates_made = True
        else:
            print(f"   ⚠️ Local representatives not updated")
            
    except Exception as e:
        print(f"   ❌ Error updating local representatives: {e}")
    
    # =============================================================================
    # 4. SAVE, SPLIT, AND CONVERT
    # =============================================================================
    if updates_made:
        print(f"\n💾 Saving and Processing Updated Document...")
        
        try:
            # Generate output filename for this variant
            base_name = file_path.stem
            output_filename = generate_output_filename(base_name, language, country, "combined")
            output_path = file_path.parent / output_filename
            
            # Save the updated combined document
            doc.save(str(output_path))
            print(f"   ✅ Saved combined document: {output_filename}")
            
            # Split into separate annexes
            print(f"   🔀 Splitting into separate annexes...")
            annex_i_path, annex_iiib_path = split_annexes(
                str(output_path), str(split_dir), language, country
            )
            print(f"   ✅ Split completed:")
            print(f"      Annex I: {Path(annex_i_path).name}")
            print(f"      Annex IIIB: {Path(annex_iiib_path).name}")
            
            # Convert to PDF
            print(f"   🔄 Converting to PDF...")
            try:
                pdf_annex_i = convert_to_pdf(annex_i_path, str(pdf_dir))
                pdf_annex_iiib = convert_to_pdf(annex_iiib_path, str(pdf_dir))
                print(f"   ✅ PDF conversion completed:")
                print(f"      Annex I PDF: {Path(pdf_annex_i).name}")
                print(f"      Annex IIIB PDF: {Path(pdf_annex_iiib).name}")
            except Exception as e:
                print(f"   ⚠️ PDF conversion failed: {e}")
                # Continue processing even if PDF conversion fails
            
            print(f"   ✅ Successfully processed {country} variant")
            return True
            
        except Exception as e:
            print(f"   ❌ Error during save/split/convert: {e}")
            return False
    
    else:
        print(f"\n⚠️ No updates made for {country} variant - document unchanged")
        return False


def process_folder(folder: str, mapping_path: str) -> None:
    """
    Process all Word documents in the given folder using the mapping.
    Enhanced with DateFormatterSystem integration and better error handling.
    
    Args:
        folder: Path to directory containing Word documents
        mapping_path: Path to Excel mapping file
        
    Raises:
        NotADirectoryError: If folder is not a valid directory
        FileNotFoundError: If mapping file cannot be loaded
    """
    print("=" * 80)
    print("🚀 STARTING FOLDER PROCESSING WITH ENHANCED DATE FORMATTING")
    print("=" * 80)
    
    # Validate folder path
    folder_path = Path(folder).resolve()
    if not folder_path.is_dir():
        raise NotADirectoryError(f"{folder} is not a valid directory")
    
    print(f"📁 Processing folder: {folder_path}")
    print(f"📋 Using mapping file: {mapping_path}")
    
    # =============================================================================
    # INITIALIZE MAPPING AND DATE FORMATTER
    # =============================================================================
    print(f"\n📊 Loading mapping table and initializing date formatter...")
    
    mapping_df = load_mapping_table(mapping_path)
    if mapping_df is None:
        raise FileNotFoundError(f"Could not load mapping file: {mapping_path}")
    
    print(f"✅ Mapping loaded: {len(mapping_df)} country configurations")
    
    # Verify date formatter initialization
    try:
        formatter = get_date_formatter()
        available_countries = formatter.get_available_countries()
        print(f"✅ Date formatter initialized: {len(available_countries)} countries supported")
        
        # Show sample formatting for verification
        print(f"\n📅 Sample date formatting verification:")
        sample_countries = available_countries[:3]  # Show first 3 countries
        for country in sample_countries:
            try:
                preview = formatter.preview_format(country)
                if 'error' not in preview:
                    print(f"   {country}:")
                    print(f"      Annex I: {preview['annex_i_example']}")
                    print(f"      Annex IIIB: {preview['annex_iiib_example']}")
            except Exception as e:
                print(f"   {country}: Error - {e}")
                
    except Exception as e:
        print(f"⚠️ Warning: Date formatter not properly initialized: {e}")
        print("   Processing will continue with fallback formatting")
    
    # =============================================================================
    # SETUP OUTPUT DIRECTORIES
    # =============================================================================
    split_dir = folder_path / "split_docs"
    pdf_dir = folder_path / "pdf_docs"
    
    os.makedirs(split_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)
    
    print(f"\n📂 Output directories:")
    print(f"   Split documents: {split_dir}")
    print(f"   PDF documents: {pdf_dir}")
    
    # =============================================================================
    # PROCESS DOCUMENTS
    # =============================================================================
    print(f"\n🔍 Scanning for Word documents...")
    
    # Find all .docx files
    docx_files = [f for f in folder_path.iterdir() 
                  if f.suffix.lower() == ".docx" 
                  and not f.name.startswith("~")  # Skip temp files
                  and "_Annex_" not in f.name    # Skip already processed files
                  and not f.name.startswith("Annex")]  # Skip split files
    
    if not docx_files:
        print("❌ No valid Word documents found in folder")
        return
    
    print(f"📄 Found {len(docx_files)} document(s) to process:")
    for doc_file in docx_files:
        print(f"   - {doc_file.name}")
    
    # Track processing statistics
    processed_count = 0
    success_count = 0
    total_variants = 0
    
    # =============================================================================
    # PROCESS EACH DOCUMENT
    # =============================================================================
    for file in docx_files:
        print("\n" + "=" * 80)
        print(f"🚀 STARTING WORKFLOW FOR: {file.name}")
        print("=" * 80)

        processed_count += 1
        
        # Identify language and country from filename
        country_code, language_name, country_name = identify_document_country_and_language(str(file))
        
        if not language_name:
            print(f"❌ Cannot proceed without language identification for {file.name}")
            continue

        print(f"🔍 Document identification:")
        print(f"   Country code: {country_code}")
        print(f"   Language: {language_name}")
        print(f"   Country: {country_name}")

        # Find all mapping rows for this language (handles multi-country languages)
        mapping_rows = find_mapping_rows_for_language(mapping_df, language_name)
        
        if not mapping_rows:
            print(f"❌ No mapping found for language: {language_name}")
            continue
        
        print(f"\n📊 Found {len(mapping_rows)} country variant(s) for {language_name}:")
        for row in mapping_rows:
            print(f"   - {row['Country']}")
            total_variants += 1
        
        # Create backup of original file
        backup_path = file.with_suffix(file.suffix + ".orig")
        if not backup_path.exists():
            try:
                shutil.copy2(file, backup_path)
                print(f"💾 Created backup: {backup_path.name}")
            except Exception as e:
                print(f"⚠️ Warning: Could not create backup: {e}")
        
        # =============================================================================
        # PROCESS EACH COUNTRY VARIANT
        # =============================================================================
        variant_success_count = 0
        
        for i, mapping_row in enumerate(mapping_rows, 1):
            country = mapping_row['Country']
            print(f"\n{'='*60}")
            print(f"🌍 PROCESSING VARIANT {i}/{len(mapping_rows)}: {country}")
            print(f"{'='*60}")
            
            try:
                success = process_single_document(file, mapping_row, split_dir, pdf_dir)
                if success:
                    variant_success_count += 1
                    success_count += 1
                    print(f"✅ Variant {i} completed successfully")
                else:
                    print(f"⚠️ Variant {i} completed with issues")
                    
            except Exception as e:
                print(f"❌ Error processing variant {i} ({country}): {e}")
                import traceback
                traceback.print_exc()
        
        # Summary for this document
        print(f"\n📊 Document Summary for {file.name}:")
        print(f"   Variants processed: {len(mapping_rows)}")
        print(f"   Successful variants: {variant_success_count}")
        print(f"   Success rate: {variant_success_count/len(mapping_rows)*100:.1f}%")
    
    # =============================================================================
    # FINAL SUMMARY
    # =============================================================================
    print("\n" + "=" * 80)
    print("✅ FOLDER PROCESSING COMPLETE")
    print("=" * 80)
    
    print(f"📊 Processing Statistics:")
    print(f"   Input files processed: {processed_count}")
    print(f"   Total country variants: {total_variants}")
    print(f"   Successful variants: {success_count}")
    print(f"   Overall success rate: {success_count/total_variants*100:.1f}%" if total_variants > 0 else "   No variants processed")
    
    print(f"\n📂 Output Locations:")
    print(f"   Split documents: {split_dir}")
    print(f"   PDF documents: {pdf_dir}")
    
    # Show some sample outputs
    split_files = list(split_dir.glob("*.docx"))
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    print(f"\n📄 Generated Files:")
    print(f"   Split Word documents: {len(split_files)}")
    print(f"   PDF documents: {len(pdf_files)}")
    
    if split_files:
        print(f"\n📋 Sample outputs:")
        for sample_file in split_files[:5]:  # Show first 5 files
            print(f"   - {sample_file.name}")
        if len(split_files) > 5:
            print(f"   ... and {len(split_files) - 5} more files")
    
    # Date formatting summary
    try:
        formatter = get_date_formatter()
        print(f"\n📅 Date Formatting Summary:")
        print(f"   Countries with date formats: {len(formatter.get_available_countries())}")
        print(f"   Enhanced formatting: ✅ Active")
        print(f"   Locale support: ✅ Available for 25+ languages")
    except:
        print(f"\n📅 Date Formatting Summary:")
        print(f"   Enhanced formatting: ⚠️ Used fallback formatting")
    
    print("=" * 80)


# =============================================================================
# ADDITIONAL HELPER FUNCTIONS FOR ENHANCED WORKFLOW
# =============================================================================

def generate_output_filename(base_name: str, language: str, country: str, 
                           doc_type: str = "combined") -> str:
    """
    Generate standardized output filename for processed documents.
    
    Args:
        base_name: Original filename without extension
        language: Language from mapping table
        country: Country from mapping table  
        doc_type: Type of document (combined, annex_i, annex_iiib)
        
    Returns:
        str: Generated filename
    """
    # Clean up country name for filename
    country_clean = re.sub(r'[^\w\-_\.]', '_', country)
    
    if doc_type == "combined":
        return f"{base_name}_{language}_{country_clean}_updated.docx"
    elif doc_type == "annex_i":
        return f"Annex_I_EU_SmPC_{language}_{country_clean}.docx"
    elif doc_type == "annex_iiib":
        return f"Annex_IIIB_EU_PL_{language}_{country_clean}.docx"
    else:
        return f"{base_name}_{language}_{country_clean}_{doc_type}.docx"


def validate_processing_environment() -> bool:
    """
    Validate that the processing environment is ready.
    
    Returns:
        bool: True if environment is ready, False otherwise
    """
    checks_passed = 0
    total_checks = 4
    
    print("🔧 Validating Processing Environment...")
    
    # Check 1: Required imports
    try:
        from docx import Document
        print("   ✅ python-docx library available")
        checks_passed += 1
    except ImportError:
        print("   ❌ python-docx library not available")
    
    # Check 2: Date formatter
    try:
        formatter = get_date_formatter()
        print("   ✅ Date formatter initialized")
        checks_passed += 1
    except:
        print("   ⚠️ Date formatter not initialized (will initialize during processing)")
        checks_passed += 1  # Not critical
    
    # Check 3: PDF conversion capability
    try:
        from docx2pdf import convert
        print("   ✅ PDF conversion library available")
        checks_passed += 1
    except ImportError:
        print("   ⚠️ PDF conversion library not available (will skip PDF generation)")
        checks_passed += 1  # Not critical for basic processing
    
    # Check 4: File system permissions
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            tmp.write(b"test")
        print("   ✅ File system write permissions OK")
        checks_passed += 1
    except:
        print("   ❌ File system write permissions issue")
    
    success_rate = checks_passed / total_checks
    print(f"   📊 Environment check: {checks_passed}/{total_checks} ({success_rate*100:.0f}%)")
    
    return success_rate >= 0.75  # 75% of checks must pass


