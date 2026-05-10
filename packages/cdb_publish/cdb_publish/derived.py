"""Display-derived fields for the publish layer (Phase 5 T3).

These functions compute frontend-ready derived fields from the analysis
JSON: r1_state per model, top-5 free-list terms ranked by Sutrop CSI.
The dashboard receives these pre-computed so it does not re-derive on
every render.

Per CDA SME plan-level verdict Q4: top_freelist_terms() defaults to
Sutrop CSI as the salience-rank metric (list-length-robust). The
domain JSON carries `display.top_terms_metric: "sutrop_csi"` so a
researcher reproducing the export can audit the choice.
"""

from __future__ import annotations

from typing import Final, Literal

from cdb_core.schemas import SutropCSI, WithinModelResult

from cdb_publish.lede import OCI_LOW_CONCENTRATION_THRESHOLD

# r1_state literal values mirror DESIGN_SYSTEM.md §3.3.5
# and the CSV export contract in §5.
R1State = Literal["typical_concentration", "low_concentration", "deterministic"]

# Q4 binding: Sutrop CSI is the canonical salience-rank metric for LSB
# display because it is robust to list length, unlike raw frequency or
# Smith's S which favour shorter lists.
TOP_TERMS_METRIC: Final = "sutrop_csi"

DEFAULT_TOP_K: Final = 5


def r1_state_for(within: WithinModelResult) -> R1State:
    """Map a WithinModelResult to its Register-1 state per DESIGN_SYSTEM.md §3.3.5.

    State assignment (priority order):
    - deterministic_output=True  → "deterministic" (R1-c)
    - oci < OCI_LOW_CONCENTRATION_THRESHOLD  → "low_concentration" (R1-b)
    - else  → "typical_concentration" (R1-a)

    Parameters
    ----------
    within:
        A WithinModelResult as loaded from DomainResult.within_model_results.

    Returns
    -------
    R1State
        One of "deterministic", "low_concentration", or "typical_concentration".
    """
    if within.deterministic_output:
        return "deterministic"
    if within.oci < OCI_LOW_CONCENTRATION_THRESHOLD:
        return "low_concentration"
    return "typical_concentration"


def top_freelist_terms(
    sutrop_csi: dict[str, SutropCSI],
    k: int = DEFAULT_TOP_K,
) -> list[str]:
    """Return the top-k terms by Sutrop CSI value (descending).

    Q4 binding: Sutrop CSI is the canonical salience-rank metric for
    LSB display because it is robust to list length (vs raw frequency
    or Smith's S, which favour shorter lists). The JSON's
    `display.top_terms_metric` records this choice for auditability.

    Stable tie-break: lexicographic ascending on the term string so
    the output is deterministic regardless of dict-insertion order.

    Parameters
    ----------
    sutrop_csi:
        Mapping of term → SutropCSI, as stored in
        DomainResult.sutrop_csi[model_id]. Each SutropCSI has a
        `.csi` float attribute.
    k:
        Maximum number of terms to return. Defaults to DEFAULT_TOP_K (5).

    Returns
    -------
    list[str]
        Term strings in descending CSI order, lexicographic tie-break,
        truncated to at most k entries. Returns an empty list when the
        input dict is empty.
    """
    if not sutrop_csi:
        return []

    # Sort descending by csi, then ascending by term for a stable tie-break.
    sorted_items = sorted(
        sutrop_csi.items(),
        key=lambda kv: (-kv[1].csi, kv[0]),
    )
    return [term for term, _ in sorted_items[:k]]
