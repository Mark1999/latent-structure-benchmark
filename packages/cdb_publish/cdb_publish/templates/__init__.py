"""Versioned lede templates for cdb_publish.

Each lede_v{N}.py module contains the PATTERNS dict and LEDE_VERSION
constant for that generation. Per CLAUDE.md §6 R7 (prompt templates
are versioned), lede templates follow the same discipline: never edit
a published template in place; create lede_v2.py for any future change.
"""
