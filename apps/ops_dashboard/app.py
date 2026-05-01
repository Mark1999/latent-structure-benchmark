"""
LSB Internal Ops Dashboard — read-only inspection tool.

This is an internal operational tool for Mark to visually validate freelist,
pile-sort, and decline-interview collection results. It is NOT the public
dashboard at cogstructurelab.com.

READ-ONLY INVARIANT: this app never writes to data/raw/informants.jsonl,
data/raw/decline_interviews.jsonl, or any other data file. It is a
read-only consumer of the LSB data layer.

Not bound by DESIGN_SYSTEM.md — internal tooling only.

Launch: uv run --with streamlit streamlit run apps/ops_dashboard/app.py \
            --server.address=127.0.0.1
SSH tunnel: ssh -L 8501:localhost:8501 lsb-agent-02
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from cdb_core.schemas import InformantRecord

from apps.ops_dashboard.lib.loader import load_informants
from apps.ops_dashboard.lib.picker import (
    apply_filters,
    available_domains,
    available_informant_ids,
    available_model_ids,
)

# ── Constants ──

_REPO_ROOT = Path(__file__).resolve().parents[2]
_INFORMANTS_PATH = _REPO_ROOT / "data" / "raw" / "informants.jsonl"

# ── Page config ──

st.set_page_config(
    page_title="LSB Internal Ops Dashboard",
    page_icon=None,
    layout="wide",
)

st.title("LSB Internal Ops Dashboard")
st.caption("Read-only inspection tool — internal use only, not the public dashboard")

st.info(
    "**READ-ONLY:** This tool never writes to any data file. "
    "It is a passive inspector of `data/raw/informants.jsonl`, "
    "`data/raw/decline_interviews.jsonl`, and related files.",
    icon=None,
)

st.divider()


# ── Loader (cached until process restart — file is append-only) ──

@st.cache_data
def _load_all() -> list[InformantRecord] | str:
    """Load all InformantRecord objects from informants.jsonl.

    Returns either the list of records or a string error message if the
    file does not exist or cannot be parsed.
    """
    if not _INFORMANTS_PATH.exists():
        return (
            f"File not found: `{_INFORMANTS_PATH}`\n\n"
            "Run the collection scripts first to populate "
            "`data/raw/informants.jsonl`."
        )
    try:
        return load_informants(_INFORMANTS_PATH)
    except ValueError as exc:
        return f"Failed to parse `{_INFORMANTS_PATH}`:\n\n```\n{exc}\n```"


# ── Main rendering ──

_loaded = _load_all()

if isinstance(_loaded, str):
    # File missing or parse error — surface clearly, no traceback
    st.error(_loaded)
    st.stop()

all_records: list[InformantRecord] = _loaded

# ── Sidebar filters ──

with st.sidebar:
    st.header("Filters")

    all_model_ids = available_model_ids(all_records)
    selected_model_ids: list[str] = st.multiselect(
        label="model_id",
        options=all_model_ids,
        default=[],
        help="Select one or more model IDs to filter records. Leave empty to include all.",
    )

    all_domain_slugs = available_domains(all_records)
    selected_domains: list[str] = st.multiselect(
        label="domain",
        options=all_domain_slugs,
        default=[],
        help="Select one or more domains to filter records. Leave empty to include all.",
    )

    st.divider()
    st.caption(
        "LSB Internal Ops Dashboard v0.1 | "
        "Not bound by DESIGN_SYSTEM.md | "
        "Single-user, Linode-only, SSH-tunnel access"
    )

# ── Apply filters ──

filtered_records = apply_filters(
    all_records,
    model_ids=selected_model_ids,
    domains=selected_domains,
)

# ── Main area ──

st.subheader("Run picker")

n_total = len(all_records)
n_match = len(filtered_records)
st.write(f"**{n_match}** record(s) match — {n_total} total in file.")

if n_match == 0:
    st.info("No records match the current filters.")
    st.stop()

# Build the informant_id picker from filtered records
informant_id_options = available_informant_ids(filtered_records)

selected_informant_id: str | None = st.selectbox(
    label="informant_id",
    options=informant_id_options,
    index=0,
    help=(
        "Select an informant_id (unique per model/domain/run). "
        "The selected value is stored as `selected_informant_id` in session state "
        "for use by downstream pages (OPS-T4+)."
    ),
)

# Persist to session state so OPS-T4 (detail view) can read it
if selected_informant_id is not None:
    st.session_state["selected_informant_id"] = selected_informant_id
    st.info(
        f"Detail view coming in OPS-T4 — selected: `{selected_informant_id}`"
    )
