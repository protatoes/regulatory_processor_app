"""Hyperlink creation and URL validation utilities."""

import logging
import re
import urllib.parse
from typing import Dict, List, Optional

import requests
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.shared import RGBColor
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from .config import URLValidationConfig, URLValidationResult, URLAccessibilityResult


# =============================================================================
# URL VALIDATION
# =============================================================================

def validate_url_format(url: str) -> URLValidationResult:
    """
    Validate URL format and return detailed validation results.

    Supports http/https/mailto protocols as required by the manual process.
    Handles edge cases like missing protocols and malformed URLs.
    """
    if not url or not isinstance(url, str):
        return URLValidationResult(
            is_valid=False,
            url=url or "",
            protocol="",
            error_message="URL is empty or not a string"
        )

    # Clean up the URL
    cleaned_url = url.strip()
    if not cleaned_url:
        return URLValidationResult(
            is_valid=False,
            url=url,
            protocol="",
            error_message="URL is empty after cleaning"
        )

    # Check for mailto links
    if cleaned_url.lower().startswith('mailto:'):
        return _validate_mailto_url(cleaned_url)

    # Check for web URLs
    if cleaned_url.lower().startswith(('http://', 'https://')):
        return _validate_web_url(cleaned_url)

    # Try to auto-detect and fix common issues
    return _auto_fix_url_format(cleaned_url)


def _validate_mailto_url(url: str) -> URLValidationResult:
    """Validate mailto URL format."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme.lower() != 'mailto':
            return URLValidationResult(
                is_valid=False,
                url=url,
                protocol="mailto",
                error_message="Invalid mailto scheme"
            )

        # Basic email validation
        email_part = parsed.path
        if not email_part or '@' not in email_part:
            return URLValidationResult(
                is_valid=False,
                url=url,
                protocol="mailto",
                error_message="Invalid email address in mailto URL"
            )

        # Simple email regex validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email_part):
            return URLValidationResult(
                is_valid=False,
                url=url,
                protocol="mailto",
                error_message=f"Invalid email format: {email_part}"
            )

        return URLValidationResult(
            is_valid=True,
            url=url,
            protocol="mailto",
            normalized_url=url.lower()
        )

    except Exception as e:
        return URLValidationResult(
            is_valid=False,
            url=url,
            protocol="mailto",
            error_message=f"Error parsing mailto URL: {str(e)}"
        )


def _validate_web_url(url: str) -> URLValidationResult:
    """Validate web URL format (http/https)."""
    try:
        parsed = urllib.parse.urlparse(url)

        if parsed.scheme.lower() not in ('http', 'https'):
            return URLValidationResult(
                is_valid=False,
                url=url,
                protocol=parsed.scheme or "unknown",
                error_message=f"Unsupported protocol: {parsed.scheme}"
            )

        if not parsed.netloc:
            return URLValidationResult(
                is_valid=False,
                url=url,
                protocol=parsed.scheme,
                error_message="Missing domain name"
            )

        # Check for valid domain format
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, parsed.netloc.split(':')[0]):  # Remove port if present
            return URLValidationResult(
                is_valid=False,
                url=url,
                protocol=parsed.scheme,
                error_message=f"Invalid domain format: {parsed.netloc}"
            )

        return URLValidationResult(
            is_valid=True,
            url=url,
            protocol=parsed.scheme,
            normalized_url=url
        )

    except Exception as e:
        return URLValidationResult(
            is_valid=False,
            url=url,
            protocol="unknown",
            error_message=f"Error parsing web URL: {str(e)}"
        )


def _auto_fix_url_format(url: str) -> URLValidationResult:
    """Attempt to auto-fix common URL format issues."""
    # Check if it looks like an email address
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, url):
        fixed_url = f"mailto:{url}"
        return _validate_mailto_url(fixed_url)

    # Check if it looks like a website (contains domain-like structure)
    web_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    if re.match(web_pattern, url):
        # Try https first (more secure)
        fixed_url = f"https://{url}"
        result = _validate_web_url(fixed_url)
        if result.is_valid:
            result.normalized_url = fixed_url
            return result

        # Fallback to http
        fixed_url = f"http://{url}"
        result = _validate_web_url(fixed_url)
        if result.is_valid:
            result.normalized_url = fixed_url
            return result

    # Unable to auto-fix
    return URLValidationResult(
        is_valid=False,
        url=url,
        protocol="unknown",
        error_message=f"Unable to determine URL format. Expected http://, https://, or mailto: format"
    )


def validate_urls_batch(urls: List[str]) -> Dict[str, URLValidationResult]:
    """Validate multiple URLs in batch and return results."""
    results = {}
    for url in urls:
        results[url] = validate_url_format(url)
    return results


# =============================================================================
# URL ACCESSIBILITY TESTING
# =============================================================================

def test_url_accessibility(url: str, timeout: int = 5, allow_redirects: bool = True) -> URLAccessibilityResult:
    """Test if a URL is accessible via HTTP request."""
    # Skip accessibility testing for mailto URLs
    if url.lower().startswith('mailto:'):
        return URLAccessibilityResult(
            is_accessible=True,  # Assume mailto is accessible if format is valid
            url=url,
            status_code=None,
            error_message="Mailto URLs are not tested for accessibility"
        )

    try:
        import time
        start_time = time.time()

        # Make HTTP request
        response = requests.head(url, timeout=timeout, allow_redirects=allow_redirects)

        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)

        # Check if request was successful
        is_accessible = response.status_code < 400

        result = URLAccessibilityResult(
            is_accessible=is_accessible,
            url=url,
            status_code=response.status_code,
            response_time_ms=response_time_ms
        )

        # Check for redirects
        if response.history:
            result.redirect_url = response.url

        if not is_accessible:
            result.error_message = f"HTTP {response.status_code}: {response.reason}"

        return result

    except requests.exceptions.Timeout:
        return URLAccessibilityResult(
            is_accessible=False,
            url=url,
            error_message=f"Request timed out after {timeout} seconds"
        )

    except requests.exceptions.ConnectionError as e:
        return URLAccessibilityResult(
            is_accessible=False,
            url=url,
            error_message=f"Connection error: {str(e)}"
        )

    except requests.exceptions.RequestException as e:
        return URLAccessibilityResult(
            is_accessible=False,
            url=url,
            error_message=f"Request failed: {str(e)}"
        )

    except Exception as e:
        return URLAccessibilityResult(
            is_accessible=False,
            url=url,
            error_message=f"Unexpected error: {str(e)}"
        )


def test_urls_accessibility_batch(urls: List[str], timeout: int = 5,
                                max_concurrent: int = 5) -> Dict[str, URLAccessibilityResult]:
    """Test multiple URLs for accessibility in batch with optional concurrency."""
    results = {}

    # For now, implement sequential testing (can be enhanced with threading later)
    for url in urls:
        results[url] = test_url_accessibility(url, timeout)

    return results


def validate_and_test_url_complete(url: str, config: URLValidationConfig = None) -> tuple[URLValidationResult, Optional[URLAccessibilityResult]]:
    """Complete URL validation including both format and accessibility testing."""
    if config is None:
        config = URLValidationConfig()

    # Step 1: Format validation (always enabled)
    format_result = validate_url_format(url) if config.enable_format_validation else None

    # Step 2: Accessibility testing (optional)
    accessibility_result = None
    if config.enable_accessibility_testing and format_result and format_result.is_valid:
        test_url = format_result.normalized_url or format_result.url
        accessibility_result = test_url_accessibility(test_url, config.accessibility_timeout)

    return format_result, accessibility_result


# =============================================================================
# DOCUMENT RELATIONSHIP MANAGEMENT
# =============================================================================

def add_hyperlink_relationship(document: Document, url: str) -> str:
    """Add a hyperlink relationship to the document and return the relationship ID."""
    try:
        # Access the document part
        document_part = document.part

        # Create the relationship for external hyperlink
        relationship = document_part.relate_to(
            url,
            RELATIONSHIP_TYPE.HYPERLINK,
            is_external=True
        )

        # Handle different types of relationship returns
        if hasattr(relationship, 'rId'):
            return relationship.rId
        elif isinstance(relationship, str):
            return relationship
        else:
            # Fallback: try to get the rId from the document's relationships
            for rel_id, rel in document_part.rels.items():
                if rel.target_ref == url and rel.reltype == RELATIONSHIP_TYPE.HYPERLINK:
                    return rel_id

            raise Exception("Could not determine relationship ID")

    except Exception as e:
        raise Exception(f"Failed to create hyperlink relationship for '{url}': {str(e)}")


def get_document_relationships(document: Document) -> Dict[str, str]:
    """Get all hyperlink relationships from a document."""
    try:
        relationships = {}
        document_part = document.part

        for rel_id, relationship in document_part.rels.items():
            if relationship.reltype == RELATIONSHIP_TYPE.HYPERLINK:
                relationships[rel_id] = relationship.target_ref

        return relationships

    except Exception as e:
        logging.warning(f"Failed to get document relationships: {e}")
        return {}


# =============================================================================
# HYPERLINK CREATION
# =============================================================================

def create_hyperlink_element(para: Paragraph, text: str, url: str, document: Document) -> OxmlElement:
    """Creates and returns a w:hyperlink OxmlElement without appending it."""
    try:
        # Step 1: Validate URL
        format_result = validate_url_format(url)
        if not format_result.is_valid:
            raise Exception(f"Invalid URL format: {format_result.error_message}")
        final_url = format_result.normalized_url or format_result.url

        # Step 2: Create document relationship
        rel_id = add_hyperlink_relationship(document, final_url)

        # Step 3: Create hyperlink XML element
        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), rel_id)

        # Step 4: Create run within hyperlink
        run_element = OxmlElement('w:r')
        run_props = OxmlElement('w:rPr')

        # Add hyperlink styling (blue color, underline)
        color = OxmlElement('w:color')
        color.set(qn('w:val'), '0000FF')
        run_props.append(color)

        underline = OxmlElement('w:u')
        underline.set(qn('w:val'), 'single')
        run_props.append(underline)

        run_element.append(run_props)

        # Add text content
        text_element = OxmlElement('w:t')
        text_element.text = text
        run_element.append(text_element)

        hyperlink.append(run_element)

        return hyperlink

    except Exception as e:
        logging.warning(f"Hyperlink element creation failed for '{url}': {e}. Falling back.")
        # Return a styled run element instead
        return create_styled_text_fallback_element(text)


def create_styled_text_fallback_element(text: str) -> OxmlElement:
    """Creates and returns a styled w:r (run) element as a fallback."""
    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')

    # Add blue color
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '0000FF')
    rPr.append(color)

    # Add underline
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)

    run.append(rPr)

    # Add text
    t = OxmlElement('w:t')
    t.text = text
    run.append(t)

    return run


def create_hyperlink_run_enhanced(para: Paragraph, text: str, url: str,
                                 validate_url: bool = True,
                                 config: URLValidationConfig = None,
                                 document: Document = None) -> Run:
    """Create a proper hyperlink run in the paragraph using correct Word relationships."""
    try:
        # Step 1: Validate URL format if requested
        if validate_url:
            if config is None:
                config = URLValidationConfig()

            format_result = validate_url_format(url)
            if not format_result.is_valid:
                raise Exception(f"Invalid URL format: {format_result.error_message}")

            # Use normalized URL if available (auto-fixed)
            final_url = format_result.normalized_url or format_result.url
        else:
            final_url = url

        # Step 2: Get document object
        if document is None:
            raise Exception("Document parameter is required for hyperlink creation")

        # Step 3: Create document relationship
        rel_id = add_hyperlink_relationship(document, final_url)

        # Step 4: Create hyperlink XML element with proper relationship reference
        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), rel_id)  # Use relationship ID, not anchor!

        # Step 5: Create run within hyperlink
        run_element = OxmlElement('w:r')
        run_props = OxmlElement('w:rPr')

        # Add hyperlink styling (blue color, underline)
        color = OxmlElement('w:color')
        color.set(qn('w:val'), '0000FF')
        run_props.append(color)

        underline = OxmlElement('w:u')
        underline.set(qn('w:val'), 'single')
        run_props.append(underline)

        run_element.append(run_props)

        # Add text content
        text_element = OxmlElement('w:t')
        text_element.text = text
        run_element.append(text_element)

        hyperlink.append(run_element)

        # Step 6: Insert hyperlink into paragraph
        para._p.append(hyperlink)

        # Step 7: Return Run object
        return Run(run_element, para)

    except Exception as e:
        # Fallback to styled text if hyperlink creation fails
        logging.warning(f"Hyperlink creation failed for '{url}': {e}. Falling back to styled text.")
        return create_styled_text_fallback(para, text)


def create_styled_text_fallback(para: Paragraph, text: str) -> Run:
    """Create styled text as fallback when hyperlink creation fails."""
    run = para.add_run(text)
    run.font.color.rgb = RGBColor(0, 0, 255)  # Blue color
    run.underline = True
    return run


# Backwards compatibility wrapper
def create_hyperlink_run(para: Paragraph, text: str, url: str) -> Run:
    """Legacy function that now uses the enhanced hyperlink creation."""
    # Since we can't get the document from just a paragraph in the legacy interface,
    # we'll fall back to styled text for backwards compatibility
    logging.warning(f"Legacy hyperlink function used for '{url}'. Falling back to styled text. Use create_hyperlink_run_enhanced() with document parameter for proper hyperlinks.")
    return create_styled_text_fallback(para, text)