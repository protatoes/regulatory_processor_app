"""Date formatting system for regulatory documents."""

import locale
import re
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd


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
        """Create a mapping between countries and their locale codes."""
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
        """Get the month name in the appropriate language and case for the country."""
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
        """Parse a custom format string and return the formatted date."""
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
        """Format a date according to the country's specified format for the given annex."""
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
        """Preview how dates will be formatted for a country."""
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


# =============================================================================
# GLOBAL DATE FORMATTER MANAGEMENT
# =============================================================================

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
    """Format a date using the enhanced DateFormatterSystem."""
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