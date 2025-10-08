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
import tempfile
import shutil
from functools import partial
from pathlib import Path
import reflex as rx

# Import the processor module and its necessary classes
from . import processor
from .config import ProcessingConfig

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
    # Uses existing tested processor with simple incremental processing.
    @rx.event(background=True)
    async def run_processing_background(self) -> None:
        """
        Simple incremental processing - one document at a time using existing processor.
        Yields control between documents to prevent worker timeouts.
        """
        async with self:
            folder = os.path.expanduser(self.folder_path.strip())
            mapping = os.path.expanduser(self.mapping_path.strip())

        # Validate inputs
        if not os.path.isdir(folder):
            async with self:
                self.status = "❌ Error: Invalid folder path"
                self.is_processing = False
            return

        if not os.path.isfile(mapping):
            async with self:
                self.status = "❌ Error: Invalid mapping file"
                self.is_processing = False
            return

        async with self:
            self.status = "🔍 Discovering documents..."

        try:
            # Document discovery
            docs_folder = Path(folder)
            documents = [
                f for f in docs_folder.iterdir()
                if f.suffix.lower() == '.docx'
                and not f.name.startswith('~')
                and 'Annex' not in f.name
            ]

            if not documents:
                async with self:
                    self.status = "❌ No valid documents found"
                    self.is_processing = False
                return

            async with self:
                self.status = f"📄 Found {len(documents)} document(s). Starting processing..."

            # Process each document using existing processor
            total_docs = len(documents)
            successful = 0
            all_output_files = []

            for idx, doc_path in enumerate(documents, 1):
                async with self:
                    self.status = f"📝 Processing document {idx}/{total_docs}: {doc_path.name}..."

                try:
                    # Process entire document in one executor call using existing processor
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        self._process_single_document,
                        str(doc_path),
                        mapping,
                        folder
                    )

                    if result.success:
                        successful += 1
                        all_output_files.extend(result.output_files)
                        async with self:
                            self.status = f"✅ Document {idx}/{total_docs} completed: {len(result.output_files)} files created"
                    else:
                        async with self:
                            self.status = f"⚠️ Document {idx}/{total_docs} failed: {result.message}"

                except Exception as e:
                    async with self:
                        self.status = f"❌ Error processing {doc_path.name}: {str(e)}"
                    print(f"Error processing {doc_path.name}: {e}")
                    import traceback
                    traceback.print_exc()

                # Yield control to prevent worker timeout
                await asyncio.sleep(0.1)

            # Final status
            async with self:
                self.is_processing = False
                if successful == total_docs:
                    self.status = f"✅ All {total_docs} document(s) processed successfully! Created {len(all_output_files)} files."
                elif successful > 0:
                    self.status = f"⚠️ Processed {successful}/{total_docs} document(s) successfully. Created {len(all_output_files)} files."
                else:
                    self.status = f"❌ Processing failed for all {total_docs} document(s)."

        except Exception as e:
            async with self:
                self.is_processing = False
                self.status = f"❌ Fatal error: {str(e)}"
            print(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()

    def _process_single_document(self, doc_path: str, mapping_path: str, base_folder: str) -> processor.ProcessingResult:
        """
        Process one complete document using existing tested processor code.
        This function runs in the executor thread and uses existing processor logic.
        """
        try:
            # Create a temporary folder for processing this single document
            import tempfile
            import shutil

            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy document to temp directory
                temp_doc_path = os.path.join(temp_dir, os.path.basename(doc_path))
                shutil.copy2(doc_path, temp_doc_path)

                # Configure processor to skip PDF conversion in background to avoid issues
                config = ProcessingConfig(
                    convert_to_pdf=False,  # Skip PDF conversion to avoid LibreOffice issues in background
                    skip_pdf_in_background=True,
                )

                # Process using existing tested processor code
                result = processor.process_folder_enhanced(temp_dir, mapping_path, config)

                if result.success and result.output_files:
                    # Move output files to final location
                    final_output_files = []

                    # Create output directories in base folder
                    base_path = Path(base_folder)
                    split_dir = base_path / 'split_docs'
                    split_dir.mkdir(exist_ok=True)

                    for temp_file in result.output_files:
                        if os.path.exists(temp_file):
                            # Determine final location based on file type
                            file_name = os.path.basename(temp_file)

                            if 'Annex I' in file_name or 'Annex IIIB' in file_name:
                                # Split documents go to split_docs folder
                                final_path = split_dir / file_name
                            else:
                                # Combined documents go to base folder
                                final_path = base_path / file_name

                            # Copy to final location
                            shutil.copy2(temp_file, str(final_path))
                            final_output_files.append(str(final_path))

                    return processor.ProcessingResult(
                        success=True,
                        message=f"Successfully processed {os.path.basename(doc_path)}",
                        output_files=final_output_files
                    )
                else:
                    return processor.ProcessingResult(
                        success=False,
                        message=f"Processing failed for {os.path.basename(doc_path)}: {result.message}",
                        errors=result.errors if hasattr(result, 'errors') else []
                    )

        except Exception as e:
            return processor.ProcessingResult(
                success=False,
                message=f"Error processing {os.path.basename(doc_path)}: {str(e)}",
                errors=[str(e)]
            )


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