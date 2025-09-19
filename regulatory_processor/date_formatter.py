"""Date formatting system for regulatory documents."""

import locale
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd


class DateFormatterSystem:
    """
    A system for formatting dates based on country-specific formats defined in a mapping table.
    Supports locale-specific month names and custom static text.
    """

    def __init__(self, mapping_source: Union[str, Path, pd.DataFrame]):
        """
        Initialize the date formatter with a mapping file.

        Args:
            mapping_source: Path to the Excel mapping file or a dataframe instance
        """
        if isinstance(mapping_source, (str, Path)):
            self.mapping_df = pd.read_excel(mapping_source)
        else:
            self.mapping_df = mapping_source.copy()
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

        Supports complex patterns including:
        - Basic: dd month yyyy, dd Month yyyy, dd. MMM yyyy
        - Numeric: mm/yyyy, MM/YYYY, dd/mm/yyyy
        - Language-specific: yyyy. gada dd. month (Latvian), dd de month de yyyy (Spanish)
        - Complex: yyyy m. month dd d. (Lithuanian), yyyy. month

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

        # Handle year formats first
        result = re.sub(r'YYYY', str(date.year), result)  # Handle uppercase YYYY
        result = re.sub(r'yyyy', str(date.year), result)

        # Handle month formats (do this before day to avoid conflicts)
        month_name = self._get_month_name(date, country, format_string)

        # Replace month patterns - order matters!
        result = re.sub(r'Month', month_name.capitalize(), result)  # Capitalized month
        result = re.sub(r'month', month_name.lower(), result)       # Lowercase month
        result = re.sub(r'MMM', date.strftime('%b'), result)        # 3-letter abbreviation

        # Handle numeric month formats - simplified to avoid regex conflicts
        result = re.sub(r'MM', f"{date.month:02d}", result)         # MM (uppercase)
        result = re.sub(r'mm', f"{date.month:02d}", result)         # mm (lowercase)

        # Handle day formats - simplified patterns that work reliably
        result = re.sub(r'dd', f"{date.day:02d}", result)           # dd → 12

        # Handle single day patterns with word boundaries (tested and working)
        result = re.sub(r'\bd\.', f"{date.day}.", result)          # d. → 12.
        result = re.sub(r'\bd\b', str(date.day), result)           # d → 12 (at word boundary)

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

    def get_available_countries(self) -> List[str]:
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


# Global date formatter instance
_date_formatter: Optional[DateFormatterSystem] = None


def initialize_date_formatter(
    mapping_source: Union[str, Path, pd.DataFrame]
) -> DateFormatterSystem:
    """Initialize the global date formatter."""
    global _date_formatter
    _date_formatter = DateFormatterSystem(mapping_source)
    return _date_formatter


def get_date_formatter() -> DateFormatterSystem:
    """Get the global date formatter instance."""
    global _date_formatter
    if _date_formatter is None:
        raise RuntimeError("Date formatter not initialized")
    return _date_formatter


def format_date_for_country(country: str, annex_type: str, date: Optional[datetime] = None) -> str:
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