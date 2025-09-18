# Document Processing Pipeline Requirements

## Feature Overview
Automate the eight-step regulatory document pipeline described by the user so that SmPC/PL Word documents are transformed, split, and exported with country-specific content and metadata.

## User Stories
- As a regulatory operations specialist, I want to load input documents and their mapping file so that the processor can prepare country-specific updates automatically.
- As a regulatory operations specialist, I want the system to identify each document's country/language mapping so that the correct template data is used.
- As a regulatory operations specialist, I want national reporting blocks regenerated with proper formatting so that SmPC and PL sections contain accurate hyperlinks and contacts.
- As a regulatory operations specialist, I want outdated SmPC/PL target text removed and replaced with insertion blocks so that the documents reflect current national reporting instructions.
- As a regulatory operations specialist, I want the Annex I and Annex IIIB dates refreshed per locale so that the documents comply with language-specific formatting rules.
- As a regulatory operations specialist, I want local representative tables filtered to the relevant countries so that each document only lists the required contacts.
- As a regulatory operations specialist, I want combined SmPC/PL documents split into Annex I and Annex IIIB versions so that downstream workflows receive the correct files.
- As a regulatory operations specialist, I want generated Annex files exported as DOCX and PDF and organized by country group so that the deliverables are easy to distribute.

## Acceptance Criteria (EARS)
1. **Document & Mapping Intake**  
   - WHEN the user provides an input folder of DOCX files and a mapping Excel file THEN the processor SHALL validate their presence, structure, and required columns before continuing.
   - WHEN validation fails THEN the processor SHALL log the failure and skip the affected document without terminating the entire batch.

2. **Country/Language Mapping**  
   - WHEN a document filename matches a mapping row THEN the processor SHALL associate the document with the row's country group and language.  
   - WHEN a mapping row specifies multiple countries delimited by semicolons THEN the processor SHALL treat each country as a separate insertion block within that document.

3. **SmPC Country Block Construction**  
   - WHEN constructing the SmPC reporting block THEN the processor SHALL create one formatted block per country consisting of bolded country name, ordered lines, and hyperlinks rendered for URLs and email addresses defined in the mapping file.  
   - WHEN any hyperlink text is missing from the document lines THEN the processor SHALL raise a recoverable warning and continue processing the document.

4. **Target Text Replacement**  
   - WHEN the SmPC/PL target text segment is detected in the document THEN the processor SHALL remove it and insert the newly built country blocks separated by double line breaks between countries and single line breaks at the boundaries.  
   - WHEN the target text cannot be located THEN the processor SHALL log a warning and leave the document unchanged for that segment.

5. **Date Updates**  
   - WHEN Section 10 (Annex I) and Section 6 (Annex IIIB) are processed THEN the processor SHALL replace the date text using the locale-specific headers, formats, and replacement templates supplied in the mapping row.  
   - WHEN a section header or placeholder cannot be found THEN the processor SHALL log the exception and keep existing text unchanged.

6. **Local Representative Filtering**  
   - WHEN the document contains a local representative table THEN the processor SHALL retain only rows/cells whose country names appear in the mapping row while preserving formatting and bolding required for the selected countries.  
   - WHEN the required country block is absent THEN the processor SHALL flag the document for manual review while continuing with remaining steps.

7. **Annex Splitting & Naming**  
   - WHEN Annex headers are detected in the document THEN the processor SHALL produce separate Annex I and Annex IIIB DOCX outputs with names following `[Annex]_EU_SmPC_[Language]_[Country(s)].docx`.  
   - WHEN multiple countries are associated with the document THEN the processor SHALL include the combined country list in the generated filename and ensure content coverage for all listed countries.

8. **PDF Conversion & Output Organization**  
   - WHEN DOCX annex outputs are produced THEN the processor SHALL (optionally) convert each to PDF and store the DOCX and PDF versions under folders grouped by country group with subfolders for each file type.  
   - WHEN PDF conversion fails THEN the processor SHALL retain the DOCX, log the error, and continue processing subsequent files.

## Non-Functional Requirements
- The processor SHALL support batch execution with progress logging and per-document error isolation.
- The processor SHALL preserve original documents by creating backups prior to modification when configured to do so.
- The processor SHALL maintain hyperlink functionality and formatting integrity in the generated DOCX and PDF outputs.
- The processor SHOULD finish processing a standard batch of 50 documents in under 15 minutes on reference hardware (to be refined during testing).

## Open Questions
1. How should the processor behave when the mapping file references countries not present in the input batch—log warning only or raise exception?  
2. Is PDF conversion mandatory for all runs or can users disable it via configuration at runtime?  
3. Should backup `.orig` files also be organized into the country-based folder structure or remain in-place next to the source documents?  
4. Are there any country-specific exceptions for hyperlink formatting (e.g., display text differs from URL/email) that must be supported beyond direct substitutions?  
5. What is the expected behavior when Annex II headers are missing or mislabeled—should the splitter fall back to heuristics or fail the document?
