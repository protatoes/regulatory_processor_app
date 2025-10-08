# Module Documentation: utils.py

## Overview
Core utility functions module providing country/language mapping, file operations, text processing, and mapping table utilities. This module contains foundational functions used throughout the application.

**File Size**: 243 lines
**Key Features**: Country code mapping, filename analysis, text normalization, Excel mapping utilities, header matching

## Country and Language Mapping

### get_country_code_mapping()
**Purpose**: Returns mapping of two-letter ISO codes to (language, country) tuples
**Inputs**: None
**Outputs**: `Dict[str, Tuple[str, str]]` - Mapping of codes to (language, country)

**Coverage**: 33 European countries/languages including:
- Standard EU languages: English, German, French, Spanish, Italian
- Nordic languages: Swedish, Finnish, Norwegian, Danish, Icelandic
- Eastern European: Polish, Czech, Slovak, Hungarian, Romanian, Bulgarian
- Baltic: Estonian, Latvian, Lithuanian
- Other: Dutch, Portuguese, Greek, Maltese, Croatian, Slovenian

### extract_country_code_from_filename()
**Purpose**: Extract two-letter country code from SmPC filename
**Inputs**: `file_path: str` - Path to document file
**Outputs**: `Optional[str]` - Lowercase country code or None

**Pattern Matching**: `ema-combined-h-\d+-([a-z]{2})`
**Example**: `"ema-combined-h-123-en.docx"` → `"en"`

### identify_document_country_and_language()
**Purpose**: Identify both country and language from document filename
**Inputs**: `file_path: str` - Path to document file
**Outputs**: `Tuple[Optional[str], Optional[str], Optional[str]]` - (country_code, language_name, country_name)

**Flow**:
1. Extract country code using `extract_country_code_from_filename()`
2. Look up language and country using `get_country_code_mapping()`
3. Return tuple of results

### find_mapping_rows_for_language()
**Purpose**: Find all mapping rows for a given language (handles multi-country languages)
**Inputs**:
- `mapping_df: pd.DataFrame` - Excel mapping data
- `language_name: str` - Target language name
**Outputs**: `List[pd.Series]` - List of matching mapping rows

**Use Case**: Languages like English may have multiple countries (Ireland, Malta)

## File Naming and Path Utilities

### generate_output_filename()
**Purpose**: Generate compliant filenames according to specifications
**Inputs**:
- `base_name: str` - Original filename base
- `language: str` - Language name
- `country: str` - Country name (handles "/" and spaces)
- `doc_type: str` - Document type identifier

**Outputs**: `str` - Properly formatted filename

**Filename Patterns**:
- `"combined"` → `"{base_name}_{country_clean}.docx"`
- `"annex_i"` → `"Annex_I_EU_SmPC_{language}_{country_clean}.docx"`
- `"annex_iiib"` → `"Annex_IIIB_EU_PL_{language}_{country_clean}.docx"`
- Other → `"{base_name}_{doc_type}.docx"`

**Country Cleaning**: Replaces "/" and spaces with underscores for filesystem compatibility

## Mapping Table Utilities

### load_mapping_table()
**Purpose**: Load Excel mapping table with error handling and validation
**Inputs**: `file_path: str` - Path to Excel file
**Outputs**: `Optional[pd.DataFrame]` - Loaded DataFrame or None on error

**Features**:
- File existence validation
- Excel loading with pandas
- Comprehensive error reporting
- Success logging with row/column counts

**Error Handling**: Returns None and logs errors instead of raising exceptions

## Text Normalization Utilities

### normalize_text_for_matching()
**Purpose**: Normalize text for header matching by removing inconsistencies
**Inputs**: `text: str` - Raw text to normalize
**Outputs**: `str` - Normalized text for comparison

**Normalization Steps**:
1. Convert to lowercase
2. Remove extra whitespace (multiple spaces → single space)
3. Remove punctuation: `. , ; : ! ? " ' " " ( )`
4. Remove formatting artifacts: `\r \n \t`
5. Final whitespace cleanup

### contains_as_words()
**Purpose**: Check if search term exists as complete words, not substrings
**Inputs**:
- `text: str` - Text to search in
- `search_term: str` - Term to find
**Outputs**: `bool` - True if found as complete words

**Algorithm**: Uses regex word boundaries (`\b`) to ensure complete word matching
**Example**: "Annex I" matches "ANNEX I text" but not "ANNEX III text"

### are_similar_headers()
**Purpose**: Check if two texts are similar annex headers that could be confused
**Inputs**:
- `text1: str` - First header text
- `text2: str` - Second header text
**Outputs**: `bool` - True if headers are similar and could cause confusion

**Comprehensive Annex Detection**:
- **Base Words**: bijlage, annexe, anhang, lisa, παραρτημα, pielikums, priedas, anexo, prilog, priloga, liite, bilaga, allegato, annex, anness, bilag, viðauki, vedlegg, příloha, aneks, príloha, приложение, melléklet, anexa
- **Roman Numerals**: `[ivx]+`, `[ιυχ]+` (Greek), `\d+` (Arabic backup)

**Pattern Matching**:
- Word first: "ANNEXE I", "BIJLAGE II"
- Number first: "I LISA", "II LISA"
- Period format: "I. MELLÉKLET"

### is_header_match()
**Purpose**: Check if paragraph text matches a header with precise word-boundary matching
**Inputs**:
- `paragraph_text: str` - Text from document paragraph
- `header_text: str` - Target header text
**Outputs**: `bool` - True if texts match

**Matching Algorithm**:
1. Normalize both texts using `normalize_text_for_matching()`
2. Check exact match after normalization
3. Check if header is contained in paragraph (word boundaries)
4. Prevent false matches between similar headers
5. Check if paragraph starts with header + space

## Section Identification Utilities

### is_section_header()
**Purpose**: Check if text appears to be a section header
**Inputs**: `text: str` - Text to analyze
**Outputs**: `bool` - True if appears to be section header

**Pattern Recognition**:
- Numbered sections: `"7."`, `"8."`
- Named sections: `"section 7"`, `"section 8"`

### contains_country_local_rep_entry()
**Purpose**: Check if paragraph contains a country-specific local representative entry
**Inputs**: `text: str` - Paragraph text to check
**Outputs**: `bool` - True if contains country entry pattern

**Pattern**: Country name at start of line followed by colon (e.g., `"Germany:"`, `"France:"`)

### should_keep_local_rep_entry()
**Purpose**: Determine if a local representative entry should be kept based on target country
**Inputs**:
- `para_text: str` - Paragraph text
- `target_country: str` - Country to filter for
- `applicable_reps: str` - Applicable representatives (unused in current implementation)
**Outputs**: `bool` - True if paragraph should be kept

**Algorithm**: Simple case-insensitive substring matching

## Dependencies
- `os` - File path operations
- `re` - Regular expression matching
- `pathlib.Path` - Modern path handling
- `pandas as pd` - Excel file processing
- `typing` - Type hints for better code documentation
- `.config.ProcessingConfig` - Configuration management
- `.exceptions.ValidationError` - Custom exception handling

## Integration Points
1. **Filename Analysis**: Used by processor for document identification
2. **Text Processing**: Header matching functions used throughout document processing
3. **Mapping Operations**: Excel loading used by all processing workflows
4. **File Naming**: Output filename generation used in document splitting
5. **Text Normalization**: Used by document splitter for header boundary detection

## Performance Characteristics
- **Country Mapping**: O(1) dictionary lookups for 33 countries
- **Text Normalization**: Efficient regex-based processing
- **Filename Parsing**: Single regex pattern for quick extraction
- **Excel Loading**: Leverages pandas optimized Excel reading

## Error Handling Strategy
- **Graceful Degradation**: Functions return None/False instead of raising exceptions
- **Logging Integration**: Error messages logged for debugging
- **Input Validation**: Comprehensive checking of file paths and data
- **Type Safety**: Optional return types for functions that may fail

## Usage Patterns

### Document Processing Flow
1. `extract_country_code_from_filename()` → identify document
2. `get_country_code_mapping()` → resolve language/country
3. `find_mapping_rows_for_language()` → get processing configurations
4. `generate_output_filename()` → create output filenames

### Text Processing Flow
1. `normalize_text_for_matching()` → prepare text for comparison
2. `contains_as_words()` → precise text matching
3. `is_header_match()` → validate header matches
4. `are_similar_headers()` → prevent false matches

### Mapping Operations
1. `load_mapping_table()` → load Excel configuration
2. `find_mapping_rows_for_language()` → filter relevant data
3. Process each mapping row for multi-country languages