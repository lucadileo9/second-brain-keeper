"""Modular CLI subcommand parser registrars."""

from .diagnostic import register_diagnostic_parsers
from .governance import register_governance_parsers
from .lifecycle import register_lifecycle_parsers
from .maintenance import register_maintenance_parsers

__all__ = [
    "register_diagnostic_parsers",
    "register_governance_parsers",
    "register_lifecycle_parsers",
    "register_maintenance_parsers",
]
