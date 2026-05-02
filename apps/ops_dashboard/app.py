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

import sys
from pathlib import Path

# Streamlit puts only the script's directory on sys.path; insert the repo root
# so `from apps.ops_dashboard.lib...` resolves the same way pytest sees it
# (pythonpath = ["."] in the root pyproject.toml).
_REPO_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORTS))

import streamlit as st
from cdb_core.schemas import DeclineInterview, InformantRecord

from apps.ops_dashboard.lib.detail import (
    DeclineDetail,
    build_thinking_trace,
    find_decline_events,
    format_freelist,
    format_pile_sort,
)
from apps.ops_dashboard.lib.loader import (
    load_decline_interviews,
    load_informants,
    load_jsonl_dicts,
)
from apps.ops_dashboard.lib.picker import (
    apply_filters,
    available_domains,
    available_informant_ids,
    available_model_ids,
)

# ── Constants ──

_REPO_ROOT = Path(__file__).resolve().parents[2]
_INFORMANTS_PATH = _REPO_ROOT / "data" / "raw" / "informants.jsonl"
_DECLINE_INTERVIEWS_PATH = _REPO_ROOT / "data" / "raw" / "decline_interviews.jsonl"
_MANUAL_CLASS_PATH = (
    _REPO_ROOT / "data" / "derived" / "decline_interviews_manual_classification.jsonl"
)
_SAFETY_SUBTYPE_PATH = (
    _REPO_ROOT
    / "data"
    / "derived"
    / "decline_interviews_safety_attribution_subtype.jsonl"
)

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


# ── Loaders (cached until process restart — files are append-only) ──

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


@st.cache_data
def _load_decline_interviews() -> list[DeclineInterview]:
    """Load all DeclineInterview objects from decline_interviews.jsonl.

    Missing file returns an empty list (no decline data collected yet is
    a normal first-class state, not an error).
    """
    return load_decline_interviews(_DECLINE_INTERVIEWS_PATH)


@st.cache_data
def _load_manual_classifications() -> list[dict]:
    """Load manual classification rows from the derived JSONL file."""
    return load_jsonl_dicts(_MANUAL_CLASS_PATH)


@st.cache_data
def _load_safety_subtypes() -> list[dict]:
    """Load safety attribution subtype rows from the derived JSONL file."""
    return load_jsonl_dicts(_SAFETY_SUBTYPE_PATH)


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

# Persist to session state so downstream sections can read it
if selected_informant_id is not None:
    st.session_state["selected_informant_id"] = selected_informant_id

# ── Detail view (OPS-T4) — activates when an informant_id is selected ──

if st.session_state.get("selected_informant_id") is None:
    st.stop()

_detail_id: str = st.session_state["selected_informant_id"]

# Locate the selected record in the full (unfiltered) list so we always
# find it even if sidebar filters change after selection.
_record_map = {r.informant_id: r for r in all_records}
if _detail_id not in _record_map:
    st.warning(f"informant_id `{_detail_id}` not found in loaded records.")
    st.stop()

_rec: InformantRecord = _record_map[_detail_id]

st.divider()
st.subheader(f"Detail — `{_detail_id}`")
st.caption(
    f"model_id: `{_rec.model_id}` | domain: `{_rec.domain_slug}` | "
    f"run_index: {_rec.run_index} | qa_passed: {_rec.qa_passed}"
)

# ── Section 1 — Freelist ──────────────────────────────────────────────────────

st.markdown("### Freelist")

_items = format_freelist(_rec)

if _items:
    for i, item in enumerate(_items, start=1):
        st.markdown(f"{i}. {item}")
else:
    st.warning(
        "**0 items elicited. The pile-sort prompt for this informant was "
        "constructed with 0 items of input — see Section 2.**"
    )

# Optional thinking trace from the freelist step
_trace = build_thinking_trace(_rec)
if _trace:
    with st.expander("Thinking trace (verbatim) — freelist step"):
        st.caption(
            "Model thinking trace, verbatim. This is the chain-of-thought "
            "output text from the freelist step, not an interpretation of "
            "internal cognition."
        )
        st.text(_trace)

# ── Section 2 — Pile-sort ─────────────────────────────────────────────────────

st.markdown("### Pile-sort")
st.caption(
    "*Pile labels and member ordering are the model's own output, verbatim. "
    "Not re-summarized or re-ordered.*"
)

_piles = format_pile_sort(_rec)

if not _piles:
    st.info("*This informant returned no pile-sort data.*")
else:
    for pile in _piles:
        if pile.is_empty:
            st.markdown(f"**Pile {pile.pile_number}: \"{pile.label}\"** (0 items)")
        elif pile.is_singleton:
            member = pile.members[0]
            st.markdown(
                f"**Pile {pile.pile_number} (singleton): \"{pile.label}\"**"
            )
            st.markdown(f"- {member}")
        else:
            st.markdown(f"**Pile {pile.pile_number}: \"{pile.label}\"**")
            for member in pile.members:
                st.markdown(f"- {member}")

# ── Section 3 — Decline events ───────────────────────────────────────────────

st.markdown("### Decline events")
st.caption(
    "*The verbatim text below contains the model's stated attributions. "
    "Any claims about reality are the model's attributions, not facts.*"
)

_decline_interviews = _load_decline_interviews()
_classifications = _load_manual_classifications()
_subtypes = _load_safety_subtypes()

_declines: list[DeclineDetail] = find_decline_events(
    informant_id=_detail_id,
    decline_interviews=_decline_interviews,
    classifications=_classifications,
    subtypes=_subtypes,
)

if not _declines:
    st.info("*No decline events recorded for this informant.*")
else:
    for decline in _declines:
        st.markdown(
            f"**Decline interview** `{decline.decline_interview_id}` — "
            f"step: `{decline.originating_step}` | "
            f"outcome: `{decline.originating_outcome_class}`"
        )
        st.text_area(
            label="Verbatim response",
            value=decline.response_verbatim,
            height=150,
            disabled=True,
            key=f"resp_{decline.decline_interview_id}",
        )
        if decline.thinking_verbatim:
            with st.expander("Follow-up thinking trace (verbatim)"):
                st.text(decline.thinking_verbatim)
        if decline.manual_classification is not None:
            classifier_label = (
                f"(classified by: {decline.manual_classifier_id})"
                if decline.manual_classifier_id
                else "(manual review)"
            )
            st.markdown(
                f"Manual classification (read-only): `{decline.manual_classification}` "
                f"{classifier_label}"
            )
        if decline.safety_attribution_subtype is not None:
            subtype_classifier_label = (
                f"(classified by: {decline.subtype_classifier_id})"
                if decline.subtype_classifier_id
                else "(manual review)"
            )
            st.markdown(
                f"Safety attribution subtype (read-only): "
                f"`{decline.safety_attribution_subtype}` "
                f"{subtype_classifier_label}"
            )
        st.divider()
