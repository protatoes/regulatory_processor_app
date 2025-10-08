# EU Regulatory Document Processor - FastAPI Version

This is a FastAPI-based web application for processing EU SmPC (Summary of Product Characteristics) documents. It replaces the original Reflex implementation with a more traditional web architecture using FastAPI backend and plain HTML/CSS/JavaScript frontend.

## Features

- **File Upload Interface**: Upload Excel mapping files directly through the web interface
- **Real-time Progress**: Live status updates and progress tracking
- **Background Processing**: Long-running document processing without blocking the UI
- **Modern UI**: Clean, responsive design with progress indicators
- **Error Handling**: Comprehensive error reporting and validation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI Server

```bash
# Using uvicorn directly
uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main_fastapi.py
```

### 3. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

1. **Enter Folder Path**: Provide the absolute path to the folder containing your combined SmPC Word documents
2. **Upload Mapping File**: Select and upload your Excel mapping configuration file (.xlsx or .xls)
3. **Start Processing**: Click the "Start Processing" button to begin
4. **Monitor Progress**: Watch real-time progress updates and status messages
5. **View Results**: See the list of generated files when processing completes

## API Endpoints

The FastAPI backend provides several REST endpoints:

- `GET /` - Serve the main HTML interface
- `POST /api/process` - Start document processing
- `GET /api/status/{task_id}` - Get processing status
- `GET /api/tasks` - List all tasks (debugging)
- `DELETE /api/tasks/{task_id}` - Delete a task
- `GET /health` - Health check endpoint

## Architecture

### Backend (FastAPI)
- **main_fastapi.py**: Main FastAPI application with API endpoints
- **Background Tasks**: Uses FastAPI's BackgroundTasks for async processing
- **File Upload**: Handles Excel file uploads with validation
- **Status Tracking**: In-memory task status tracking (use Redis in production)

### Frontend (Plain HTML/CSS/JS)
- **static/index.html**: Main user interface
- **static/style.css**: Modern CSS with responsive design
- **static/app.js**: JavaScript for form handling and real-time updates

### Document Processing
- Uses the existing `regulatory_processor` module unchanged
- Processes documents in background threads to avoid blocking
- Skips PDF conversion by default (can be enabled)

## Configuration

The processor can be configured by modifying the `ProcessingConfig` in `main_fastapi.py`:

```python
config = ProcessingConfig(
    convert_to_pdf=False,  # Skip PDF conversion for web interface
    skip_pdf_in_background=True,
    create_backups=True
)
```

## Development

### Running in Development Mode

```bash
uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables automatic reloading when code changes.

### File Structure

```
regulatory_processor_app/
├── main_fastapi.py           # FastAPI backend
├── static/                   # Frontend assets
│   ├── index.html           # Main UI
│   ├── style.css            # Styling
│   └── app.js               # JavaScript logic
├── regulatory_processor/     # Document processing module (unchanged)
├── requirements.txt          # Dependencies
└── README_FASTAPI.md        # This file
```

## Differences from Reflex Version

### Advantages of FastAPI Version:
1. **Separation of Concerns**: Clear API boundaries between frontend and backend
2. **File Upload**: Proper file upload handling instead of file paths
3. **Frontend Flexibility**: Can easily switch to React, Vue, or other frameworks
4. **API Reusability**: Other applications can consume the same API
5. **Production Ready**: Better suited for containerization and cloud deployment
6. **Standard Web Technologies**: Uses familiar HTML/CSS/JavaScript

### Migration Notes:
- The core document processing logic remains unchanged
- Background task handling is similar but uses FastAPI's system
- File upload replaces the file path input from Reflex version
- Status polling provides real-time updates similar to Reflex

## Production Deployment

For production deployment, consider:

1. **Task Storage**: Replace in-memory task storage with Redis or database
2. **File Storage**: Use proper file storage service for uploaded files
3. **Security**: Add authentication and input validation
4. **Monitoring**: Add logging and monitoring
5. **Scaling**: Use multiple workers and load balancing

Example production command:
```bash
uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 --workers 4
```

## Troubleshooting

### Common Issues:

1. **Port Already in Use**: Change the port number in the uvicorn command
2. **File Upload Errors**: Check file permissions and disk space
3. **Processing Timeouts**: Increase timeout settings for large documents
4. **Static Files Not Loading**: Ensure the `static/` directory exists and contains all files

### Logs:

The application logs to the console. For production, configure proper logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Support

For issues related to:
- **Document Processing**: Check the original `regulatory_processor` module documentation
- **Web Interface**: Check browser console for JavaScript errors
- **API Issues**: Check FastAPI logs and use `/health` endpoint for diagnostics
