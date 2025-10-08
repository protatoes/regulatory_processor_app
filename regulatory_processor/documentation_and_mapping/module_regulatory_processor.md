# Module Documentation: regulatory_processor.py

## Overview
Main Reflex web application module that provides the user interface and orchestrates background document processing. This module serves as the entry point for the entire regulatory document processing workflow.

## Classes and Functions

### AppState Class (extends rx.State)
**Purpose**: Manages application state for the Reflex web interface and coordinates background processing tasks.

**State Variables**:
- `folder_path: str = ""` - User-provided path to folder containing SmPC documents
- `mapping_path: str = ""` - User-provided path to Excel mapping file
- `status: str = "Please provide paths and start processing."` - Current processing status message
- `is_processing: bool = False` - Flag indicating if processing is currently running

#### start_processing()
**Purpose**: Validates user inputs and initiates background document processing
**Inputs**: None (uses self state variables)
**Outputs**: `AppState.run_processing_background` (background task trigger)
**Flow**:
1. Prevents multiple concurrent processes
2. Validates folder_path exists and is directory
3. Validates mapping_path exists and is file
4. Sets UI to processing state
5. Triggers background task

**Error Handling**: Updates status with validation error messages

#### run_processing_background()
**Purpose**: Main background processing orchestrator that prevents worker timeouts
**Decorator**: `@rx.event(background=True)` - Runs on separate thread
**Inputs**: None (uses self state variables)
**Outputs**: None (updates UI state)
**Flow**:
1. Document discovery in target folder
2. Iterative processing of each document
3. Real-time status updates via async context
4. Success/failure tracking and reporting
5. Final result aggregation

**Key Features**:
- Uses `asyncio.sleep(0.1)` to yield control between documents
- Processes one document at a time to prevent timeouts
- Comprehensive error handling with traceback logging
- Real-time UI updates using `async with self:`

#### _process_single_document()
**Purpose**: Process one complete document using existing processor logic
**Inputs**:
- `doc_path: str` - Path to document to process
- `mapping_path: str` - Path to mapping file
- `base_folder: str` - Base folder for output organization
**Outputs**: `processor.ProcessingResult` - Processing result with success/failure info
**Flow**:
1. Creates temporary directory for isolated processing
2. Copies document to temp directory
3. Configures ProcessingConfig (PDF conversion disabled in background)
4. Calls `processor.process_folder_enhanced()`
5. Moves output files to final locations in base folder
6. Returns ProcessingResult

**File Organization**:
- Combined documents → base folder
- Split documents (Annex I/IIIB) → `split_docs/` subfolder

### index() Function
**Purpose**: Defines the main UI layout for the Reflex application
**Inputs**: None
**Outputs**: `rx.Component` - Reflex UI component tree
**UI Elements**:
- Application title heading
- Folder path input field
- Mapping file path input field
- Start Processing button (disabled during processing)
- Status display box with styling

### app Initialization
**Purpose**: Creates and configures the Reflex application
**Components**:
- `app = rx.App()` - Main application instance
- `app.add_page(index, title="Document Processor")` - Adds main page

## Dependencies
- `reflex as rx` - Web framework for UI and state management
- `asyncio` - Asynchronous processing support
- `tempfile, shutil` - File system operations
- `os, pathlib.Path` - Path handling
- `processor` - Core document processing module
- `config.ProcessingConfig` - Configuration management

## Integration Points
1. **Entry Point**: User interaction triggers `start_processing()`
2. **Background Orchestration**: `run_processing_background()` manages workflow
3. **Document Processing**: Delegates to `processor.process_folder_enhanced()`
4. **UI Updates**: Real-time status updates during processing
5. **File Organization**: Manages output file placement and organization

## Error Handling Strategy
- **Input Validation**: Pre-flight checks for paths and file existence
- **Background Processing**: Exception catching with detailed logging
- **UI Feedback**: Clear error messages displayed to user
- **Graceful Degradation**: Processing continues even if individual documents fail

## Performance Characteristics
- **Background Threading**: Prevents UI blocking during processing
- **Incremental Processing**: One document at a time with control yielding
- **Memory Management**: Temporary directories for isolated processing
- **PDF Conversion**: Disabled in background to avoid LibreOffice issues

## Key Design Decisions
1. **Reflex Framework**: Chosen for Python-native web UI development
2. **Background Tasks**: Prevents worker timeouts and UI freezing
3. **Incremental Processing**: Balances throughput with responsiveness
4. **File Isolation**: Temporary directories prevent conflicts
5. **Status Updates**: Real-time feedback improves user experience