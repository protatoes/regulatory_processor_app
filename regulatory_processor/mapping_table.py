"""Mapping table utilities and data models for regulatory document processing."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

import pandas as pd

from .config import MappingError, ProcessingConfig

# Columns that must exist in the mapping workbook in order to process documents.
REQUIRED_COLUMNS: Sequence[str] = (
    "Country",
    "Language",
    "National reporting system SmPC",
    "National reporting system PL",
    "Line 1 - Country names to be bolded - SmPC",
    "Line 2 - SmPC",
    "Line 3 - SmPC",
    "Line 4 - SmPC",
    "Line 5 - SmPC",
    "Line 6 - SmPC",
    "Line 7 - SmPC",
    "Line 8 - SmPC",
    "Line 9 - SmPC",
    "Line 10 - SmPC",
    "Hyperlinks SmPC",
    "Link for email - SmPC",
    "Text to be appended after National reporting system PL",
    "Local Representative",
    "Country names to be bolded - Local Reps",
    "Annex I Date Header",
    "Annex I Date Format",
    "Annex IIIB Date Text",
    "Annex IIIB Date Format",
    "Annex I Header in country language",
    "Annex II Header in country language",
    "Annex IIIB Header in country language",
    "Original text national reporting - SmPC",
    "Original text national reporting - PL",
)

# Columns that may contain filename association data for lookup convenience.
FILENAME_PATTERN_COLUMNS: Sequence[str] = (
    "Filename Pattern",
    "Filename pattern",
    "Source Filename",
    "Source Filenames",
    "Document Pattern",
)


def _is_missing(value: object) -> bool:
    """Return ``True`` when the supplied value should be treated as missing."""

    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):  # type: ignore[arg-type]
        return True
    if isinstance(value, str):
        trimmed = value.strip()
        return not trimmed or trimmed.lower() == "nan"
    try:
        return bool(pd.isna(value))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover - defensive fallback
        return False


def _split_cell(value: object, delimiter: str) -> Tuple[str, ...]:
    """Split a mapping cell into a tuple of trimmed tokens."""

    if _is_missing(value):
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    if not isinstance(value, str):
        value = str(value)
    parts = [part.strip() for part in str(value).split(delimiter)]
    return tuple(part for part in parts if part)


def _normalize_token(value: str) -> str:
    """Normalize text for dictionary keys (case-insensitive, alphanumeric)."""

    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "", value.lower())


@dataclass
class MappingRow:
    """Structured representation of a single mapping workbook row."""

    index: int
    series: pd.Series
    delimiter: str
    language: str = field(init=False)
    language_token: str = field(init=False)
    countries: Tuple[str, ...] = field(init=False)
    country_codes: Tuple[str, ...] = field(init=False)
    country_tokens: Tuple[str, ...] = field(init=False)
    smpc_lines: Tuple[Tuple[str, ...], ...] = field(init=False)
    smpc_hyperlinks: Tuple[str, ...] = field(init=False)
    smpc_emails: Tuple[str, ...] = field(init=False)
    pl_append_texts: Tuple[str, ...] = field(init=False)
    local_rep_countries: Tuple[str, ...] = field(init=False)
    filename_patterns: Tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:  # noqa: D401 - documented via dataclass docstring
        self.language = str(self._resolve_value("Language", default="")).strip()
        self.language_token = _normalize_token(self.language)
        self.countries = self._split_column("Country")
        self.country_codes = self._split_column("Country Code") or self._split_column(
            "Country Codes"
        )
        tokens_source = self.country_codes or self.countries
        self.country_tokens = tuple(
            token for token in (_normalize_token(token) for token in tokens_source) if token
        )
        self.smpc_lines = tuple(
            self._split_column(f"Line {line_no} - SmPC", allow_empty=True)
            for line_no in range(1, 11)
        )
        self.smpc_hyperlinks = self._split_column("Hyperlinks SmPC", allow_empty=True)
        self.smpc_emails = self._split_column("Link for email - SmPC", allow_empty=True)
        self.pl_append_texts = self._split_column(
            "Text to be appended after National reporting system PL", allow_empty=True
        )
        self.local_rep_countries = self._split_column(
            "Country names to be bolded - Local Reps", allow_empty=True
        )
        self.filename_patterns = self._collect_filename_patterns()

    # ------------------------------------------------------------------
    # Convenience accessors mirroring minimal pandas.Series behaviour
    # ------------------------------------------------------------------

    def _resolve_value(self, key: str, default: Optional[object] = None) -> object:
        if key not in self.series:
            return default
        value = self.series.get(key, default)
        if _is_missing(value):
            return default
        return value

    def _split_column(self, key: str, allow_empty: bool = False) -> Tuple[str, ...]:
        if key not in self.series:
            return ()
        parts = _split_cell(self.series.get(key), self.delimiter)
        if parts:
            return parts
        return parts if allow_empty else ()

    def _collect_filename_patterns(self) -> Tuple[str, ...]:
        patterns: List[str] = []
        for column in FILENAME_PATTERN_COLUMNS:
            if column in self.series:
                patterns.extend(_split_cell(self.series[column], self.delimiter))
        return tuple(patterns)

    # Public API --------------------------------------------------------

    @property
    def index_labels(self) -> Tuple[str, ...]:
        """Return the original column labels for compatibility."""

        return tuple(str(label) for label in self.series.index)

    @property
    def index(self) -> pd.Index:
        """Expose the pandas index for compatibility with legacy helpers."""

        return self.series.index

    @property
    def country_display(self) -> str:
        """Return a display-friendly string for the country group."""

        if self.countries:
            return "; ".join(self.countries)
        value = self._resolve_value("Country", default="")
        return str(value).strip() if value is not None else ""

    def get(self, key: str, default: Optional[object] = None) -> object:
        """Mirror ``dict.get`` semantics using the underlying series."""

        return self._resolve_value(key, default)

    def __getitem__(self, key: str) -> object:
        return self.series[key]

    def to_series(self) -> pd.Series:
        """Return a copy of the backing pandas series."""

        return self.series.copy()

    def as_dict(self) -> Dict[str, object]:
        """Return the row as a plain dictionary."""

        return {str(key): value for key, value in self.series.items()}

    def iter_country_slices(self) -> Iterator[Tuple[str, List[str]]]:
        """Yield country name with the ordered SmPC lines for that country."""

        if not self.countries:
            return

        for idx, country in enumerate(self.countries):
            lines: List[str] = []
            for line_values in self.smpc_lines:
                if idx < len(line_values):
                    lines.append(line_values[idx])
            yield country, lines


class MappingTable:
    """Container for mapping rows with multiple lookup strategies."""

    def __init__(self, dataframe: pd.DataFrame, config: ProcessingConfig):
        self.dataframe = dataframe.copy()
        self.config = config
        self.rows: List[MappingRow] = [
            MappingRow(index=i, series=dataframe.iloc[i], delimiter=config.country_delimiter)
            for i in range(len(dataframe))
        ]
        self._country_language_index: Dict[Tuple[str, str], List[MappingRow]] = {}
        self._filename_index: Dict[str, List[MappingRow]] = {}
        self._build_indexes()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_excel(
        cls, file_path: str | Path, config: Optional[ProcessingConfig] = None
    ) -> "MappingTable":
        """Load, validate, and parse the mapping workbook."""

        cfg = config or ProcessingConfig()
        path = Path(file_path)
        try:
            dataframe = pd.read_excel(path)
        except Exception as exc:  # pragma: no cover - pandas handles specifics
            raise MappingError(f"Failed to read mapping file '{file_path}': {exc}") from exc

        return cls.from_dataframe(dataframe=dataframe, config=cfg)

    @classmethod
    def from_dataframe(
        cls, dataframe: pd.DataFrame, config: Optional[ProcessingConfig] = None
    ) -> "MappingTable":
        """Construct a mapping table from a pre-loaded dataframe."""

        if dataframe.empty:
            raise MappingError("Mapping workbook does not contain any rows")

        missing = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
        if missing:
            raise MappingError(
                "Mapping workbook is missing required columns: " + ", ".join(sorted(missing))
            )

        cfg = config or ProcessingConfig()
        return cls(dataframe=dataframe, config=cfg)

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def _build_indexes(self) -> None:
        for row in self.rows:
            if row.language_token:
                tokens = row.country_tokens or (_normalize_token(row.country_display),)
                for country_token in tokens:
                    if not country_token:
                        continue
                    key = (country_token, row.language_token)
                    self._country_language_index.setdefault(key, []).append(row)

            for pattern in row.filename_patterns:
                normalized = _normalize_token(pattern)
                if not normalized:
                    continue
                self._filename_index.setdefault(normalized, []).append(row)

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[MappingRow]:
        return iter(self.rows)

    def for_language(self, language: str) -> List[MappingRow]:
        """Return all rows that match the requested language (case-insensitive)."""

        token = _normalize_token(language)
        if not token:
            return []
        return [row for row in self.rows if row.language_token == token]

    def get_by_country_language(self, country: str, language: str) -> List[MappingRow]:
        """Lookup rows by country token and language token."""

        key = (_normalize_token(country), _normalize_token(language))
        return list(self._country_language_index.get(key, []))

    def match_filename(self, filename: str, language: Optional[str] = None) -> List[MappingRow]:
        """Return mapping rows that match the provided filename pattern."""

        normalized_filename = _normalize_token(Path(filename).stem)
        if not normalized_filename:
            return []

        candidates: List[MappingRow] = []
        for pattern, rows in self._filename_index.items():
            if pattern and pattern in normalized_filename:
                candidates.extend(rows)

        if language:
            token = _normalize_token(language)
            candidates = [row for row in candidates if row.language_token == token]

        return candidates

    def languages(self) -> List[str]:
        """Return the list of languages available in the mapping table."""

        return sorted({row.language for row in self.rows if row.language})

    def to_dataframe(self) -> pd.DataFrame:
        """Return a copy of the underlying dataframe."""

        return self.dataframe.copy()


__all__ = [
    "MappingRow",
    "MappingTable",
    "REQUIRED_COLUMNS",
    "FILENAME_PATTERN_COLUMNS",
]
