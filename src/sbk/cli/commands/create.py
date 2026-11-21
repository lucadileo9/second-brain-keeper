"""Implementation of 'sbk create' command."""

import logging
from argparse import Namespace
from pathlib import Path
from typing import List, Optional

from ...exceptions import CreationError, TaxonomyError, TemplateError, VaultKeeperError
from ...utils.formatters import format_output, render_markdown_table
from ..common import get_vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_create(args: Namespace, logger: logging.Logger) -> int:
    """Create a standardized note using templates, strict validation, and folder auto-routing."""
    v = get_vault(args, logger)
    if not v:
        return EXIT_ERROR

    title = getattr(args, "title")
    tipo = getattr(args, "tipo")
    folder = getattr(args, "folder", None)
    raw_tags = getattr(args, "tags", None)
    template = getattr(args, "template", None)
    dry_run = getattr(args, "dry_run", False)
    fmt = getattr(args, "format", "md")
    raw_body = getattr(args, "body", None)
    body_file = getattr(args, "body_file", None)

    body: Optional[str] = None
    if raw_body is not None:
        body = raw_body
    elif body_file is not None:
        file_path = Path(body_file)
        if not file_path.is_file():
            logger.error("Creation failed: Body file '%s' does not exist or is not a file.", file_path)
            return EXIT_ERROR

        # Enforce max file size of 5 MB to prevent vault corruption/bloat
        max_size_bytes = 5 * 1024 * 1024
        if file_path.stat().st_size > max_size_bytes:
            logger.error(
                "Creation failed: Body file '%s' exceeds maximum allowed size of 5 MB (%d bytes).",
                file_path,
                file_path.stat().st_size,
            )
            return EXIT_ERROR

        try:
            raw_bytes = file_path.read_bytes()
            if b"\x00" in raw_bytes:
                logger.error("Creation failed: Body file '%s' contains binary null bytes.", file_path)
                return EXIT_ERROR
            body = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            logger.error("Creation failed: Body file '%s' is not valid UTF-8 text: %s", file_path, exc)
            return EXIT_ERROR
        except Exception as exc:
            logger.error("Creation failed: Error reading body file '%s': %s", file_path, exc)
            return EXIT_ERROR

    tags_list: Optional[List[str]] = None
    if raw_tags:
        tags_list = [t.strip().lstrip("#") for t in raw_tags.split(",") if t.strip()]

    try:
        res = v.create(
            title=title,
            tipo=tipo,
            folder=folder,
            tags=tags_list,
            template=template,
            body=body,
            dry_run=dry_run,
        )
    except (CreationError, TaxonomyError, TemplateError, VaultKeeperError) as exc:
        logger.error("Creation failed: %s", exc)
        return EXIT_ERROR
    except Exception as exc:
        logger.error("Unexpected error during note creation: %s", exc)
        return EXIT_ERROR

    if fmt in ("json", "yaml", "csv"):
        print(format_output(res, format=fmt))
        return EXIT_SUCCESS

    # Markdown format
    idx_info = f"Aggiornato (`{res.index_path.name}`)" if res.index_updated and res.index_path else "Invariato"
    status_info = (
        "[DRY-RUN] Nessun file scritto"
        if res.dry_run
        else f"Transazione `{res.tx_id or 'N/A'}` (annullabile con `vk undo`)"
    )
    tags_str = ", ".join(f"`{t}`" for t in res.tags) if res.tags else "(Nessuno)"

    table = render_markdown_table(
        headers=["Proprietà", "Valore"],
        rows=[
            ["Percorso", f"`{res.rel_path.as_posix()}`"],
            ["Stem", f"[[{res.stem}]]"],
            ["Tipo", f"`{res.tipo}`"],
            ["Tag", tags_str],
            ["Template", f"`{res.template_used or 'Predefinito Standard'}`"],
            ["Indice Cartella", idx_info],
            ["Stato", status_info],
        ],
    )

    prefix = "[DRY-RUN] " if res.dry_run else ""
    print(f"# {prefix}Nuova Nota: {res.title}\n\n{table}")
    return EXIT_SUCCESS
