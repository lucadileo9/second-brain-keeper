"""Polymorphic output serializer supporting Markdown, JSON, YAML, and CSV formats."""

import csv
import io
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

import yaml

from ..exceptions import FormatError


class OutputFormat(str, Enum):
    """Supported output serialization formats."""

    MD = "md"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"

    @classmethod
    def from_str(cls, val: str) -> "OutputFormat":
        """Convert string to OutputFormat case-insensitively."""
        normalized = val.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        return cls.MD

    @classmethod
    def from_extension(cls, path: Union[str, Path]) -> "OutputFormat":
        """Infer OutputFormat from file path extension."""
        ext = Path(path).suffix.lower()
        if ext in (".json",):
            return cls.JSON
        if ext in (".yaml", ".yml"):
            return cls.YAML
        if ext in (".csv",):
            return cls.CSV
        return cls.MD


def _normalize_obj(obj: Any) -> Any:
    """Recursively normalize dataclasses and custom objects to standard Python primitives."""
    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        return _normalize_obj(obj.to_dict())
    if is_dataclass(obj) and not isinstance(obj, type):
        return _normalize_obj(asdict(obj))
    if isinstance(obj, dict):
        return {str(k): _normalize_obj(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_normalize_obj(i) for i in obj]
    return obj


def render_markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Format headers and rows into a clean GitHub Flavored Markdown (GFM) table."""
    if not headers:
        return ""

    header_cols = [str(h).strip() for h in headers]
    separator_cols = [":---" for _ in headers]

    lines = [
        "| " + " | ".join(header_cols) + " |",
        "| " + " | ".join(separator_cols) + " |",
    ]

    for row in rows:
        row_cols = [str(r).replace("|", "\\|").replace("\n", " ") for r in row]
        # Pad row with empty cells if length mismatch
        if len(row_cols) < len(headers):
            row_cols.extend([""] * (len(headers) - len(row_cols)))
        lines.append("| " + " | ".join(row_cols[: len(headers)]) + " |")

    return "\n".join(lines)


def format_output(
    data: Any,
    format: Union[OutputFormat, str] = OutputFormat.MD,
    headers: Optional[List[str]] = None,
    title: Optional[str] = None,
) -> str:
    """Serialize data into the requested format (Markdown, JSON, YAML, CSV)."""
    fmt = OutputFormat.from_str(str(format)) if not isinstance(format, OutputFormat) else format
    normalized = _normalize_obj(data)

    if fmt == OutputFormat.JSON:
        return json.dumps(normalized, indent=2, ensure_ascii=False, default=str)

    if fmt == OutputFormat.YAML:
        return yaml.safe_dump(normalized, sort_keys=False, allow_unicode=True, default_flow_style=False).strip()

    if fmt == OutputFormat.CSV:
        # Validate that hierarchical/nested structures are not being exported to flat CSV
        if isinstance(normalized, dict):
            has_nested = any(isinstance(v, (dict, list)) and v for v in normalized.values())
            if has_nested:
                raise FormatError(
                    "Cannot export hierarchical/nested data structure to flat CSV format. "
                    "Use JSON, YAML, or Markdown instead."
                )

        output = io.StringIO()
        writer = csv.writer(output)

        if isinstance(normalized, list):
            if normalized and isinstance(normalized[0], dict):
                keys = headers or list(normalized[0].keys())
                writer.writerow(keys)
                for item in normalized:
                    if isinstance(item, dict):
                        writer.writerow([str(item.get(k, "")) for k in keys])
            elif normalized:
                writer.writerow(["item"])
                for item in normalized:
                    writer.writerow([str(item)])
            else:
                writer.writerow(headers or ["item"])
        elif isinstance(normalized, dict):
            writer.writerow(["property", "value"])
            for k, v in normalized.items():
                writer.writerow([str(k), str(v)])
        else:
            writer.writerow(["value"])
            writer.writerow([str(normalized)])
        return output.getvalue().strip()

    # Markdown format (Default)
    output_lines: List[str] = []
    if title:
        output_lines.append(f"## {title}\n")

    if isinstance(normalized, str):
        output_lines.append(normalized)
    elif isinstance(normalized, list):
        if not normalized:
            output_lines.append("*(Nessun elemento trovato)*")
        elif isinstance(normalized[0], dict):
            keys = headers or list(normalized[0].keys())
            rows = [[item.get(k, "") for k in keys] for item in normalized if isinstance(item, dict)]
            output_lines.append(render_markdown_table(keys, rows))
        else:
            for item in normalized:
                output_lines.append(f"- {item}")
    elif isinstance(normalized, dict):
        keys = ["Proprieta", "Valore"]
        rows = [[str(k), str(v)] for k, v in normalized.items()]
        output_lines.append(render_markdown_table(keys, rows))
    else:
        output_lines.append(str(normalized))

    return "\n".join(output_lines).strip()


class ReportWriter:
    """Centralized dispatcher for rendering and exporting reports across CLI commands."""

    def __init__(
        self,
        data: Any,
        md_rendered: Optional[str] = None,
        headers: Optional[List[str]] = None,
        title: Optional[str] = None,
        tabular_data: Optional[Any] = None,
    ) -> None:
        self.data = data
        self.md_rendered = md_rendered
        self.headers = headers
        self.title = title
        self.tabular_data = tabular_data

    def render(self, fmt: Union[OutputFormat, str]) -> str:
        """Render data to target format string."""
        f = OutputFormat.from_str(str(fmt)) if not isinstance(fmt, OutputFormat) else fmt
        if f == OutputFormat.MD and self.md_rendered is not None:
            return self.md_rendered
        if f == OutputFormat.CSV and self.tabular_data is not None:
            return format_output(self.tabular_data, format=f, headers=self.headers, title=self.title)
        return format_output(self.data, format=f, headers=self.headers, title=self.title)

    def write_reports(
        self,
        console_format: Union[OutputFormat, str] = OutputFormat.MD,
        output_files: Optional[Sequence[Union[str, Path]]] = None,
        quiet: bool = False,
        logger: Optional[Any] = None,
    ) -> None:
        """Export reports to files and/or standard output based on format and quiet flags."""
        if output_files:
            for out_path in output_files:
                if not out_path:
                    continue
                p = Path(out_path).resolve()
                detected_fmt = OutputFormat.from_extension(p)
                content = self.render(detected_fmt)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content + "\n", encoding="utf-8")
                if logger and not quiet:
                    logger.info("Report saved to: %s", p)

        if not quiet:
            content = self.render(console_format)
            if content:
                print(content)
