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

import reflex as rx  # type: ignore

from . import processor


class AppState(rx.State):
    """Application state for the document processor.

    Attributes
    ----------
    folder_path : str
        The path entered by the user pointing to the directory of
        combined SmPC Word files.
    mapping_path : str
        The path to the Excel mapping file.
    status : str
        A status message displayed to the user describing the
        progress or result of the processing.
    """

    folder_path: str = ""
    mapping_path: str = ""
    status: str = ""

    async def run_processing(self) -> None:
        """Asynchronously process the files when the button is clicked.

        This method uses the helper functions defined in
        ``processor.py`` to perform the heavy lifting.  It updates
        the status field before and after processing to provide
        feedback to the user.  Any exceptions are caught and the
        status is updated with an error message.
        """
        # Trim surrounding whitespace and expand user home symbols
        folder = os.path.expanduser(self.folder_path.strip())
        mapping = os.path.expanduser(self.mapping_path.strip())
        if not folder or not mapping:
            self.status = "Please provide both folder and mapping paths."
            return
        self.status = "Processing... this may take a few minutes"
        # Yield control back to the event loop so the status update
        # propagates to the client.  Without this yield the status
        # would not appear until after processing completes.
        yield
        try:
            processor.process_folder(folder, mapping)
            self.status = (
                f"Processing completed. Updated documents saved in {folder}."
            )
        except Exception as exc:
            # Catch all exceptions and display the error message
            self.status = f"Error: {exc}"
        # Final yield ensures the last status update is sent
        yield


def index() -> rx.Component:
    """Build the index page of the application.

    The page is laid out as a vertical stack of elements.  It
    contains a heading, two input fields for folder and mapping
    paths, a button to start processing, and a text element to
    display the status.  The input fields update the corresponding
    state attributes via their ``on_change`` handlers, and the
    button triggers the asynchronous ``run_processing`` event.

    Returns
    -------
    rx.Component
        A Reflex component representing the page.
    """
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
            # Display the status message.  Reflex vars cannot be used directly
            # in a Python `if` expression, so we avoid conditional colour
            # logic here.  If desired, use `rx.cond` to choose styles based
            # on state at a later time.
            rx.text(
                AppState.status,
                # Display the status below the button.  We specify only
                # margin and font style here – no conditional styling is
                # applied.  See the comments above for guidance on
                # adding conditional colours via ``rx.cond`` should
                # that be desired.
                margin_top="1em",
                font_style="italic",
            ),
            width="600px",
            align="start",
            # Use a valid spacing token (0–9) instead of arbitrary CSS units.
            # See Radix UI docs for accepted values.  The original value
            # "0.5em" caused a TypeError during compilation.
            spacing="3",
        ),
        padding="2em",
    )


# Create the Reflex application and register the page.
app = rx.App()
app.add_page(index, title="Document Processor")
# NOTE:
# In recent versions of Reflex the CLI (`reflex run`) is responsible for
# compiling the app automatically.  Calling `app.compile()` here leads to
# an AttributeError because `App.compile` was removed.  See the CLI
# documentation for details on project compilation【338122900162100†L69-L96】.