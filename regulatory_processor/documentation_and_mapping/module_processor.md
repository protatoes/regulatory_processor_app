# Module Documentation: processor.py

## Overview
Core document processing module containing the main orchestration logic for EU SmPC and PL document processing. This module handles document updates, splitting, and PDF conversion with comprehensive error handling and logging.

**File Size**: 3,054 lines
**Key Features**: Document processing orchestration, content updates, document splitting, PDF conversion, background task support

## Classes

### ThreadSafePDFConverter (Singleton)
**Purpose**: Thread-safe PDF conversion handler using LibreOffice
**Design Pattern**: Singleton with thread-safe initialization
**Key Features**:
- Serializes PDF conversions to avoid LibreOffice conflicts
- Uses queue-based processing in dedicated thread
- Handles LibreOffice installation detection

### FileManager
**Purpose**: Handles file operations and path management

#### Methods:
- `__init__(base_folder: Path, config: ProcessingConfig)`
- `setup_output_directories() -> Tuple[Path, Path]` - Creates split_docs and pdf_docs directories
- `discover_processable_documents() -> List[Path]` - Finds valid .docx files for processing
- `_is_processable_document(file_path: Path) -> bool` - Validates if file should be processed
- `create_backup(file_path: Path) -> Optional[Path]` - Creates .orig backup files

**Input Filtering**:
- Accepts: `.docx` files
- Excludes: Temp files (`~*`), existing annex files, files with annex markers

### DocumentUpdater
**Purpose**: Handles document modification operations

#### apply_all_updates()
**Inputs**:
- `doc: Document` - Document to modify
- `mapping_row: pd.Series` - Country/language configuration
- `mapping_file_path: Optional[str]` - Path to Excel mapping

**Outputs**: `Tuple[bool, List[str]]` - (success_flag, list_of_updates_applied)

**Update Chain**:
1. **National reporting systems** → `update_document_with_fixed_smpc_blocks()`
2. **Annex I dates** → `update_section_10_date()`
3. **Annex IIIB dates** → `update_annex_iiib_date()`
4. **Local representatives** → `update_local_representatives()`

### DocumentProcessor (Main Orchestrator)
**Purpose**: Main document processing orchestrator with comprehensive workflow management

#### Constructor
**Inputs**: `config: Optional[ProcessingConfig] = None`
**Outputs**: Initialized processor instance
**Features**: Auto-configures logging, initializes statistics tracking

#### process_folder()
**Inputs**:
- `folder_path: str` - Path to folder containing documents
- `mapping_path: str` - Path to Excel mapping file

**Outputs**: `ProcessingResult` - Complete processing results with statistics

**Processing Flow**:
1. **Validation Phase**
   - `_validate_folder_path()` - Ensures directory exists
   - `_load_and_validate_mapping()` - Loads Excel mapping file
   - `initialize_date_formatter()` - Sets up country-specific date formatting

2. **Setup Phase**
   - Creates FileManager instance
   - Sets up output directories (split_docs, pdf_docs)
   - Discovers processable documents

3. **Document Processing Loop**
   - For each document: `_process_single_document()`
   - Language/country identification
   - Mapping row lookup
   - Backup creation
   - Variant processing for multi-country languages

4. **Post-Processing**
   - Batch PDF conversion (if enabled and not in background)
   - Statistics compilation
   - Final result generation

#### _process_single_document()
**Purpose**: Process one document with all its country variants
**Inputs**:
- `document_path: Path`
- `mapping_df: pd.DataFrame`
- `file_manager: FileManager`
- `split_dir: Path`
- `pdf_dir: Path`
- `mapping_path: str`

**Flow**:
1. Document identification using filename analysis
2. Mapping row discovery for language
3. Backup creation
4. Variant processing loop
5. Success rate calculation and reporting

#### _process_document_variant()
**Purpose**: Process single country variant of a document
**Inputs**:
- `document_path: Path`
- `mapping_row: pd.Series`
- `split_dir: Path`
- `pdf_dir: Path`
- `mapping_path: str`

**Flow**:
1. Document loading via `docx.Document()`
2. Content updates via `DocumentUpdater.apply_all_updates()`
3. Document saving and splitting via `_save_and_split_document()`

#### _save_and_split_document() (Async)
**Purpose**: Save updated document and split into separate annexes
**Async Design**: Prevents blocking during file operations

**Flow**:
1. Generate output filename using `generate_output_filename()`
2. Save combined document
3. Split into annexes using `split_annexes()`
4. Queue for PDF conversion (batch processing)
5. Update statistics and return results

#### _batch_convert_pdfs()
**Purpose**: Convert all pending Word documents to PDF after main processing
**Inputs**: `pdf_dir: Path`
**Outputs**: `List[str]` - List of created PDF file paths

**Features**:
- Processes queued conversions from `_pending_pdf_conversions`
- Error handling for individual failures
- Success/failure statistics tracking
- Detailed logging of conversion results

## Major Content Update Functions

### update_document_with_fixed_smpc_blocks()
**Purpose**: Updates national reporting systems in SmPC Section 4.8 and PL Section 4
**Inputs**: `doc: Document`, `mapping_row: pd.Series`
**Outputs**: `Tuple[bool, List[str]]` - (success, list_of_sections_updated)

**Algorithm**:
- Locates target sections using text pattern matching
- Removes gray-shaded and hyperlinked text (old reporting info)
- Inserts new country-specific reporting blocks with hyperlinks
- Handles both SmPC and PL sections with different text patterns

### update_section_10_date()
**Purpose**: Updates dates in Annex I Section 10
**Inputs**: `doc: Document`, `mapping_row: pd.Series`, `mapping_file_path: Optional[str]`
**Outputs**: `bool` - Success flag

**Flow**:
1. Locates Section 10 header using mapping data
2. Finds insertion point after header
3. Formats date using `format_date_for_country()`
4. Inserts formatted date with proper formatting

### update_annex_iiib_date()
**Purpose**: Updates dates in Annex IIIB Section 6
**Similar to update_section_10_date but targets Annex IIIB sections**

### update_local_representatives()
**Purpose**: Updates local representative information in Annex IIIB Section 6
**Inputs**: `doc: Document`, `mapping_row: pd.Series`
**Outputs**: `bool` - Success flag

**Processing Chain**:
1. Calls `filter_local_representatives()`
2. Attempts table processing first (NEW: `LocalRepTableProcessor`)
3. Falls back to paragraph processing if table method fails
4. Returns combined success status

## Document Splitting Functions

### split_annexes()
**Purpose**: Wrapper function for document splitting using modern clone-and-prune approach
**Inputs**: `source_path: str`, `output_dir: str`, `language: str`, `country: str`, `mapping_row: pd.Series`
**Outputs**: `Tuple[str, str]` - (annex_i_path, annex_iiib_path)

**Implementation**: Delegates to `document_splitter.clone_and_split_document()`

## PDF Conversion Functions

### convert_to_pdf()
**Purpose**: Convert Word document to PDF using multiple fallback methods
**Inputs**: `doc_path: str`, `output_dir: str`
**Outputs**: `str` - Path to created PDF file

**Conversion Methods** (in order of preference):
1. **LibreOffice** (`soffice --headless`) - Primary method
2. **docx2pdf** - Python library fallback
3. **Pandoc** - Alternative converter
4. **Placeholder creation** - Final fallback (creates .txt file indicating failure)

**Known Issues**: All PDF conversion methods currently failing consistently

## Utility Functions

### Content Detection Functions
- `is_run_gray_shaded()` - Detects gray-shaded text runs
- `is_run_hyperlink()` - Detects hyperlinked text runs
- `find_target_text_runs()` - Locates specific text patterns
- `find_runs_to_remove()` - Identifies runs for removal

### Text Processing Functions
- `build_replacement_text_by_country()` - Creates country-specific replacement text
- `get_replacement_components()` - Extracts mapping data for text replacement
- `insert_formatted_replacement_surgically()` - Inserts new content with formatting

### Header Processing Functions
- `_find_section_10_header()` - Locates Section 10 headers
- `_insert_date_after_header()` - Inserts dates after section headers
- `is_header_match()` - Flexible header text matching

## Entry Point Functions

### process_folder() (Legacy)
**Purpose**: Backwards compatible entry point
**Inputs**: `folder: str`, `mapping_path: str`
**Outputs**: None (logs results)
**Behavior**: Maintains original interface while using enhanced system

### process_folder_enhanced()
**Purpose**: Modern entry point with detailed result reporting
**Inputs**: `folder: str`, `mapping_path: str`, `config: Optional[ProcessingConfig]`
**Outputs**: `ProcessingResult` - Detailed success/failure information

## Error Handling Strategy

### Exception Types
- **ValidationError**: Input validation failures
- **MappingError**: Excel mapping file problems
- **DocumentError**: Word document manipulation issues
- **ProcessingError**: General processing failures

### Recovery Mechanisms
- Individual document failure doesn't stop batch processing
- Graceful degradation for PDF conversion failures
- Comprehensive logging for troubleshooting
- Backup creation before processing

## Performance Characteristics

### Async Support
- `_save_and_split_document()` is async to prevent UI blocking
- Batch PDF conversion after main processing
- Memory-efficient document handling

### Background Processing Support
- PDF conversion can be disabled in background contexts
- Prevents LibreOffice conflicts in threading environments
- Real-time status updates through logging

## Integration Points

1. **Entry Point**: `process_folder_enhanced()` called from `regulatory_processor.py`
2. **Document Updates**: `DocumentUpdater.apply_all_updates()` coordinates all content changes
3. **Document Splitting**: Integrates with `document_splitter.py` for modern splitting
4. **Date Formatting**: Uses `date_formatter.py` for country-specific date formatting
5. **Utilities**: Leverages `utils.py` for file operations and text processing
6. **Hyperlinks**: Integrates `hyperlinks.py` for URL validation and hyperlink creation
7. **Local Representatives**: Uses `local_rep_table_processor.py` for table-based processing

## Legacy/Redundant Functions

### Potentially Redundant
- `split_annexes_original()` - **LEGACY**: Old splitting implementation, kept for fallback
- `debug_three_header_structure()` - **DEBUG**: Development function, could be removed
- `_is_header_match()` - **DUPLICATE**: Functionality exists in `utils.py`
- `_contains_as_words()` - **DUPLICATE**: Functionality exists in `utils.py`
- `_are_similar_headers()` - **DUPLICATE**: Functionality exists in `utils.py`
- `_normalize_text_for_matching()` - **DUPLICATE**: Functionality exists in `utils.py`

### Header Processing Duplicates
Several header processing functions in this module duplicate functionality from `utils.py`. These should be consolidated to use the centralized implementations.

## Key Design Decisions

1. **Class-Based Architecture**: Separation of concerns with FileManager, DocumentUpdater, DocumentProcessor
2. **Async Support**: Background task compatibility without blocking UI
3. **Batch Processing**: PDF conversion separated from main processing for performance
4. **Comprehensive Logging**: Detailed progress tracking and error reporting
5. **Graceful Degradation**: Processing continues even when individual components fail
6. **Configuration-Driven**: Behavior controlled through ProcessingConfig
7. **Statistics Tracking**: Detailed metrics for success rates and performance analysis