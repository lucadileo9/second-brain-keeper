"""Template discovery, variable interpolation, and standard note templating engine."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..exceptions import CreationError, TemplateError
from ..models import VaultConfig
from ..utils.helpers import resolve_vault_path
from .document import MarkdownDocument


def resolve_target_folder(
    vault_root: Path,
    tipo: str = "Appunto",
    custom_folder: Optional[Union[str, Path]] = None,
    inbox_folder: str = "00_Inbox",
) -> Path:
    """Resolve the destination directory for a new note.

    If custom_folder is provided:
        - Resolves relative to vault_root (or validates absolute path within vault_root).
    Otherwise:
        - Resolves deterministically to the configured staging inbox folder (default: '00_Inbox').

    Args:
        vault_root: Root path of the vault.
        tipo: Note classification type (unused for routing, kept for backward compatibility).
        custom_folder: Optional explicit target folder.
        inbox_folder: Staging inbox folder name or relative path (default: '00_Inbox').

    Returns:
        Resolved Path for the target folder.

    Raises:
        CreationError: If custom_folder resolves outside the vault root.
    """
    if custom_folder is not None:
        resolved = resolve_vault_path(custom_folder, vault_root)
        try:
            resolved.relative_to(vault_root.resolve())
        except ValueError:
            raise CreationError(f"Target folder '{custom_folder}' is outside vault root: {vault_root}")
        return resolved

    clean_inbox = str(inbox_folder).strip() if inbox_folder else "00_Inbox"
    return resolve_vault_path(clean_inbox, vault_root)


class TemplateEngine:
    """Discovers, renders, and interpolates Markdown note templates."""

    def __init__(self, config: VaultConfig) -> None:
        self.config = config

    def get_templates_folder(self) -> Optional[Path]:
        """Locate the active templates folder, checking configured and fallback paths."""
        folder_str = self.config.templates_folder or "00-09_Meta/02_Template"
        candidates = [
            self.config.root_path / folder_str,
            self.config.root_path / "01-09_Risorse_Di_Sistema" / "01_Templates",
            self.config.root_path / "00-09_Meta" / "02_Template",
            self.config.root_path / "Templates",
            self.config.root_path / "_templates",
        ]
        for c in candidates:
            if c.is_dir():
                return c
        return self.config.root_path / folder_str

    def list_templates(self) -> List[str]:
        """Return sorted list of template filenames found in the templates directory."""
        tmpl_dir = self.get_templates_folder()
        if not tmpl_dir or not tmpl_dir.is_dir():
            return []
        return sorted([p.name for p in tmpl_dir.glob("*.md") if not p.name.startswith(".")])

    def find_template(self, template_name_or_path: Optional[str]) -> Optional[Path]:
        """Attempt to locate a template by explicit name, filename, or path.

        Checks:
        1. Direct filesystem path (cwd-relative or absolute).
        2. Vault-root-relative path.
        3. File in the active templates folder matching target name or target + '.md'.
        4. Case-insensitive filename or stem match in templates folder.

        Returns None if not found.
        """
        if template_name_or_path is None or not template_name_or_path.strip():
            return None

        target = template_name_or_path.strip()

        # 1. Direct filesystem path (cwd-relative or absolute)
        p_explicit = Path(target)
        if p_explicit.is_file():
            return p_explicit.resolve()

        # 2. Vault-root-relative path
        p_vault_explicit = (self.config.root_path / p_explicit).resolve()
        if p_vault_explicit.is_file():
            return p_vault_explicit

        # 3. Check inside templates_folder
        tmpl_dir = self.get_templates_folder()
        if not tmpl_dir or not tmpl_dir.is_dir():
            return None

        candidate = tmpl_dir / target
        if candidate.is_file():
            return candidate.resolve()

        if not target.endswith(".md"):
            candidate_md = tmpl_dir / f"{target}.md"
            if candidate_md.is_file():
                return candidate_md.resolve()

        # 4. Case-insensitive match in tmpl_dir
        target_lower = target.lower()
        target_stem = target_lower[:-3] if target_lower.endswith(".md") else target_lower
        for p in tmpl_dir.glob("*.md"):
            if p.name.startswith("."):
                continue
            if p.name.lower() == target_lower or p.stem.lower() == target_stem:
                return p.resolve()

        return None

    def resolve_template_path(self, template: Optional[str] = None) -> Optional[Path]:
        """Resolve a template path using deterministic 3-tier precedence.

        Tier 1: Explicit CLI template argument (`template`).
                If provided, resolves it; raises TemplateError if not found.
        Tier 2: Configured default template (`self.config.default_template`).
                If set in config, resolves it; raises TemplateError if not found.
        Tier 3: None (caller falls back to universal code scaffold).

        Args:
            template: Optional explicit template name or path.

        Returns:
            Resolved Path of the template file, or None if Tier 3 fallback applies.

        Raises:
            TemplateError: If an explicit template or configured default cannot be found.
        """
        tmpl_dir = self.get_templates_folder()

        # Tier 1: Explicit CLI argument
        if template is not None and template.strip():
            found = self.find_template(template)
            if found is not None:
                return found
            raise TemplateError(
                f"Template '{template.strip()}' not found in '{tmpl_dir}'. "
                f"Available templates: {', '.join(self.list_templates()) or '(None)'}"
            )

        # Tier 2: Configured default template
        default_tmpl = self.config.default_template
        if default_tmpl is not None and default_tmpl.strip():
            found_default = self.find_template(default_tmpl)
            if found_default is not None:
                return found_default
            raise TemplateError(
                f"Configured default template '{default_tmpl.strip()}' not found in '{tmpl_dir}'. "
                f"Available templates: {', '.join(self.list_templates()) or '(None)'}"
            )

        # Tier 3: Universal code fallback (caller should use get_default_template)
        return None

    def get_default_template(self, tipo: str) -> str:
        """Generate an ultra-minimal, language-agnostic template scaffold."""
        clean_tipo = tipo.strip().capitalize() if tipo and tipo.strip() else "Appunto"
        if self.config and self.config.allowed_types:
            for allowed in self.config.allowed_types:
                if allowed.lower() == clean_tipo.lower():
                    clean_tipo = allowed
                    break
        return f"---\ntipo: {clean_tipo}\ntags: []\n---\n\n# {{{{title}}}}\n"

    def render_template(
        self,
        raw_content: str,
        title: str,
        stem: str,
        tipo: str,
        tags: Optional[List[str]] = None,
        extra_vars: Optional[Dict[str, Any]] = None,
        body: Optional[str] = None,
    ) -> str:
        """Interpolate variables and enforce strictly valid frontmatter schema.

        Supported variables:
            {{title}}, {{stem}}, {{tipo}}, {{type}}, {{date}}, {{time}}, {{datetime}}, {{body}}
            and any keys passed in extra_vars.

        Args:
            raw_content: Raw template Markdown content.
            title: Human-readable note title.
            stem: Normalized filename stem.
            tipo: Note classification type.
            tags: List of validated taxonomy tags.
            extra_vars: Optional dictionary of additional template variables.
            body: Optional initial markdown body content to inject.

        Returns:
            Rendered Markdown text with frontmatter and body.
        """
        now = datetime.now()
        context: Dict[str, str] = {
            "title": title,
            "stem": stem,
            "tipo": tipo,
            "type": tipo,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "datetime": now.isoformat(timespec="seconds"),
        }

        has_body_placeholder = bool(re.search(r"\{\{\s*body\s*\}\}", raw_content, re.IGNORECASE))
        if has_body_placeholder:
            context["body"] = body.strip() if body else ""

        if extra_vars:
            for k, v in extra_vars.items():
                context[k] = str(v)

        # Interpolate variables: {{var}} or {{ var }}
        def repl(match: re.Match) -> str:
            var_name = match.group(1).strip()
            for k, v in context.items():
                if k.lower() == var_name.lower():
                    return v
            return match.group(0)

        interpolated = re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", repl, raw_content)

        # Parse document to normalize and enforce frontmatter
        doc = MarkdownDocument.from_content(interpolated)
        doc.tipo = tipo

        # If template did not have a {{body}} placeholder and body was provided, append it cleanly
        if not has_body_placeholder and body and body.strip():
            clean_body = body.strip()
            if doc.body.strip():
                doc.body = f"{doc.body.rstrip()}\n\n{clean_body}\n"
            else:
                doc.body = f"\n\n{clean_body}\n"

        if tags is not None:
            doc.set_frontmatter_field("tags", list(tags))
        else:
            # Clean up dummy tags from template if present
            existing_tags = doc.tags
            if tipo.lower() != "sistema":
                existing_tags = [t for t in existing_tags if t.lower() != "sistema"]
            doc.set_frontmatter_field("tags", existing_tags)

        return doc.to_content()
