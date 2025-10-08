# Module Documentation: date_formatter.py

## Overview
Date formatting system for regulatory documents providing country-specific date formatting with locale-aware month names and custom static text. This module handles complex date formatting requirements for different European countries and languages.

**File Size**: 247 lines
**Key Features**: Country-specific date formatting, locale support, custom format parsing, global formatter management

## Main Class

### DateFormatterSystem
**Purpose**: Core date formatting system with country-specific format support
**Design**: Instance-based with mapping file initialization

#### Constructor
**Inputs**: `mapping_file_path: str` - Path to Excel mapping file
**Initialization Flow**:
1. Load mapping data with `pd.read_excel()`
2. Extract country formats via `_load_country_formats()`
3. Create locale mapping via `_create_locale_mapping()`

#### _load_country_formats()
**Purpose**: Extract date formats from mapping table for each country
**Inputs**: None (uses self.mapping_df)
**Outputs**: `Dict[str, Dict[str, str]]` - Nested dictionary of country→annex_type→format

**Structure**:
```python
{
    'Ireland/Malta': {
        'annex_i': 'dd month yyyy',
        'annex_iiib': 'month yyyy'
    },
    'Germany/Österreich': {
        'annex_i': 'dd. MMM yyyy',
        'annex_iiib': 'MMM yyyy'
    }
}
```

#### _create_locale_mapping()
**Purpose**: Create mapping between countries and their locale codes for month name localization
**Inputs**: None
**Outputs**: `Dict[str, str]` - Country name to locale code mapping

**Supported Locales** (24 countries):
- Western Europe: `nl_NL.UTF-8`, `fr_FR.UTF-8`, `de_DE.UTF-8`, `it_IT.UTF-8`, `es_ES.UTF-8`, `pt_PT.UTF-8`
- Nordic: `sv_SE.UTF-8`, `fi_FI.UTF-8`, `da_DK.UTF-8`, `is_IS.UTF-8`, `no_NO.UTF-8`
- Eastern Europe: `cs_CZ.UTF-8`, `pl_PL.UTF-8`, `sk_SK.UTF-8`, `bg_BG.UTF-8`, `hu_HU.UTF-8`, `ro_RO.UTF-8`
- Baltic: `et_EE.UTF-8`, `lv_LV.UTF-8`, `lt_LT.UTF-8`
- Mediterranean: `el_GR.UTF-8`, `mt_MT.UTF-8`, `hr_HR.UTF-8`, `sl_SI.UTF-8`
- Ireland/Malta: `en_IE.UTF-8`

#### _get_month_name()
**Purpose**: Get month name in appropriate language and case for the country
**Inputs**:
- `date: datetime` - Date to get month name for
- `country: str` - Country for locale selection
- `format_type: str` - Format string containing case information

**Outputs**: `str` - Localized month name

**Month Format Handling**:
- `'Month'` (capital M) → Full month name (`'January'`)
- `'MMM'` → Three-letter abbreviation (`'Jan'`)
- `'month'` (lowercase) → Lowercase full name (`'january'`)

**Locale Handling**:
1. Attempts to set country-specific locale
2. Falls back to English (`en_US.UTF-8`) if locale unavailable
3. Provides hardcoded English fallback if all locale operations fail

#### _parse_custom_format()
**Purpose**: Parse custom format string and return formatted date
**Inputs**:
- `date: datetime` - Date to format
- `format_string: str` - Custom format specification
- `country: str` - Country for locale context

**Outputs**: `str` - Formatted date string

**Format Patterns**:
- `yyyy` → 4-digit year (`2024`)
- `Month/month/MMM` → Localized month name (various cases)
- `mm/MM` → 2-digit month number (`01`, `02`, etc.)
- `dd` → 2-digit day (`01`, `02`, etc.)
- `d.` → Single digit day with period (`1.`, `2.`, etc.)

**Processing Order**: Year → Month → Numeric month → Day (prevents conflicts)

#### format_date()
**Purpose**: Main formatting function for country-specific date formatting
**Inputs**:
- `date: datetime` - Date to format
- `country: str` - Target country
- `annex_type: str` - Either 'annex_i' or 'annex_iiib'

**Outputs**: `str` - Formatted date string

**Validation**:
- Validates country exists in mapping
- Validates annex_type is supported
- Raises `ValueError` for invalid inputs

#### Utility Methods
- `get_available_countries() -> List[str]` - List all supported countries
- `get_country_formats(country: str) -> Dict[str, str]` - Get both formats for a country
- `preview_format(country: str, sample_date: datetime = None) -> Dict[str, str]` - Preview formatting with sample date

## Global Date Formatter Management

### Global State
- `_date_formatter: Optional[DateFormatterSystem] = None` - Global formatter instance

### initialize_date_formatter()
**Purpose**: Initialize the global date formatter with mapping file
**Inputs**: `mapping_file_path: str` - Path to Excel mapping file
**Outputs**: `DateFormatterSystem` - Initialized formatter instance
**Side Effects**: Sets global `_date_formatter` variable

### get_date_formatter()
**Purpose**: Get the global date formatter instance
**Inputs**: None
**Outputs**: `DateFormatterSystem` - Global formatter instance
**Raises**: `RuntimeError` if formatter not initialized

### format_date_for_country()
**Purpose**: Format date using the global formatter system
**Inputs**:
- `country: str` - Target country
- `annex_type: str` - Document annex type
- `date: Optional[datetime] = None` - Date to format (defaults to now)

**Outputs**: `str` - Formatted date string

**Error Handling**:
- Catches all exceptions during formatting
- Logs errors with detailed information
- Falls back to simple format: `date.strftime("%d %B %Y")`

## Legacy Functions

### format_date() (LEGACY)
**Purpose**: Legacy date formatting function for backward compatibility
**Status**: **DEPRECATED** - Use `format_date_for_country()` instead
**Inputs**: `date_format_str: str` - Format specification string
**Outputs**: `str` - Formatted current date

**Supported Legacy Formats**:
- `"dd month yyyy"` → `"01 January 2024"`
- `"month yyyy"` → `"January 2024"`
- `"Month yyyy"` → `"January 2024"`
- `"dd. MMM yyyy"` → `"01. Jan 2024"`
- `"MMM yyyy"` → `"Jan 2024"`
- `"dd/mm/yyyy"` → `"01/01/2024"`
- `"dd.mm.yyyy"` → `"01.01.2024"`
- Default → `"01 January 2024"`

**Issues with Legacy Function**:
- No country-specific localization
- Fixed to current date only
- No locale support for month names
- Limited format options

## Dependencies
- `locale` - System locale management for month names
- `re` - Regular expression pattern matching for format parsing
- `datetime` - Date object handling
- `typing` - Type hints for better code documentation
- `pandas as pd` - Excel file processing

## Integration Points
1. **Initialization**: Called by `processor.py` during setup phase
2. **Document Updates**: Used by date update functions in `processor.py`
3. **Global Access**: Available throughout application via global formatter
4. **Configuration**: Reads date formats from Excel mapping file

## Error Handling Strategy

### Locale Fallbacks
1. **Primary**: Country-specific locale (e.g., `de_DE.UTF-8`)
2. **Secondary**: English locale (`en_US.UTF-8`)
3. **Tertiary**: Hardcoded English month names

### Format Parsing
- **Graceful Degradation**: Returns empty string for invalid formats
- **Pattern Flexibility**: Handles various format variations
- **Order Sensitivity**: Processes patterns in specific order to prevent conflicts

### Global Formatter
- **Initialization Check**: Raises clear error if formatter not initialized
- **Exception Handling**: Catches and logs all formatting errors
- **Fallback Formatting**: Provides simple fallback when advanced formatting fails

## Usage Patterns

### Initialization (once per application run)
```python
initialize_date_formatter('/path/to/mapping.xlsx')
```

### Direct Usage
```python
formatter = get_date_formatter()
formatted = formatter.format_date(datetime.now(), 'Ireland/Malta', 'annex_i')
```

### Convenience Function
```python
formatted = format_date_for_country('Germany/Österreich', 'annex_iiib')
```

## Locale Requirements
**System Dependencies**: Requires system locale support for non-English month names
**Fallback Strategy**: Gracefully degrades to English if locales unavailable
**Supported Languages**: 24+ European language locales

## Custom Format Examples

### German Format
- Input: `"dd. MMM yyyy"` with German locale
- Output: `"15. Jan 2024"`

### French Format
- Input: `"dd month yyyy"` with French locale
- Output: `"15 janvier 2024"`

### English Format
- Input: `"month yyyy"` with English locale
- Output: `"January 2024"`

## Performance Characteristics
- **Initialization**: One-time Excel loading and processing
- **Formatting**: Fast regex-based pattern replacement
- **Locale Setting**: May be slow on first call per country
- **Caching**: Global formatter instance prevents repeated initialization