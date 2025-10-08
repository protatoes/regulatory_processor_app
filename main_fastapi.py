"""
FastAPI backend for EU Regulatory Document Processor.

This replaces the Reflex app with a FastAPI backend that serves
a plain HTML frontend and provides REST API endpoints for document processing.
"""

import os
import uuid
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any
import logging

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from regulatory_processor.processor import process_folder_enhanced
from regulatory_processor.config import ProcessingConfig
PROCESSOR_AVAILABLE = True
print("✅ Processor imports successful")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EU Regulatory Document Processor",
    description="Process EU SmPC documents with splitting and formatting",
    version="1.0.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory task storage (use Redis/database in production)
tasks: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def read_root():
    """Serve the main HTML page."""
    try:
        return FileResponse("static/index.html")
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Static files not found</h1><p>Please create the static/index.html file</p>",
            status_code=404
        )

# @app.get("/favicon.ico")
# async def favicon():
#     """Return a simple favicon response to avoid 404 errors."""
#     from fastapi.responses import Response
#     # Return empty response with proper headers
#     return Response(status_code=204)

@app.post("/api/process")
async def start_processing(
    background_tasks: BackgroundTasks,
    folder_path: str = Form(...),
    mapping_file: UploadFile = File(...)
):
    """
    Start document processing in the background.
    
    Args:
        folder_path: Path to folder containing Word documents
        mapping_file: Excel mapping file upload
    
    Returns:
        JSON with task_id and status
    """
    # Validate inputs
    if not folder_path or not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Invalid folder path")
    
    if not mapping_file.filename or not mapping_file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid mapping file format")
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    try:
        # Save uploaded mapping file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_mapping_path = os.path.join(temp_dir, f"{task_id}_mapping.xlsx")
        
        with open(temp_mapping_path, "wb") as f:
            content = await mapping_file.read()
            f.write(content)
        
        logger.info(f"Started processing task {task_id} for folder: {folder_path}")
        
        # Initialize task status
        tasks[task_id] = {
            "status": "started",
            "progress": 0,
            "message": "Processing started...",
            "files": [],
            "errors": []
        }
        
        # Start background processing
        background_tasks.add_task(
            process_documents_background,
            task_id,
            folder_path,
            temp_mapping_path,
            temp_dir
        )
        
        return {"task_id": task_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Error starting processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """Get the current status of a processing task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

@app.get("/api/tasks")
async def list_tasks():
    """List all tasks (for debugging)."""
    return {"tasks": list(tasks.keys()), "count": len(tasks)}

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task from memory."""
    if task_id in tasks:
        del tasks[task_id]
        return {"message": "Task deleted"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

async def process_documents_background(
    task_id: str, 
    folder_path: str, 
    mapping_path: str,
    temp_dir: str
):
    """
    Background task to process documents using the existing processor.
    
    Args:
        task_id: Unique task identifier
        folder_path: Path to documents folder
        mapping_path: Path to temporary mapping file
        temp_dir: Temporary directory to clean up
    """
    try:
        logger.info(f"Background processing started for task {task_id}")
        
        # Update status
        tasks[task_id].update({
            "status": "processing",
            "progress": 10,
            "message": "Initializing document processor..."
        })
        
        # Configure processor (skip PDF conversion for web interface)
        config = ProcessingConfig(
            convert_to_pdf=True,  # False = Skip PDF conversion to avoid LibreOffice issues
            skip_pdf_in_background=False,
            create_backups=True
        )
        
        # Update progress
        tasks[task_id].update({
            "progress": 20,
            "message": "Starting document analysis..."
        })
        
        # Run the processor in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            process_folder_enhanced,
            folder_path,
            mapping_path,
            config
        )
        
        # Update progress
        tasks[task_id]["progress"] = 90
        tasks[task_id]["message"] = "Finalizing results..."
        
        # Process results
        if result.success:
            tasks[task_id].update({
                "status": "completed",
                "progress": 100,
                "message": result.message,
                "files": result.output_files,
                "errors": getattr(result, 'errors', [])
            })
            logger.info(f"Task {task_id} completed successfully with {len(result.output_files)} files")
        else:
            tasks[task_id].update({
                "status": "failed",
                "progress": 100,
                "message": result.message,
                "files": [],
                "errors": getattr(result, 'errors', [])
            })
            logger.warning(f"Task {task_id} failed: {result.message}")
            
    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        logger.error(f"Task {task_id} error: {error_msg}")
        
        tasks[task_id].update({
            "status": "error",
            "progress": 0,
            "message": error_msg,
            "files": [],
            "errors": [str(e)]
        })
        
    finally:
        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up temporary directory for task {task_id}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp directory: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "processor_available": PROCESSOR_AVAILABLE,
        "active_tasks": len([t for t in tasks.values() if t["status"] == "processing"]),
        "total_tasks": len(tasks),
        "static_files_exist": os.path.exists("static/index.html")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
