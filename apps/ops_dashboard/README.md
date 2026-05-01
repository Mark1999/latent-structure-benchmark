# LSB Internal Ops Dashboard

An internal read-only inspection tool for validating LSB collection results
(freelist, pile-sort, decline interviews). This is **not** the public dashboard
at `cogstructurelab.com`; that lives in `apps/dashboard/`.

## What it is

- Read-only consumer of `data/raw/informants.jsonl` and related files.
- Never writes to any data file.
- Single-user, Linode-only, accessed via SSH tunnel.
- Streamlit app; no build step required.
- **Not bound by `DESIGN_SYSTEM.md`** — internal tooling, no UI/UX gate.

## How to launch

On `lsb-agent-02`, from the repo root (`/opt/lsb-agent`):

```bash
uv run --with streamlit streamlit run apps/ops_dashboard/app.py \
    --server.address=127.0.0.1
```

This binds Streamlit to `127.0.0.1:8501` only — it is not reachable from the
public internet. Run inside a `tmux` session so it persists when you disconnect:

```bash
tmux new-session -s ops-dash
uv run --with streamlit streamlit run apps/ops_dashboard/app.py \
    --server.address=127.0.0.1
# Ctrl-B d  to detach
```

## SSH tunnel

From your local machine (Mark's workstation):

```bash
ssh -L 8501:localhost:8501 lsb-agent-02
```

Then open `http://localhost:8501` in a browser.

## Installing the ops extra

The `ops` optional-dependency group in `apps/ops_dashboard/pyproject.toml`
pins Streamlit to `>=1.57,<1.58`. If you want to install it into the uv
environment rather than using `--with streamlit` each time:

```bash
uv pip install -e "apps/ops_dashboard[ops]"
```

## Read-only invariant

This app is a passive inspector. It:

- Opens data files in read-only mode only.
- Never calls any collection adapter.
- Never imports `anthropic`, `openai`, `google.generativeai`, or any other
  LLM client library.
- Never writes to `data/raw/informants.jsonl`,
  `data/raw/decline_interviews.jsonl`, or any other data file.

If a future change would break the read-only invariant, stop and ask Mark.

## Not in scope

- Bound by `DESIGN_SYSTEM.md` — it is not.
- UI/UX agent review — not required for internal tooling.
- CDA SME review — not required for display tooling.
- Public internet access — never. SSH tunnel only.
