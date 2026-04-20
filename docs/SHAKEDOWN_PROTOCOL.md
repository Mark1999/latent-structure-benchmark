# Pre-Phase-4a Shakedown Protocol

**Document name:** `docs/SHAKEDOWN_PROTOCOL.md`
**Status:** Binding for any pre-Phase-4a collection run that is not a formal validation-gate run
**Prepared:** 2026-04-20 (post PR B merge; post unified @architect + @cda_sme recommendation)
**Audience:** Mark (operator), Coder agent, CDA SME agent, Reviewer agent
**Companion docs:** `ARCHITECTURE.md` §4.1 (collection), §4.1.6 (QA_Runner), §5.3 Phase 4, §6.2 (spend cap); `docs/INCIDENTS/2026-04-19-test-data-loss.md` (backup precondition); `docs/BOOTSTRAP_DESIGN.md` §2 (Register 1 underestimation caveat); `docs/SME_REVIEW.md`

---

## 0. What this document is

A binding protocol for running a small, non-canonical data collection against real LLM APIs before the Phase 4a gate-running collection begins. It operationalizes the unified @architect + @cda_sme recommendation synthesized on 2026-04-20.

**The shakedown exists to validate the pipeline, not the models.** Its outputs are diagnostic about the instrument, not evidence about the subject matter. Methodologically, a shakedown sits in the same epistemic class as a synthetic test run — the data happens to come from real APIs, but it is not evidence of anything about the models.

---

## 1. What the shakedown is (and is not)

**Is:**

- A one-time end-to-end pipeline exercise against real LLM output.
- The first real `DomainResult` the CDA SME has seen.
- An empirical partial resolution of three post-F1 open questions: the OCI R1-b cutoff (provisional 3.0), the G2 rename sufficiency, and the "mismatch is the finding" methods-page lead-paragraph verification.
- Non-canonical. Diagnostic only. Internal use only.

**Is not:**

- Phase 4a. Phase 4a is the canonical 12-model × domain × N=5 collection that produces the dataset, runs G1/G2/G3 gates, and (on pass) unlocks Zenodo DOI minting. Phase 4a requires the B2 backup layer active per `docs/INCIDENTS/2026-04-19-test-data-loss.md` §5.1.
- A substitute for the §4.2.7 saturation sweep (that requires N=30 on three reference models).
- A substitute for Phase 4c human baseline acquisition.
- Evidence about the models under study. The shakedown N is too small, the domain coverage is too thin, and the uncertainty handling is too conservative to support any claim about the models.
- Publishable. Shakedown data never appears on `cogstructurelab.com`, in any social post, or in any external citation.

---

## 2. Non-canonical labeling — binding, machine-enforced

The CDA SME's sole non-negotiable guardrail: shakedown data must be **machine-prevented** from being confused with canonical data. Convention alone (file naming, commit messages) is insufficient.

**Four-layer enforcement (all four required):**

1. **Path segregation.** Shakedown JSONL is written to `data/shakedown/<campaign-id>/informants.jsonl`, **never** `data/raw/informants.jsonl`. The canonical `InformantRecord` stream and the shakedown stream do not share a file.
2. **Gitignore.** `data/shakedown/` is listed in `.gitignore` so the data cannot be accidentally committed alongside code.
3. **Build-script exclusion.** `scripts/build_db.py` excludes any path under `data/shakedown/` from the canonical SQLite database build. This is the machine enforcement — the bundle-build script cannot ingest shakedown records even if asked.
4. **Per-record campaign tag.** Every shakedown record is tagged in its QA notes with `campaign_id=shakedown-<YYYYMMDD>` written verbatim into `qa_notes` at collection time. This is a secondary signal, not the primary one (the path is primary). It exists so that if a record ever escapes the directory — copied, exported, forwarded in a screenshot — its provenance is intact on the record itself.

**The `README.md` file placed in `data/shakedown/<campaign-id>/` at collection start reads verbatim:**

> **NON-CANONICAL.** Diagnostic data from a pre-Phase-4a pipeline shakedown run. These numbers are diagnostic about the LSB pipeline, not evidence about any model's output. Do not cite, screenshot, export, or reference externally. This directory is deleted before Phase 4a begins. See `docs/SHAKEDOWN_PROTOCOL.md`.

---

## 3. External-citation rule (binding, added at CDA SME insistence)

If shakedown results are ever cited, screenshotted, or referenced externally — even informally, in a talk, in a tweet, in a Slack message to someone outside the project — the shakedown run becomes an **"official" artifact retroactively**, and the Phase 4a B2 backup precondition applies **in hindsight**. If at that point there is no off-host backup of the run's records, the cited artifact is irreproducible and the project's audit-trail commitment (§1 commitment 7 of `ARCHITECTURE.md`) is broken.

Practical consequence: the shakedown is internal-only. If anyone wants to show shakedown results to an outside collaborator, the conversation has to be: "here is a pipeline test run; the methodology tests out but the data is non-canonical; the real corpus is coming in Phase 4a." No screenshots without that framing, no talks referencing the numbers without that framing.

**"External" explicitly includes:** pasting data, numbers, or file contents into any LLM chat interface on an outside machine (ChatGPT web, Claude.ai, Gemini web, etc.); forwarding via Slack/email/DM to anyone outside the project; uploading to any shared drive (Google Drive, Dropbox) accessible by non-project accounts; including in any talk slide deck, even an internal one if the deck may be redistributed. The 2026 norm of "paste it into an assistant for a quick look" is a screenshot equivalent for this purpose and makes the data retroactively official under this rule.

---

## 4. Scope

| Parameter | Value | Reasoning |
|---|---|---|
| Models | **4 architecturally distinct** — recommended: `claude-sonnet-4.6`, `gpt-5.4-mini`, `gemini-2.5-flash`, `deepseek-chat-v3.1` | Spans 3 origins (US, US, US, CN), 2 openness states (closed, closed, closed, open), 4 collection methods (`anthropic_api`, `openai_api`, `google_ai`, `openrouter`). Exercises the most adapter surface per dollar. |
| Domains | **2**: `family` and `holidays` | `family` has grounding candidates (see `PHASE_4C_CANDIDATE_SOURCES.md`); `holidays` is ungrounded in v1. Exercises State-0 vs State-1 rendering + the groundings-list-as-first-class logic. |
| N runs per (model, domain) cell | **8** | Minimum for meaningful OCI spectrum and Sutrop saturation; agrees with both agents. |
| Primary cells | 4 × 2 × 8 = 64 full CDA protocol runs (3 steps each = ~192 API calls) | — |
| Prompt-sensitivity cell | **1** additional cell with 8 prompt variants on `claude-sonnet-4.6` × `family` × N=5 | Exercises split G1 (salience + spatial) under real variance. |
| Determinism cell | **1** additional run-set at `temperature=0` on one model × `family` × N=5 | Exercises the OCI sentinel path and the `deterministic_output=False` path under high-concentration real data (the actual deterministic trigger is `λ₂ ≤ DETERMINISTIC_EIGENVALUE_THRESHOLD = 1e-12` on an agreement matrix of size ≥ 2 per `packages/cdb_analyze/cdb_analyze/two_level.py`). Current transformers at T=0 are expected **not** to trip `deterministic_output=True` — that classification is reserved for future deterministic architectures per SME §3.3. The cell verifies the sentinel reports correctly and the Register 2 visual convention in `DESIGN_SYSTEM.md` §3.3.5 (hollow triangle, no ellipse) is *not* triggered by T=0 alone on a transformer. |
| Total API calls (estimate) | ~300 | See §6 for budget. |
| Wall-clock | 4–6 hours, serial | Allows inspection of first model's output before fanning out. |

**Model substitutions are allowed** if the named IDs are not in `data/models/registry.json` at run time. The required property is architectural diversity: at least one closed-weight US, at least one open-weight, at least one non-US origin, at least four collection methods exercised.

---

## 5. Preconditions before execution (all must be met)

1. **Off-host copy: private GitHub repo push of `data/shakedown/<campaign-id>.tar.gz` after each session.** Committed to a private repo named `lsb-shakedown-archive` under Mark's account. JSONL is small (low single-digit MB) and the private-repo path uses existing GitHub auth, so there is zero infrastructure to stand up — simpler than a Backblaze B2 bucket for a short-lived shakedown cycle. Verify `git push --dry-run` succeeds against `lsb-shakedown-archive` before the shakedown begins. The "just leave it on the Surface" option is not acceptable — the 2026-04-19 incident's lesson applies even to non-canonical data. If Mark does not yet have `lsb-shakedown-archive` configured, create it first; no shakedown runs until it's verified.
2. **`.gitignore` lists `data/shakedown/`.** Added in this PR.
3. **`scripts/build_db.py` excludes `data/shakedown/`.** Added in this PR.
4. **Spend cap env override active.** Export `CDB_MAX_SPEND_USD=25` for the shakedown session (well below the $300 monthly cap, well above the ~$15 expected cost). The three-tier defense halts cleanly on overspend.
5. **One model run inspected before fanning out.** Collect one model's output on one domain at N=2, eyeball the free-list and pile-sort parsing, confirm `qa_passed=True`, then proceed with the full scope. Protects against a parser bug eating the whole run.
6. **CDA SME sign-off on this document.** This file (`SHAKEDOWN_PROTOCOL.md`) is routed through CDA SME before any shakedown command is run.

---

## 6. Budget

Estimated spend by provider (rough, based on registry per-token pricing and observed output lengths in test runs):

**Note on the interview step.** The pile-sort step's prompt carries the full item list back to the model (up to 60 items × ~10 chars each ≈ 600 input tokens overhead per call), and the interview step produces the longest output (one label per pile, often with justification text). The per-call averages below include both effects. Claude Sonnet in particular under-estimates at $0.08/call if interview outputs exceed ~1k tokens; the table below uses $0.12/call to be conservative.

| Cell | Runs | Steps | API calls | $/call (est) | Subtotal |
|---|---|---|---|---|---|
| Claude Sonnet × 2 domains | 16 | 3 | 48 | $0.12 | $5.76 |
| GPT-5.4-mini × 2 domains | 16 | 3 | 48 | $0.03 | $1.44 |
| Gemini Flash × 2 domains | 16 | 3 | 48 | $0.02 | $0.96 |
| DeepSeek Chat × 2 domains | 16 | 3 | 48 | $0.015 | $0.72 |
| Sensitivity cell (8 variants × N=5 × 3 steps, Claude) | 40 | 3 | 120 | $0.12 | $14.40 |
| Determinism cell (N=5 at T=0 × 3 steps, Claude) | 5 | 3 | 15 | $0.12 | $1.80 |
| **Expected total** | | | **~327** | | **~$25.08** |
| Ceiling with retries / token blow-outs | | | ~500 | | **~$40** |

**The `$CDB_MAX_SPEND_USD=25` override sits at the expected total.** If the run trips the cap, that's itself a finding — it means Claude's interview step is producing more output than estimated, and the Phase 4a budget extrapolation (12 × 3 × 5 × $0.12 ≈ $22 per domain per pass) needs revision. If that happens, raise the cap to $50 and resume; do not run more than $50 in a single shakedown session without a fresh budget review.

To reduce cost: running the sensitivity cell on `gpt-5.4-mini` or `gemini-2.5-flash` instead of Claude drops the cell from ~$14 to ~$2–4. Acceptable substitution if Claude budget is a constraint; the cell's purpose is to exercise split G1 plumbing, not to characterize Claude specifically.

---

## 7. Execution sequence

```bash
# 0. Precondition check
cat docs/SHAKEDOWN_PROTOCOL.md | head -40   # confirm this is the operative protocol
grep -q "data/shakedown/" .gitignore         # confirm gitignore
grep -q "data/shakedown" scripts/build_db.py # confirm build exclusion
# Verify the four named models are in the live registry. Substitute any
# that are not per the §4 scope note. Model IDs in the registry change
# over time; running this with dead IDs is a §7a CLI-gap finding, not
# a shakedown finding.
uv run python -c "
import json
r = json.load(open('data/models/registry.json'))
registry_ids = {m['model_id'] for m in r['models']}
needed = {'claude-sonnet-4.6', 'gpt-5.4-mini', 'gemini-2.5-flash', 'deepseek-chat-v3.1'}
missing = needed - registry_ids
assert not missing, f'Missing from registry — substitute per §4: {missing}'
print('All four shakedown models present in registry')
"
# Verify off-host archive target is reachable
git -C /path/to/lsb-shakedown-archive push --dry-run origin main  # abort if this fails

# 1. Branch + campaign id
CAMPAIGN_ID="shakedown-$(date +%Y%m%d)"
mkdir -p "data/shakedown/$CAMPAIGN_ID"
cat > "data/shakedown/$CAMPAIGN_ID/README.md" <<'EOF'
NON-CANONICAL. Diagnostic data from a pre-Phase-4a pipeline shakedown run.
Do not cite, screenshot, export, or reference externally. This directory
is deleted before Phase 4a begins. See docs/SHAKEDOWN_PROTOCOL.md.
EOF

# 2. Smoke test — one model × N=1 across both domains before any fan-out.
# This catches domain-specific parsing bugs (holiday items often include
# dates and numerals which exercise different free-list parser paths
# than family term strings) on the smallest possible call budget.
# Campaign tag is folded into --output path; env-var shortcuts
# LSB_CAMPAIGN_ID / LSB_RAW_JSONL_PATH do NOT exist per §7a and are
# NOT used. All subsequent collect.py invocations use explicit --output.
export CDB_MAX_SPEND_USD=25
SHAKEDOWN_JSONL="data/shakedown/$CAMPAIGN_ID/informants.jsonl"
uv run python scripts/collect.py \
    --model claude-sonnet-4.6 --domain family --runs 1 \
    --output "$SHAKEDOWN_JSONL"
uv run python scripts/collect.py \
    --model claude-sonnet-4.6 --domain holidays --runs 1 \
    --output "$SHAKEDOWN_JSONL"

# 3. Eyeball the output — parsed_items non-empty, parsed_piles non-empty,
#    qa_passed=True on both records, provider_request_id populated.
uv run python scripts/qa_check.py --file "$SHAKEDOWN_JSONL"

# 4. Fan out — the four models × two domains × N=8 primary cells
for model in claude-sonnet-4.6 gpt-5.4-mini gemini-2.5-flash deepseek-chat-v3.1; do
    for domain in family holidays; do
        uv run python scripts/collect.py \
            --model "$model" --domain "$domain" --runs 8 \
            --output "$SHAKEDOWN_JSONL"
    done
done

# 5. Sensitivity cell — 8 prompt variants on one model × one domain.
# Uses --prompt-version iteratively (§7a: --prompt-variants N does
# not exist on master; the eight v1_s1..v1_s8 directories are the
# eight variants).
for variant in v1_s1 v1_s2 v1_s3 v1_s4 v1_s5 v1_s6 v1_s7 v1_s8; do
    uv run python scripts/collect.py \
        --model claude-sonnet-4.6 --domain family --runs 5 \
        --prompt-version "$variant" \
        --output "$SHAKEDOWN_JSONL"
done

# 6. Determinism cell — temperature=0 on one model × one domain.
# REQUIRES the --temperature pre-shakedown PR per §7a (not on
# master at time of protocol authoring). If that PR has not landed,
# skip this cell; log it as a pre-shakedown blocker.
uv run python scripts/collect.py \
    --model claude-sonnet-4.6 --domain family --runs 5 \
    --temperature 0.0 \
    --output "$SHAKEDOWN_JSONL"

# 7. Run the analysis pipeline against the shakedown JSONL
uv run python scripts/analyze.py \
    --file "$SHAKEDOWN_JSONL" \
    --domain family \
    --output "data/shakedown/$CAMPAIGN_ID/results/family.json"
uv run python scripts/analyze.py \
    --file "$SHAKEDOWN_JSONL" \
    --domain holidays \
    --output "data/shakedown/$CAMPAIGN_ID/results/holidays.json"

# 8. Off-host copy
tar -czf "data/shakedown/$CAMPAIGN_ID.tar.gz" "data/shakedown/$CAMPAIGN_ID/"
# ... then push to the chosen off-host path (B2 or private repo)

# 9. Cost report
uv run python scripts/cost_report.py --month current
```

### 7a. CLI preflight — known gaps (audited 2026-04-20)

An audit of `scripts/collect.py` against the §7 sequence above produced the following findings. These must be addressed **before** the shakedown runs, not discovered during it:

| Flag / env var the §7 sequence uses | Status on master | Workaround / required fix |
|---|---|---|
| `--domain`, `--model`, `--runs`, `--output`, `--dry-run` | ✓ Present | Use as-is |
| `LSB_RAW_JSONL_PATH` env var | ✗ **Not present** | Use `--output data/shakedown/<campaign-id>/informants.jsonl` explicitly on every invocation; drop the env-var shortcut from §7 |
| `LSB_CAMPAIGN_ID` env var | ✗ **Not present** | The per-record campaign tag in `qa_notes` is not automatic — either (a) add a post-hoc sed/script pass on the JSONL to insert `campaign_id=shakedown-<date>` into `qa_notes`, or (b) ship a small pre-PR that adds `--campaign-id` to `collect.py` and writes it into `qa_notes` at collection time. (b) is cleaner; recommend doing it as a 5-line pre-shakedown PR |
| `--prompt-variants N` | ✗ **Not present** | Use `--prompt-version v1_s1`, `v1_s2`, ..., `v1_s8` iteratively (loop over the eight versioned prompt directories; `packages/cdb_collect/prompts/` contains `v1_s1` through `v1_s8`). Equivalent output, just scripted as a bash loop rather than a single invocation |
| `--temperature 0.0` | ✗ **Not present** | **Genuine blocker for the determinism cell.** Temperature is hard-coded in the protocol runner (0.7 for free-list, 0.3 for pile-sort per §4.1.3). Running at T=0 requires a small pre-shakedown PR adding `--temperature` override to `collect.py`. Without it, the determinism cell cannot run |

**Disposition of the two genuine blockers** (`--campaign-id`, `--temperature`): land them as a **small pre-shakedown PR** — 1 file each, ~10 lines each, one test apiece — before the shakedown kicks off. Not bundled with this protocol PR; they're code changes, this is a doc change. Logging here so they're not forgotten.

**Where the workaround is acceptable** (`--prompt-variants`): use the `--prompt-version v1_sN` loop. No code change required.

---

## 8. Sanity checks on the first real DomainResult (CDA SME list)

Before any further work proceeds on Phase 4a, the first real `data/shakedown/<campaign-id>/results/family.json` (primary cell) and the sensitivity-cell `DomainResult` must together pass all eight of these checks:

1. `consensus_type` is populated from the Caulkins typology (not hardcoded, not empty).
2. `romney_eigenratio` and per-model `oci` are reported as **distinct** fields with distinct labels; no cross-contamination.
3. Every `WithinModelResult` carries `underestimates_uncertainty=True` per the Level-1 binding from `docs/BOOTSTRAP_DESIGN.md` §2.
4. `generated_lede` check: **if** `cdb_publish` is wired and the field is non-empty, it must pass the §1.5.4 forbidden-vocabulary regex from `ARCHITECTURE.md`. **If** `cdb_publish` is not yet wired and the field is empty, this check is N/A (vacuously satisfied); do not mark it failed.
5. Any model with a negative `cultural_centrality_scores` entry is flagged in `negative_centrality_models`, not silently dropped.
6. `truncation_type` is populated on every `InformantRecord` (not null-by-default) — the field should name the reason the free list ended (usually `elbow`).
7. **Split G1 fields are distinct on the sensitivity-cell DomainResult** (SME §1.3, un-deferred). `g1_salience_stability` and `g1_spatial_stability` are reported as separate numeric fields; `g1_salience_pass` and `g1_spatial_pass` are reported as separate booleans; `g1_overall_pass` equals their conjunction. A single aggregated G1 number on a sensitivity-cell result is a regression of SME §1.3 and fails this check.
8. **`consensus_type` and `negative_centrality_flag` are logically consistent per the `classify_consensus` decision table.** If `negative_centrality_flag=True`, then `consensus_type` MUST be one of `{SUBCULTURAL, CONTESTED, DETERMINISTIC}`. If all centrality scores are positive (flag False), then `consensus_type` MUST be one of `{STRONG_CONSENSUS, WEAK_CONSENSUS, TURBULENT, DETERMINISTIC}`. Any inconsistency means the classification dispatch is broken, not that the model is weird.

If any check fails, the shakedown result is a finding about the pipeline and the issue is logged. The shakedown does not "fail" in a pass/fail sense — surfacing issues is its purpose.

---

## 9. What "done" means for the shakedown

- All cells collected without exceeding the `CDB_MAX_SPEND_USD=25` cap.
- `data/shakedown/<campaign-id>/` contains the JSONL, the per-domain `results/*.json`, and the off-host copy has been verified.
- The six §8 sanity checks have been run and any failures logged.
- The CDA SME has reviewed the two real `DomainResult` JSONs and filed their methodology findings — partial resolution of open questions 1, 4, and 5 is the expected output; open questions 2 and 3 remain untouched.
- Any pipeline bugs surfaced by the shakedown are filed as issues against master and fixed *before* Phase 4a begins.

---

## 10. Retention and disposal

- **During the review window:** `data/shakedown/<campaign-id>/` lives on the Surface plus the off-host copy (`lsb-shakedown-archive` private repo). Duration: as long as the CDA SME needs to review, probably a few days.
- **Before Phase 4a kickoff:** `data/shakedown/` is deleted from the Surface.
- **Off-host copy retention:** retained until **Phase 4a G1/G2/G3 gate evaluation completes successfully**, then deleted. The audit-trail value of the shakedown is "did the pipeline work before the official run?" — that value stays relevant until Phase 4a concludes, whether that's 30 days from now or 120. Hard date retention (90 days) risks the archive evaporating mid-cycle if Phase 4a slips. Delete the archive repo after Phase 4d passes.
- **If bugs were surfaced:** the shakedown records that exercised the buggy path are kept alongside the bug fix PR as a regression-test fixture, explicitly subset and labeled. These extracted fixtures are the only shakedown artifacts that survive past Phase 4a and enter the canonical repo (under `tests/fixtures/` with full provenance notes).

### 10.1 Machine-enforcement constant location

The four-layer labeling in §2 includes `scripts/build_db.py` refusing to ingest any path containing the `shakedown` segment. The literal string is pinned in:

```python
# scripts/build_db.py, module level
SHAKEDOWN_PATH_SEGMENT: str = "shakedown"
```

**Do not rename the `data/shakedown/` directory or the constant without updating the other.** A silent rename to `data/pre-canonical/` (or similar) without touching `SHAKEDOWN_PATH_SEGMENT` would silently disable the fourth labeling layer. Future changes to the directory name require a paired change to the constant in the same PR. The constant is intentionally located at module level in `scripts/build_db.py` rather than in `ARCHITECTURE.md` or in a shared config so that the refusal check lives with the code that uses it.

---

## 11. What this shakedown does NOT unblock

Repeated here so the list is in one place:

- Phase 4a collection — requires B2 backup active.
- Phase 4b saturation sweep — requires N=30 on three reference models, well beyond shakedown scope.
- Phase 4c human baseline acquisition — Mark's literature pull for Romney 1996.
- Phase 4d gate evaluation — runs on the canonical 12-model corpus, not shakedown data.
- v1 release — gated on Phase 4 gates passing.
- Any public or semi-public claim about any model.

---

*End of protocol. This document is binding for the 2026-04-20 shakedown cycle and any subsequent pre-Phase-4a instrumentation runs. Update before any future shakedown that broadens scope beyond what is specified here.*
