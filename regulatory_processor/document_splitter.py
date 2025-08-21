"""Document splitting utilities for separating Annexes."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from docx import Document

from .file_manager import generate_output_filename
from .document_utils import copy_paragraph


def split_annexes(source_path: str, output_dir: str, language: str, country: str, mapping_row: pd.Series) -> Tuple[str, str]:
    """Split a combined SmPC document into Annex I and Annex IIIB documents."""
    return split_annexes_three_headers_with_fallback(source_path, output_dir, language, country, mapping_row)


def split_annexes_enhanced(source_path: str, output_dir: str, language: str, country: str, mapping_row: pd.Series) -> Tuple[str, str]:
    """Split a combined SmPC document using language-specific headers."""
    
    # Load the document
    doc = Document(source_path)
    
    # Get language-specific headers from mapping file
    annex_ii_header = str(mapping_row.get('Annex II Header in country language', '')).strip()
    annex_iiib_header = str(mapping_row.get('Annex IIIB Header in country language', '')).strip()
    
    # Validate headers are available
    if not annex_ii_header or annex_ii_header.lower() == 'nan':
        raise ValueError(f"Missing Annex II header for {country} ({language})")
    if not annex_iiib_header or annex_iiib_header.lower() == 'nan':
        raise ValueError(f"Missing Annex IIIB header for {country} ({language})")
    
    print(f"🔍 Using headers for {country} ({language}):")
    print(f"   Annex II: '{annex_ii_header}'")
    print(f"   Annex IIIB: '{annex_iiib_header}'")
    
    # Find split points by scanning all paragraphs
    annex_ii_split_index = None
    annex_iiib_split_index = None
    
    for idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        
        # Look for Annex II header
        if annex_ii_split_index is None and _is_header_match(text, annex_ii_header):
            annex_ii_split_index = idx
            print(f"✅ Found Annex II header at paragraph {idx}: '{text[:50]}...'")
        
        # Look for Annex IIIB header
        if annex_iiib_split_index is None and _is_header_match(text, annex_iiib_header):
            annex_iiib_split_index = idx
            print(f"✅ Found Annex IIIB header at paragraph {idx}: '{text[:50]}...'")
    
    # Validate that we found the required headers
    if annex_ii_split_index is None:
        raise ValueError(f"Could not find Annex II header '{annex_ii_header}' in document")
    if annex_iiib_split_index is None:
        raise ValueError(f"Could not find Annex IIIB header '{annex_iiib_header}' in document")
    
    # Ensure proper order
    if annex_ii_split_index >= annex_iiib_split_index:
        raise ValueError(f"Document structure error: Annex II (para {annex_ii_split_index}) should come before Annex IIIB (para {annex_iiib_split_index})")
    
    print(f"📊 Split points identified:")
    print(f"   Annex I: paragraphs 0 to {annex_ii_split_index - 1}")
    print(f"   Annex IIIB: paragraphs {annex_iiib_split_index} to end")
    
    # Create new documents
    annex_i_doc = Document()
    annex_iiib_doc = Document()
    
    # Split the document
    for idx, para in enumerate(doc.paragraphs):
        if idx < annex_ii_split_index:
            # Annex I content
            copy_paragraph(annex_i_doc, para)
        elif idx >= annex_iiib_split_index:
            # Annex IIIB content
            copy_paragraph(annex_iiib_doc, para)
    
    # Create country-specific subfolder
    country_safe = country.replace('/', '_').replace(' ', '_')
    country_dir = os.path.join(output_dir, country_safe)
    os.makedirs(country_dir, exist_ok=True)
    
    # Generate output paths
    base_name = Path(source_path).stem
    annex_i_filename = generate_output_filename(base_name, language, country, "annex_i")
    annex_iiib_filename = generate_output_filename(base_name, language, country, "annex_iiib")
    
    annex_i_path = os.path.join(country_dir, annex_i_filename)
    annex_iiib_path = os.path.join(country_dir, annex_iiib_filename)
    
    # Save documents
    annex_i_doc.save(annex_i_path)
    annex_iiib_doc.save(annex_iiib_path)
    
    print(f"💾 Created: {country_safe}/{annex_i_filename}")
    print(f"💾 Created: {country_safe}/{annex_iiib_filename}")
    
    return annex_i_path, annex_iiib_path


def split_annexes_three_headers_xml(source_path: str, output_dir: str, language: str, country: str, mapping_row: pd.Series) -> Tuple[str, str]:
    """Split document using all three headers with XML-based approach."""
    
    print(f"\n🔬 THREE-HEADER XML SPLITTING")
    print(f"File: {Path(source_path).name}")
    print(f"Country: {country} ({language})")
    
    # Load the document
    doc = Document(source_path)
    
    # Get all three language-specific headers
    annex_i_header = str(mapping_row.get('Annex I Header in country language', '')).strip()
    annex_ii_header = str(mapping_row.get('Annex II Header in country language', '')).strip()
    annex_iiib_header = str(mapping_row.get('Annex IIIB Header in country language', '')).strip()
    
    # Validate all headers are available
    if not annex_i_header or annex_i_header.lower() == 'nan':
        raise ValueError(f"Missing Annex I header for {country} ({language})")
    if not annex_ii_header or annex_ii_header.lower() == 'nan':
        raise ValueError(f"Missing Annex II header for {country} ({language})")
    if not annex_iiib_header or annex_iiib_header.lower() == 'nan':
        raise ValueError(f"Missing Annex IIIB header for {country} ({language})")
    
    print(f"🎯 Target headers:")
    print(f"   Annex I: '{annex_i_header}'")
    print(f"   Annex II: '{annex_ii_header}'")
    print(f"   Annex IIIB: '{annex_iiib_header}'")
    
    # Find all header positions
    header_positions = find_header_positions(doc, annex_i_header, annex_ii_header, annex_iiib_header)
    
    if header_positions['annex_i'] is None:
        raise ValueError(f"Could not find Annex I header '{annex_i_header}' in document")
    if header_positions['annex_ii'] is None:
        raise ValueError(f"Could not find Annex II header '{annex_ii_header}' in document")
    if header_positions['annex_iiib'] is None:
        raise ValueError(f"Could not find Annex IIIB header '{annex_iiib_header}' in document")
    
    # Validate header order
    validate_header_order(header_positions)
    
    print(f"✅ Header positions validated:")
    print(f"   Annex I: Paragraph {header_positions['annex_i']}")
    print(f"   Annex II: Paragraph {header_positions['annex_ii']}")
    print(f"   Annex IIIB: Paragraph {header_positions['annex_iiib']}")
    
    # Extract sections
    annex_i_doc = extract_section_xml(doc, 
                                      start_idx=header_positions['annex_i'], 
                                      end_idx=header_positions['annex_ii'])
    
    annex_iiib_doc = extract_section_xml(doc, 
                                         start_idx=header_positions['annex_iiib'], 
                                         end_idx=None)
    
    # Generate output paths
    base_name = Path(source_path).stem
    annex_i_filename = generate_output_filename(base_name, language, country, "annex_i")
    annex_iiib_filename = generate_output_filename(base_name, language, country, "annex_iiib")
    
    annex_i_path = os.path.join(output_dir, annex_i_filename)
    annex_iiib_path = os.path.join(output_dir, annex_iiib_filename)
    
    # Save documents
    annex_i_doc.save(annex_i_path)
    annex_iiib_doc.save(annex_iiib_path)
    
    print(f"💾 Created with XML preservation:")
    print(f"   {annex_i_filename}")
    print(f"   {annex_iiib_filename}")
    
    return annex_i_path, annex_iiib_path


def find_header_positions(doc: Document, annex_i_header: str, annex_ii_header: str, annex_iiib_header: str) -> Dict[str, Optional[int]]:
    """Find the paragraph positions of all three annex headers."""
    
    positions = {'annex_i': None, 'annex_ii': None, 'annex_iiib': None}
    
    # Find best match for each header
    for idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        
        # Check for Annex I header
        if positions['annex_i'] is None and _is_header_match(text, annex_i_header):
            positions['annex_i'] = idx
            print(f"✅ Found Annex I header at paragraph {idx}: '{text[:50]}...'")
        
        # Check for Annex II header
        if positions['annex_ii'] is None and _is_header_match(text, annex_ii_header):
            positions['annex_ii'] = idx
            print(f"✅ Found Annex II header at paragraph {idx}: '{text[:50]}...'")
        
        # Check for Annex IIIB header
        if positions['annex_iiib'] is None and _is_header_match(text, annex_iiib_header):
            positions['annex_iiib'] = idx
            print(f"✅ Found Annex IIIB header at paragraph {idx}: '{text[:50]}...'")
    
    return positions


def validate_header_order(positions: Dict[str, int]) -> None:
    """Validate that headers are in the correct order: I < II < IIIB."""
    
    annex_i_pos = positions['annex_i']
    annex_ii_pos = positions['annex_ii']
    annex_iiib_pos = positions['annex_iiib']
    
    if annex_i_pos >= annex_ii_pos:
        raise ValueError(f"Document structure error: Annex I (para {annex_i_pos}) should come before Annex II (para {annex_ii_pos})")
    
    if annex_ii_pos >= annex_iiib_pos:
        raise ValueError(f"Document structure error: Annex II (para {annex_ii_pos}) should come before Annex IIIB (para {annex_iiib_pos})")
    
    print(f"📊 Document structure validated:")
    print(f"   Annex I: {annex_ii_pos - annex_i_pos} paragraphs")
    print(f"   Annex II: {annex_iiib_pos - annex_ii_pos} paragraphs") 
    print(f"   Annex IIIB: Continues to end of document")


def extract_section_xml(source_doc: Document, start_idx: int, end_idx: Optional[int] = None) -> Document:
    """Extract a section from the source document using safe copying."""
    
    # Determine which paragraphs to include
    total_paragraphs = len(source_doc.paragraphs)
    actual_end_idx = end_idx if end_idx is not None else total_paragraphs
    
    print(f"📋 Extracting paragraphs {start_idx} to {actual_end_idx-1} (total: {actual_end_idx - start_idx})")
    
    # Create new document
    new_doc = Document()
    
    # Copy paragraphs safely
    for idx in range(start_idx, actual_end_idx):
        if idx < len(source_doc.paragraphs):
            copy_paragraph(new_doc, source_doc.paragraphs[idx])
    
    return new_doc


def split_annexes_three_headers_with_fallback(source_path: str, output_dir: str, language: str, country: str, mapping_row: pd.Series) -> Tuple[str, str]:
    """Main splitting function with three-header approach and fallback."""
    
    try:
        # Try the three-header XML approach first
        return split_annexes_three_headers_xml(source_path, output_dir, language, country, mapping_row)
    
    except (ValueError, KeyError) as e:
        print(f"⚠️ Three-header approach failed: {e}")
        print(f"🔄 Falling back to two-header approach...")
        
        try:
            return split_annexes_enhanced(source_path, output_dir, language, country, mapping_row)
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            raise fallback_error


def _is_header_match(paragraph_text: str, header_text: str) -> bool:
    """Check if paragraph text matches a header with flexible matching."""
    if not paragraph_text or not header_text:
        return False
    
    # Normalize both texts
    para_normalized = _normalize_text_for_matching(paragraph_text)
    header_normalized = _normalize_text_for_matching(header_text)
    
    # Exact match (most reliable)
    if para_normalized == header_normalized:
        return True
    
    # Check if paragraph contains the header as words
    if _contains_as_words(para_normalized, header_normalized):
        return True
    
    # Similar headers (fuzzy match for minor variations)
    if _are_similar_headers(para_normalized, header_normalized):
        return True
    
    return False


def _contains_as_words(text: str, search_term: str) -> bool:
    """Check if text contains search_term as complete words."""
    import re
    # Create word boundary pattern
    pattern = r'\b' + re.escape(search_term) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def _are_similar_headers(text1: str, text2: str) -> bool:
    """Check if two header texts are similar enough to be considered a match."""
    if not text1 or not text2:
        return False
    
    # Remove common prefixes/suffixes that might vary
    prefixes_to_ignore = ['annex', 'annexe', 'anexo', 'allegato', 'anhang', 'bijlage']
    suffixes_to_ignore = ['summary', 'product', 'information', 'leaflet']
    
    def clean_header(text):
        words = text.lower().split()
        # Remove common prefixes
        while words and words[0] in prefixes_to_ignore:
            words.pop(0)
        # Remove common suffixes  
        while words and words[-1] in suffixes_to_ignore:
            words.pop()
        return ' '.join(words)
    
    clean1 = clean_header(text1)
    clean2 = clean_header(text2)
    
    # Check if one is contained in the other after cleaning
    if clean1 and clean2:
        return (clean1 in clean2) or (clean2 in clean1)
    
    return False


def _normalize_text_for_matching(text: str) -> str:
    """Normalize text for consistent header matching."""
    if not text:
        return ""
    
    import re
    # Convert to lowercase
    normalized = text.lower()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Remove common punctuation that might vary
    normalized = re.sub(r'[.,;:!?]', '', normalized)
    
    # Remove Roman numerals and numbers that might be inconsistent
    normalized = re.sub(r'\b(i{1,3}v?|iv|v|vi{0,3}|ix|x)\b', '', normalized)
    normalized = re.sub(r'\b\d+\b', '', normalized)
    
    # Remove extra whitespace again after removals
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized