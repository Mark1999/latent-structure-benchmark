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

import streamlit as st

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

st.markdown(
    """
    ### What this is

    An internal visual inspection tool for validating LSB collection results.
    Use it to browse freelist, pile-sort, and decline-interview records without
    reading raw JSON.

    **This is not the public dashboard.** The public dashboard lives at
    `cogstructurelab.com` and is built from `apps/dashboard/`.

    ### Navigation (tasks OPS-T2 and beyond)

    Additional pages will be added here as the ops dashboard is built out:

    - **T2 — Record loader:** browse `InformantRecord` objects from `informants.jsonl`
    - **T3 — Freelist viewer:** inspect raw freelist responses per model / domain
    - **T4 — Pile-sort viewer:** inspect pile-sort matrices
    - **T5 — Decline-interview viewer:** inspect `DeclineInterview` records
    - **T6 — QA summary:** per-model QA pass/fail summary table
    - **T7 — Run-diff viewer:** compare two runs side by side

    ### Read-only invariant

    This app may call `st.cache_data`-backed loaders that read files, but it
    never opens any file for writing, never calls any collection adapter, and
    never imports any LLM client library.
    """,
    unsafe_allow_html=False,
)

st.divider()
st.caption(
    "LSB Internal Ops Dashboard v0.1 | "
    "Not bound by DESIGN_SYSTEM.md | "
    "Single-user, Linode-only, SSH-tunnel access"
)
