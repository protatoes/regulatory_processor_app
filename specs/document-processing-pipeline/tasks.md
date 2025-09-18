# Document Processing Pipeline Tasks

## 1. Foundation & Configuration
- [ ] 1.1 Update `ProcessingConfig` defaults and flags for backups, PDF conversion, overwrite policy, and logging level; adjust `ProcessingResult/ProcessingStats` to capture new counters (Req 1, Req 8, Non-Functional).
- [ ] 1.2 Implement `MappingTable` loader that validates required columns and builds lookup dictionaries by `(country_code, language)` and filename pattern (Req 1).
- [ ] 1.3 Create `MappingRow` dataclass parsing semicolon-delimited fields into ordered lists for countries, SmPC lines, hyperlinks, emails, PL append text, and local representative countries (Req 2, Req 3, Req 6).

## 2. SmPC & PL Block Processing
- [ ] 2.1 Build helper functions in `document_utils` to construct country insertion blocks with bold country names, formatted lines, and hyperlink/email conversion; emit warnings when substrings missing (Req 3).
- [ ] 2.2 Update `DocumentUpdater` to replace SmPC/PL target text runs with generated blocks, handling block separation and appended PL text while logging warnings when target text absent (Req 4).

## 3. Date Updates
- [ ] 3.1 Extend `DateFormatterSystem` to support locale-specific patterns, month localization, and configurable processing date; integrate Annex I/IIIB update methods that use mapping headers/placeholders (Req 5).

## 4. Local Representative Filtering
- [ ] 4.1 Implement `LocalRepresentativeUpdater` logic to detect country blocks inside representative tables, keep only mapping-listed countries, and enforce bold formatting of country names (Req 6).

## 5. Annex Splitting & Output
- [ ] 5.1 Enhance `DocumentSplitter` to locate Annex headers using localized strings and produce Annex I/IIIB documents while preserving formatting (Req 7).
- [ ] 5.2 Implement output filename generator and folder organization per country group, including manifest updates and uniqueness handling (Req 7, Req 8).

## 6. PDF Conversion & Finalization
- [ ] 6.1 Integrate optional PDF conversion pipeline with fallback strategy, recording failures without aborting processing (Req 8).
- [ ] 6.2 Wire all components together in `DocumentProcessor` main loop: discover documents, resolve mapping rows, execute processing steps with error handling, manage backups, and update statistics (Req 1–8, Non-Functional).

## 7. Testing
- [ ] 7.1 Author unit tests for mapping parsing, hyperlink creation, date formatting, representative filtering, and annex splitting behaviors (Req 1–7).
- [ ] 7.2 Add integration tests covering single-country and multi-country document scenarios, including PDF conversion toggling and error handling (Req 1–8, Non-Functional).
