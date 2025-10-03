"""
Reflex web application for processing EU regulatory SmPC documents.

This module defines a Reflex application with a minimal user
interface.  The user can enter the path to a folder containing
combined SmPC Word files and the path to an Excel mapping file.  When
the "Start Processing" button is pressed, the application invokes
the processor in a background task to update, split and convert the
documents. Progress is reported via a status field on the page.
"""

import os
import asyncio
from functools import partial
import reflex as rx

# Import the processor module and its necessary classes
from . import processor

class AppState(rx.State):
    """
    Application state that uses background tasks to run the processor
    without blocking the UI and causing worker timeouts.
    """
    
    folder_path: str = ""
    mapping_path: str = ""
    status: str = "Please provide paths and start processing."
    is_processing: bool = False

    # ### PART 1: THE STARTER EVENT HANDLER ###
    # This is called when the user clicks the button. It sets the UI to a
    # loading state and immediately starts the background task.
    async def start_processing(self) -> None:
        """
        Validates inputs, sets the UI to a processing state, and
        starts the document processing in a background task.
        """
        # Prevent starting a new process if one is already running
        if self.is_processing:
            return

        # Validate inputs
        folder = os.path.expanduser(self.folder_path.strip())
        mapping = os.path.expanduser(self.mapping_path.strip())
        
        if not folder or not os.path.isdir(folder):
            self.status = "Error: The folder path is invalid or does not exist."
            return
        
        if not mapping or not os.path.isfile(mapping):
            self.status = "Error: The mapping file path is invalid or does not exist."
            return
        
        # Set the UI to a loading state
        self.is_processing = True
        self.status = "Processing... this may take several minutes. Please do not close this window."
        
        # Kick off the background task
        return AppState.run_processing_background

    # ### PART 2: THE BACKGROUND TASK ###
    # Decorated with @rx.event(background=True), this runs on a separate thread.
    # It contains the slow, blocking call to your processor.
    @rx.event(background=True)
    async def run_processing_background(self) -> None:
        """
        Runs the heavy document processing logic in the background.
        This function does not block the main app thread and yields control
        to the Reflex event loop using asyncio.run_in_executor.
        """
        # Use 'async with self' to get a clean instance of the state
        async with self:
            folder = os.path.expanduser(self.folder_path.strip())
            mapping = os.path.expanduser(self.mapping_path.strip())

        # Update status to show we're starting
        async with self:
            self.status = "Initializing document processing..."

        try:
            # Create processing configuration - skip PDF conversion in executor
            config = processor.ProcessingConfig(
                create_backups=True,
                convert_to_pdf=True,
                skip_pdf_in_background=True,  # Skip PDF to avoid ThreadPoolExecutor deadlock
                log_level="INFO"
            )

            # Update status before starting main processing
            async with self:
                self.status = "Processing documents (this may take several minutes)..."

            # Run document processing in executor (no PDF conversion happens here)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,  # Use default ThreadPoolExecutor
                partial(processor.process_folder_enhanced, folder, mapping, config)
            )

            # PDF conversion happens HERE - outside the executor
            if result.success and result.pending_pdf_conversions:
                async with self:
                    self.status = f"Converting {len(result.pending_pdf_conversions)} documents to PDF..."

                # Run conversions outside executor context
                pdf_results = await self._convert_pdfs_outside_executor(result.pending_pdf_conversions)
                result.output_files.extend(pdf_results)

        except Exception as e:
            # If the processor crashes, create an error result to show the user
            result = processor.ProcessingResult(
                success=False,
                message="A fatal error occurred during processing.",
                errors=[str(e)]
            )

        # Update state directly in the background task - no need to yield to another handler
        async with self:
            self.is_processing = False
            if result.success:
                output_count = len(result.output_files)
                pdf_count = len([f for f in result.output_files if f.endswith('.pdf')])
                self.status = (
                    f"✅ Processing completed successfully! "
                    f"Created {output_count} files ({pdf_count} PDFs)."
                )
            else:
                self.status = f"❌ Processing failed: {result.message}"
                if result.errors:
                    error_summary = "; ".join(result.errors[:2])
                    self.status += f" Details: {error_summary}"

    async def _convert_pdfs_outside_executor(self, conversions) -> list:
        """Run PDF conversions outside executor in async context."""
        pdf_files = []

        for doc_path, output_dir in conversions:
            # Run in executor but as individual calls, not nested inside document processing
            loop = asyncio.get_event_loop()
            try:
                pdf_path = await loop.run_in_executor(
                    None,
                    processor.convert_to_pdf,
                    doc_path,
                    output_dir
                )
                pdf_files.append(pdf_path)
            except Exception as e:
                print(f"PDF conversion failed for {doc_path}: {e}")

        return pdf_files

def index() -> rx.Component:
    """The main user interface for the document processor."""
    return rx.center(
        rx.vstack(
            rx.heading(
                "EU Regulatory Document Processor",
                font_size="1.5em",
            ),
            rx.text(
                "Enter the absolute path to the folder containing the combined SmPC Word files:",
            ),
            rx.input(
                placeholder="/path/to/smpc/files",
                on_change=AppState.set_folder_path,
                width="100%",
            ),
            rx.text("Enter the absolute path to the Excel mapping file:"),
            rx.input(
                placeholder="/path/to/Mapping Test.xlsx",
                on_change=AppState.set_mapping_path,
                width="100%",
            ),
            rx.button(
                "Start Processing",
                # The on_click now calls our "starter" event handler
                on_click=AppState.start_processing,
                # The button is disabled while processing is in progress
                is_disabled=AppState.is_processing,
                width="100%",
                color_scheme="teal",
            ),
            # Use a box with a border for the status to make it stand out
            rx.box(
                rx.text(AppState.status),
                margin_top="1em",
                padding="1em",
                border="1px solid #ddd",
                border_radius="md",
                width="100%",
                bg="#461010",
            ),
            width="600px",
            align="start",
            spacing="3",
        ),
        padding="2em",
    )

# Create the Reflex application
# Timeout is configured in rxconfig.py instead of here
app = rx.App()
app.add_page(index, title="Document Processor")