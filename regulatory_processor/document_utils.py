"""Document processing utilities for manipulating Word documents."""

from typing import Dict, List, Optional, Tuple
import pandas as pd
from docx import Document
from docx.document import Document as DocumentObject
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.shared import RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from .date_formatter import format_date_for_country


def copy_paragraph(dest_doc: Document, source_para: Paragraph) -> None:
    """Copy a paragraph from one document to another, preserving runs."""
    new_para = dest_doc.add_paragraph()
    new_para.style = source_para.style
    for run in source_para.runs:
        new_run = new_para.add_run(run.text)
        new_run.bold = run.bold
        new_run.italic = run.italic
        new_run.underline = run.underline
        new_run.style = run.style


def is_hex_gray_color(hex_color: str) -> bool:
    """Check if a hex color represents a gray shade."""
    if not hex_color:
        return False
    
    hex_color = hex_color.replace('#', '').upper()
    
    gray_hex_values = [
        'BFBFBF', 'CCCCCC', 'D9D9D9', '808080', '999999', 
        '666666', 'C0C0C0', 'A0A0A0'
    ]
    
    if hex_color in gray_hex_values:
        return True
    
    # Check if R=G=B (indicates gray)
    try:
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return r == g == b
    except ValueError:
        pass
    
    return False


def is_run_gray_shaded(run: Run) -> bool:
    """Check if a run has gray shading."""
    try:
        run_pr = run._element.get_or_add_rPr()
        shading_elements = run_pr.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
        
        if shading_elements:
            for shading in shading_elements:
                fill = shading.get(qn('w:fill'))
                if fill and is_hex_gray_color(fill):
                    return True
        
        # Check font color for gray
        if run.font.color and hasattr(run.font.color, 'rgb'):
            gray_colors = [
                RGBColor(128, 128, 128), RGBColor(153, 153, 153), 
                RGBColor(102, 102, 102), RGBColor(96, 96, 96),
                RGBColor(217, 217, 217), RGBColor(191, 191, 191)
            ]
            if run.font.color.rgb in gray_colors:
                return True
                
    except Exception:
        pass
    
    return False


def is_run_hyperlink(run: Run) -> bool:
    """Check if a run is part of a hyperlink."""
    try:
        run_xml = run._r
        hyperlink_elements = run_xml.xpath('.//w:hyperlink')
        if hyperlink_elements:
            return True
            
        # Check hyperlink-style formatting
        if (run.font.color and hasattr(run.font.color, 'rgb') and 
            run.font.color.rgb == RGBColor(0, 0, 255) and run.underline):
            return True
            
    except Exception:
        pass
    
    return False


def find_target_text_runs(para: Paragraph, target_string: str) -> List[Run]:
    """Find runs that contain the target text to be replaced."""
    target_runs = []
    
    # Build text map to find position
    char_pos = 0
    run_positions = []
    
    for run in para.runs:
        run_start = char_pos
        run_end = char_pos + len(run.text)
        run_positions.append((run, run_start, run_end))
        char_pos = run_end
    
    # Find target string position in full text
    full_text = para.text
    target_start = full_text.lower().find(target_string.lower())
    
    if target_start == -1:
        return []
    
    target_end = target_start + len(target_string)
    
    # Find runs that overlap with target text
    for run, run_start, run_end in run_positions:
        # Check if run overlaps with target range
        if (run_start < target_end and run_end > target_start):
            target_runs.append(run)
    
    return target_runs


def find_target_text_range(para: Paragraph, target_string: str) -> Tuple[int, int]:
    """Find the complete target text range in paragraph."""
    full_text = para.text.lower()
    target_lower = target_string.lower()
    
    # Try exact match first
    start_pos = full_text.find(target_lower)
    if start_pos != -1:
        return start_pos, start_pos + len(target_string)
    
    # Try to find key parts
    key_phrases = ['national reporting system', 'appendix v', 'listed in appendix']
    
    earliest_start = len(full_text)
    latest_end = 0
    
    for phrase in key_phrases:
        pos = full_text.find(phrase)
        if pos != -1:
            earliest_start = min(earliest_start, pos)
            latest_end = max(latest_end, pos + len(phrase))
    
    if earliest_start < len(full_text):
        return earliest_start, latest_end
    
    return -1, -1


def find_runs_to_remove(para: Paragraph, target_string: str) -> List[Run]:
    """Find runs that should be removed (gray shaded, hyperlinks, or target text)."""
    runs_to_remove = []
    
    target_start, target_end = find_target_text_range(para, target_string)
    
    if target_start == -1:
        return runs_to_remove
    
    # Map character positions to runs
    char_pos = 0
    run_ranges = []
    
    for run in para.runs:
        run_start = char_pos
        run_end = char_pos + len(run.text)
        run_ranges.append((run, run_start, run_end))
        char_pos = run_end
    
    # Find runs to remove
    for run, run_start, run_end in run_ranges:
        should_remove = False
        
        # Check if run overlaps with target range
        if run_start < target_end and run_end > target_start:
            should_remove = True
        # Check if it's gray shaded
        elif is_run_gray_shaded(run):
            should_remove = True
        # Check if it's a hyperlink
        elif is_run_hyperlink(run):
            should_remove = True
        
        if should_remove:
            runs_to_remove.append(run)
    
    return runs_to_remove


def create_hyperlink_run(para: Paragraph, text: str, url: str) -> Run:
    """Create a proper hyperlink run in the paragraph."""
    try:
        # Create hyperlink element
        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), "")
        hyperlink.set(qn('w:anchor'), "")
        
        # Create run element
        run_element = OxmlElement('w:r')
        run_props = OxmlElement('w:rPr')
        
        # Add hyperlink formatting
        color = OxmlElement('w:color')
        color.set(qn('w:val'), '0000FF')
        run_props.append(color)
        
        underline = OxmlElement('w:u')
        underline.set(qn('w:val'), 'single')
        run_props.append(underline)
        
        run_element.append(run_props)
        
        # Add text
        text_element = OxmlElement('w:t')
        text_element.text = text
        run_element.append(text_element)
        
        hyperlink.append(run_element)
        para._element.append(hyperlink)
        
        # Return the last run (newly created)
        return para.runs[-1]
        
    except Exception:
        # Fallback to regular run with hyperlink-like formatting
        run = para.add_run(text)
        run.font.color.rgb = RGBColor(0, 0, 255)
        run.underline = True
        return run


def build_replacement_text_by_country(components: List[Dict]) -> str:
    """Build replacement text grouped by country."""
    # Group components by country
    countries = {}
    for comp in components:
        country = comp['country']
        if country not in countries:
            countries[country] = []
        countries[country].append(comp)
    
    # Build the replacement text
    lines = []
    for country, comps in countries.items():
        # Sort components by type (text first, then hyperlinks)
        text_comps = [c for c in comps if c['type'] == 'text']
        link_comps = [c for c in comps if c['type'] == 'hyperlink']
        
        country_parts = []
        for comp in text_comps + link_comps:
            if comp['type'] == 'text':
                country_parts.append(comp['content'])
            elif comp['type'] == 'hyperlink':
                country_parts.append(comp['content'])  # Just the text for now
        
        if country_parts:
            lines.append(' '.join(country_parts))
    
    return '\n'.join(lines)


def get_replacement_components(mapping_row: pd.Series, section_type: str, 
                              cached_components: Optional[List] = None, 
                              country_delimiter: str = ";") -> List:
    """Build replacement text components from mapping data."""
    if cached_components is not None:
        return cached_components
    
    components = []
    country = mapping_row['Country']
    
    if section_type.lower() == "smpc":
        # SmPC Section 4.8 components
        nrs_text = mapping_row.get('4.8 NRS Text', '')
        nrs_url = mapping_row.get('4.8 NRS URL', '')
        av_url = mapping_row.get('4.8 Appendix V URL', '')
        
        if nrs_text:
            components.append({
                'type': 'text',
                'content': str(nrs_text),
                'country': country
            })
        
        if nrs_url:
            components.append({
                'type': 'hyperlink',
                'content': 'national reporting system',
                'url': str(nrs_url),
                'country': country
            })
        
        if av_url:
            components.append({
                'type': 'hyperlink', 
                'content': 'Appendix V',
                'url': str(av_url),
                'country': country
            })
    
    elif section_type.lower() == "pl":
        # PL Section 4 components
        pl_text = mapping_row.get('Section 4 PL Text', '')
        pl_url = mapping_row.get('Section 4 PL URL', '')
        
        if pl_text:
            components.append({
                'type': 'text',
                'content': str(pl_text),
                'country': country
            })
        
        if pl_url:
            components.append({
                'type': 'hyperlink',
                'content': 'national reporting system',
                'url': str(pl_url),
                'country': country
            })
    
    return components


def update_section_10_date(doc: DocumentObject, mapping_row: pd.Series) -> bool:
    """Update the date in Section 10 of Annex I."""
    try:
        section_10_found = False
        country = mapping_row['Country']
        
        for paragraph in doc.paragraphs:
            if "10." in paragraph.text and ("date of" in paragraph.text.lower() or 
                                          "revision" in paragraph.text.lower()):
                section_10_found = True
                formatted_date = format_date_for_country(country, 'annex_i')
                
                # Replace the date placeholder
                if "<DATE>" in paragraph.text:
                    paragraph.text = paragraph.text.replace("<DATE>", formatted_date)
                    return True
                
                # Look for existing date pattern and replace
                import re
                date_pattern = r'\d{1,2}\s+\w+\s+\d{4}'
                if re.search(date_pattern, paragraph.text):
                    paragraph.text = re.sub(date_pattern, formatted_date, paragraph.text)
                    return True
        
        return section_10_found
    except Exception:
        return False


def update_annex_iiib_date(doc: Document, mapping_row: pd.Series) -> bool:
    """Update the date in Section 6 of Annex IIIB."""
    try:
        section_6_found = False
        country = mapping_row['Country']
        
        for paragraph in doc.paragraphs:
            if "6." in paragraph.text and ("detailed information" in paragraph.text.lower() or 
                                         "leaflet" in paragraph.text.lower()):
                section_6_found = True
                formatted_date = format_date_for_country(country, 'annex_iiib')
                
                # Replace the date placeholder
                if "<DATE>" in paragraph.text:
                    paragraph.text = paragraph.text.replace("<DATE>", formatted_date)
                    return True
                
                # Look for existing date pattern and replace
                import re
                date_pattern = r'\d{1,2}\s+\w+\s+\d{4}'
                if re.search(date_pattern, paragraph.text):
                    paragraph.text = re.sub(date_pattern, formatted_date, paragraph.text)
                    return True
        
        return section_6_found
    except Exception:
        return False


def update_local_representatives(doc: Document, mapping_row: pd.Series) -> bool:
    """Update local representatives in Section 6 of Annex IIIB."""
    try:
        updated = False
        local_rep_text = mapping_row.get('Local Representative', '')
        
        if not local_rep_text or str(local_rep_text).lower() == 'nan':
            return False
        
        for paragraph in doc.paragraphs:
            if ("local representative" in paragraph.text.lower() or 
                "section 6" in paragraph.text.lower()):
                
                # Replace placeholder
                if "<LOCAL_REP>" in paragraph.text:
                    paragraph.text = paragraph.text.replace("<LOCAL_REP>", str(local_rep_text))
                    updated = True
        
        return updated
    except Exception:
        return False