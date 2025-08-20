"""
Reflex web application for processing EU regulatory SmPC documents.

This module defines a Reflex application with a minimal user
interface.  The user can enter the path to a folder containing
combined SmPC Word files and the path to an Excel mapping file.  When
the "Start Processing" button is pressed, the application invokes
``processor.process_folder`` to update, split and convert the
documents.  Progress is reported via a status field on the page.

Reflex apps consist of two main parts: a state class that manages
all of the server‑side state and events, and one or more page
functions that build the HTML structure.  The state class must
subclass ``rx.State`` and can define asynchronous methods that are
called when the user interacts with the UI.

For more information on how to build Reflex applications, refer to
the official documentation.  The installation instructions at
``reflex.dev`` explain how to use ``pip`` to install the framework
and how to initialise a new project using ``reflex init``【338122900162100†L69-L96】.

"""


import os
from pathlib import Path
import reflex as rx

from . import processor


class AppState(rx.State):
    """Enhanced application state with better status reporting."""
    
    folder_path: str = ""
    mapping_path: str = ""
    status: str = ""

    async def run_processing(self) -> None:
        """Enhanced processing with better error reporting."""
        # Validate inputs
        folder = os.path.expanduser(self.folder_path.strip())
        mapping = os.path.expanduser(self.mapping_path.strip())
        
        if not folder or not mapping:
            self.status = "Please provide both folder and mapping paths."
            return
        
        # Start processing
        self.status = "Processing... this may take a few minutes"
        yield
        
        try:
            # Use enhanced processor if available, fallback to original
            if hasattr(processor, 'process_folder_enhanced'):
                # Enhanced processing with detailed results
                config = processor.ProcessingConfig(
                    create_backups=True,
                    convert_to_pdf=True,
                    log_level="INFO"
                )
                
                result = processor.process_folder_enhanced(folder, mapping, config)
                
                if result.success:
                    # Extract statistics from result
                    output_count = len(result.output_files)
                    self.status = (
                        f"Processing completed successfully! "
                        f"Created {output_count} output files. "
                        f"Updated documents saved in {folder}."
                    )
                else:
                    self.status = f"Processing completed with issues: {result.message}"
                    if result.errors:
                        error_summary = "; ".join(result.errors[:2])  # Show first 2 errors
                        self.status += f" Errors: {error_summary}"
            else:
                # Fallback to original processor
                processor.process_folder(folder, mapping)
                self.status = f"Processing completed. Updated documents saved in {folder}."
                
        except Exception as exc:
            self.status = f"Error: {exc}"
        
        yield


def index() -> rx.Component:
    """Compatible UI that works with current Reflex version."""
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
                value=AppState.folder_path,
                on_change=AppState.set_folder_path,
                width="100%",
            ),
            rx.text("Enter the absolute path to the Excel mapping file:"),
            rx.input(
                placeholder="/path/to/Mapping Test.xlsx",
                value=AppState.mapping_path,
                on_change=AppState.set_mapping_path,
                width="100%",
            ),
            rx.button(
                "Start Processing",
                on_click=AppState.run_processing,
                width="100%",
                color_scheme="teal",
            ),
            rx.text(
                AppState.status,
                margin_top="1em",
                font_style="italic",
            ),
            width="600px",
            align="start",
            spacing="3",
        ),
        padding="2em",
    )


# Create the Reflex application
app = rx.App()
app.add_page(index, title="Document Processor")