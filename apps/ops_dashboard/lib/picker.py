"""Pure helper functions for the run picker page.

All functions are pure (no side effects, no I/O, no Streamlit calls).
They are extracted here so that tests/test_ops_dashboard_app.py can
unit-test them without spinning up a Streamlit server.

READ-ONLY INVARIANT: no file opens, no database writes, no LLM client
imports. This module consumes InformantRecord objects already loaded by
lib/loader.py.

See ARCHITECTURE.md §3.2 (InformantRecord schema) and
docs/DATA_DICTIONARY.md §1.1 for field semantics.
"""

from __future__ import annotations

from cdb_core.schemas import InformantRecord


def available_model_ids(records: list[InformantRecord]) -> list[str]:
    """Return sorted unique model_id values from a list of records.

    Args:
        records: List of InformantRecord objects (may be empty).

    Returns:
        Sorted list of distinct model_id strings. Empty list if records
        is empty.
    """
    return sorted({r.model_id for r in records})


def available_domains(records: list[InformantRecord]) -> list[str]:
    """Return sorted unique domain_slug values from a list of records.

    Args:
        records: List of InformantRecord objects (may be empty).

    Returns:
        Sorted list of distinct domain_slug strings. Empty list if
        records is empty.
    """
    return sorted({r.domain_slug for r in records})


def apply_filters(
    records: list[InformantRecord],
    model_ids: list[str],
    domains: list[str],
) -> list[InformantRecord]:
    """Filter records by model_id and/or domain_slug.

    An empty list for either argument means "no filter on this axis" —
    all values pass. Filters are ANDed: a record must satisfy every
    non-empty criterion. If both lists are empty, all records are
    returned unchanged.

    Args:
        records: List of InformantRecord objects to filter.
        model_ids: Keep only records whose model_id is in this list.
            Empty list = no model filter.
        domains: Keep only records whose domain_slug is in this list.
            Empty list = no domain filter.

    Returns:
        Filtered list of InformantRecord objects (may be empty).
    """
    result = records
    if model_ids:
        model_set = set(model_ids)
        result = [r for r in result if r.model_id in model_set]
    if domains:
        domain_set = set(domains)
        result = [r for r in result if r.domain_slug in domain_set]
    return result


def available_informant_ids(records: list[InformantRecord]) -> list[str]:
    """Return sorted informant_id values from a list of records.

    Args:
        records: List of InformantRecord objects (may be empty).

    Returns:
        Sorted list of informant_id strings. Empty list if records is
        empty.
    """
    return sorted(r.informant_id for r in records)
