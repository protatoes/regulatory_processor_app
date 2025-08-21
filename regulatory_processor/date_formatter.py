"""Date formatting system for regulatory documents."""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


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