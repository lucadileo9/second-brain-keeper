"""SBK (Second Brain Keeper) typed exception hierarchy.

All exceptions raised by the sbk core engine inherit from SBKError.
"""

from typing import Optional


class SBKError(Exception):
    """Base exception for all SBK (Second Brain Keeper) operations."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


# Backward-compatibility alias
VaultKeeperError = SBKError


class ConfigurationError(SBKError):
    """Raised when configuration validation or loading fails."""


class VaultNotFoundError(SBKError):
    """Raised when the specified vault root directory does not exist or is inaccessible."""


class FrontmatterError(SBKError):
    """Raised when frontmatter parsing, validation, or updating fails."""


class TaxonomyError(SBKError):
    """Raised when tag taxonomy validation encounters errors."""


class NamingError(SBKError):
    """Raised when naming normalization or collision detection fails."""


class LinkResolutionError(SBKError):
    """Raised when wikilink parsing, disambiguation, or rewriting fails."""


class AttachmentError(SBKError):
    """Raised when attachment scanning, soft-deletion, or file moving fails."""


class JournalError(SBKError):
    """Raised when transaction journaling fails or transaction state is corrupted."""


class UndoError(SBKError):
    """Raised when an undo operation fails to revert a transaction."""


class UndoConflictError(UndoError):
    """Raised when undo fails because a file was modified externally after the transaction."""


class DocumentError(SBKError):
    """Raised when parsing or manipulating a MarkdownDocument fails."""


class LifecycleError(SBKError):
    """Raised when vault item renaming, moving, or refactoring fails."""


class ArchiveError(LifecycleError):
    """Raised when archiving a note or project fails."""


class OffloadError(LifecycleError):
    """Raised when offloading heavy media to cold storage fails."""


class SearchError(SBKError):
    """Raised when vault search parameters or execution fails."""


class ConfigUpdateError(SBKError):
    """Raised when updating vault configuration files fails."""


class TemplateError(SBKError):
    """Raised when template resolution, parsing, or variable interpolation fails."""


class CreationError(SBKError):
    """Raised when note creation fails due to collisions or validation errors."""


class FormatError(SBKError):
    """Raised when data cannot be serialized to the requested format."""
