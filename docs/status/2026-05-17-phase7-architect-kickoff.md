# Phase 7 Architect Kickoff — Social Publishing Pipeline

**Status:** Draft for Mark's review. Pre-CDA-SME, pre-Coder.
**Date:** 2026-05-17
**Architect:** Opus
**Companion specs:** ARCHITECTURE.md §4.6 (canonical), §2 (boundary rule), §1.5 (framing), CLAUDE.md §6/§7/§9
**Phase 7 spec source:** ARCHITECTURE.md §4.6 lines 1181–1216 ("Social publishing pipeline")
**Inherits from:** Phase 6 closure 2026-05-16 (10/14 tasks landed; T1+T2 methodology page + T3+T4 DriftTracker blocked on data/copy)

---

## §1 Goal

Stand up `cdb_social/` — the social-publishing pipeline described in ARCHITECTURE.md §4.6 — as a Claude-Code-orchestrated cron job that detects post-worthy events in the published results store, drafts platform-specific posts via per-platform subagent prompts, queues drafts for Mark's human review, and (after approval) publishes to social platforms via their APIs. Phase 7's deliverable is a runnable end-to-end pipeline with at least one live platform integration (recommended: Bluesky) plus draft-only support for the other two. The pipeline must respect every guardrail in §1.5 and §1.5.4: drafters cannot emit forbidden vocabulary, cannot emit a numeric finding without its adjacent uncertainty, and cannot frame LSB as hypothesis-testing.

The success condition for Phase 7: a single `python -m cdb_social.cli run-once` invocation, given the current `apps/dashboard/public/data/` snapshot, produces zero-to-many sanitized drafts in `out/social/queue/pending/`, the review CLI surfaces each draft with verbatim text + a regenerated preview image (or no-image-yet sentinel), Mark approves with `y`, and `python -m cdb_social.cli publish` posts the approved item to Bluesky. The rest of the trigger types and the other platforms can ship as code-only stubs with disabled live firing.

---

## §2 Out of scope

The following are explicitly **not** in Phase 7. Each is either blocked on a prerequisite or assigned elsewhere.

1. **Drift trigger live firing (trigger #3).** Procrustes drift requires multi-date data per `model_version_returned`. The 0.2 corpus has at most one collection date per model version. The detector ships as a callable pure function; the cron's `--enable-trigger=drift` flag stays off until the next collection campaign produces multi-date data. The 0.15 threshold is a placeholder pending real distributions.

2. **Methodology-page deep links.** Phase 6 T1+T2 are blocked on Mark-authored prose. Until that lands, social posts link to `cogstructurelab.com/{domain}` (the article shell), not `/methodology`. The drafter prompt must use the configurable `methodology_url` field on `SocialDraft` so a one-line config change unblocks every post once T1+T2 ship.

3. **Server-side static chart export.** The browser-side PNG export (`apps/dashboard/src/lib/png-export.ts`, 1600×900 / 2000×2000, watermarked) is fully built — but it requires a DOM, an SVG tree, and the dashboard's React state. A server-side equivalent needs either (a) Playwright headless rendering of the live dashboard URL or (b) a matplotlib/altair re-implementation in Python. Both are heavier than one task. **Recommendation: ship Phase 7 with text-only drafts that include a dashboard URL.** Image generation deferred to Phase 7.5 (see §7 open decision 2). The FT designer is already working on the dashboard; coordinating with them on a re-usable export module is a fit there.

4. **Paid X (Twitter) API access decision.** X's free tier has been read-only since 2024. Posting requires a paid plan. Mark must choose whether to pay or whether to ship X as draft-export-only (post manually). See §7 open decision 1.

5. **LinkedIn partner-program approval.** LinkedIn's "share API" posting requires being in their partner program, which is hard to get. Recommend draft-export-only for LinkedIn in v1. See §7 open decision 1.

6. **Phase 8 public release work.** Repo go-public, license file shipping, methodology page finalization, Zenodo DOI, HuggingFace dataset release — all Phase 8.

7. **An admin web UI for review.** The §4.6 spec is explicit: v1 review is a CLI (`scripts/social_review.py`), v2 considers a web UI. Phase 7 is v1.

8. **First-post content selection.** Whether the inaugural post should be a "we're live" announcement about Phase 6 completion or whether to wait for the first organic trigger — see §7 open decision 5.

---

## §3 Decomposition into Coder-sized tasks

Seven tasks. Each is sized to fit in a single PR by a Sonnet Coder, with the gate verdicts noted.

### T1 — Schema and queue layout
**Goal:** Add `SocialTrigger`, `SocialDraft`, `SocialPostRecord` Pydantic models to `cdb_core/schemas.py`. Resolve the §4.6 vs §2 path conflict by adopting `out/social/queue/{pending,approved,published,failed}/` and `out/social/state/`. Update `docs/DATA_DICTIONARY.md` with a new §13 covering the three schema types and the on-disk layout.
**Scope:** ~120 LoC schema additions; ~80 lines DATA_DICTIONARY; one new directory tree under `out/social/` (gitignored except for a README).
**Depends on:** nothing.
**Gates:** **Architect sign-off required** (R6 — schema change). **CDA SME required** — the schema's `forbidden_terms_hit` field, the `confidence_score` semantics, and the `framing_check_passed` flag are all methodology-adjacent. UI/UX not required.
**Acceptance sketch:**
- `SocialTrigger` carries `trigger_type` enum (NEW_MODEL/NEW_DOMAIN/DRIFT/DIVERGENCE/MONTHLY_ROUNDUP), `detected_at`, `domain_slug | None`, `model_id | None`, `evidence` (dict for trigger-specific payload), `dedupe_key`.
- `SocialDraft` carries `draft_id` (SHA256 of trigger + platform + drafter_version + prompt_version), `trigger`, `platform` enum (BLUESKY/X/LINKEDIN), `text`, `image_path | None`, `suggested_posting_time`, `confidence_score`, `methodology_url`, `dashboard_url`, `forbidden_terms_hit: list[str]` (sanity-check field — must be `[]` for any draft that enters the queue), `framing_check_passed: bool`, `drafter_version`, `created_at`.
- `SocialPostRecord` carries the post-publish outcome: `draft_id`, `published_at`, `platform_post_id`, `platform_post_url`, `publish_status` (PUBLISHED/FAILED/DRY_RUN), `error_message | None`.
- `out/social/` layout: `queue/pending/{draft_id}.json`, `queue/approved/{draft_id}.json`, `queue/published/{YYYY-MM}/{draft_id}.json`, `queue/failed/{draft_id}.json`, `state/divergence_highs.json`, `state/seen_models.json`, `state/seen_domains.json`, `state/monthly_roundup.json`, `state/posted_dedupe_keys.json`.
- DATA_DICTIONARY.md §13 documents every field with units, allowed values, and the dedupe-key construction rule.
**Test plan:** pydantic round-trip tests for each schema; golden-file test for the directory README.

### T2 — Triggers (pure functions, no live firing for DRIFT)
**Goal:** Implement `cdb_social/triggers.py` as a set of pure functions over the published results store. Each trigger returns a `list[SocialTrigger]`; the cron orchestrator decides whether to draft.
**Scope:** ~250 LoC; one file (`triggers.py`); one fixtures directory under `tests/fixtures/social/published_data_snapshots/`.
**Depends on:** T1.
**Gates:** **CDA SME required** — divergence "new high" semantics, monthly-roundup content scope, and drift-threshold placeholder all need methodology sign-off. UI/UX not required.
**Acceptance sketch:**
- `detect_new_model(manifest, state) → list[SocialTrigger]` — compares `manifest.json` model lists against `out/social/state/seen_models.json`; emits one trigger per (domain, new_model) pair; first-run bootstrap writes the state file with current models and emits no triggers.
- `detect_new_domain(manifest, state) → list[SocialTrigger]` — same shape against `seen_domains.json`.
- `detect_drift(domain_results, state) → list[SocialTrigger]` — computes drift across `model_version_returned` × `collection_date`; returns `[]` until multi-date data is present (the function is correct; the data is not). Threshold from a top-of-module constant `DRIFT_THRESHOLD = 0.15` matching §4.6 line 1209.
- `detect_divergence(domain_results, state) → list[SocialTrigger]` — for each domain, computes the maximum pairwise distance in the similarity matrix; compares against `state/divergence_highs.json`; emits when the max strictly exceeds the prior high. First-run bootstrap records baseline highs and emits nothing.
- `detect_monthly_roundup(state, today) → list[SocialTrigger]` — at most one trigger per calendar month; updates `state/monthly_roundup.json` with last-fired YYYY-MM.
- Dedupe: every trigger carries a `dedupe_key`; the orchestrator skips triggers whose key is already in `state/posted_dedupe_keys.json`.
**Test plan:** fixture-driven tests with synthetic manifests / DomainResults; first-run bootstrap test (must emit zero); subsequent-run delta test; idempotency test (re-running with same state emits zero).

### T3 — Drafter framework + Bluesky drafter
**Goal:** Implement the LLM-driven drafter framework in `cdb_social/drafters/` with a base class that enforces the §1.5.4 vocab guardrails as a **post-generation validation step**, plus the Bluesky drafter. Each drafter takes a `SocialTrigger` + the relevant `DomainResult` and returns a `SocialDraft` or raises `DrafterRejectedException` on irrecoverable forbidden-vocab hits.
**Scope:** ~300 LoC: `base.py` (~120), `bluesky.py` (~80), validators (~100); per-platform system prompt files at `cdb_social/drafters/prompts/v1/{platform}.md`.
**Depends on:** T1, T2.
**Gates:** **CDA SME required** — the per-platform system prompts, the post-generation validator's forbidden-token list, the uncertainty-adjacency rule (any numeric in the post must have its CI within N tokens), and the "no hypothesis framing" rule all need explicit methodology gate. UI/UX not required (no visual surface).
**Acceptance sketch:**
- `DrafterBase` defines the contract: `draft(trigger, domain_result) → SocialDraft`. The base class **does not call the LLM**; subclasses do, but every output runs through `validate_draft()` before being returned.
- `validate_draft(text)` does three things: (1) substring-scan against the §1.5.4 left-column phrases plus the additional Register-1/Register-2 forbidden tokens; (2) regex-scan for "bare numeric findings" — any digit-containing token that is not followed by a CI-shaped neighbor within K tokens fails R10; (3) regex-scan for hypothesis-framing tokens ("we hypothesized", "confirms that", "proves that"). Failures populate `forbidden_terms_hit` and the draft is rejected — no quiet repair.
- Bluesky drafter uses Claude (matching the rest of the pipeline per CLAUDE.md ethos) via the standard `cdb_core` LLM helper. Anthropic prompt caching MUST be enabled on the system prompt per ARCHITECTURE.md §6.2.
- System prompt files are versioned: `cdb_social/drafters/prompts/v1/bluesky.md`, etc. Bumping a prompt requires a new directory (matching the §6 R7 prompt-versioning rule).
- `DrafterBase` constructs an immutable prompt context including: the relevant DomainResult numerics with CIs; the forbidden vocab table verbatim; the §1.5 corpus-lens framing block; the dashboard URL pattern; the platform-specific character/format constraints.
- Bluesky draft outputs: text ≤ 300 chars (Bluesky's limit), one URL, no thread structure (single-post platform), `image_path = None` for Phase 7 (per §2 out-of-scope item 3).
**Test plan:** fixture-replay tests with canned LLM responses (no real API in tests — `tests/fixtures/social/llm_responses/`); validator unit tests for each forbidden-vocab class; round-trip test (good draft passes, every category of bad draft is rejected with correct `forbidden_terms_hit` content).

### T4 — X and LinkedIn drafters (draft-only)
**Goal:** Implement the X and LinkedIn drafter subclasses. Both produce `SocialDraft` JSON; neither has live publishing in Phase 7. X drafter produces thread-shaped output (list of strings) for future use; LinkedIn drafter produces single-post longer-form output.
**Scope:** ~200 LoC: `x.py` (~80), `linkedin.py` (~80), shared thread utilities (~40); two system-prompt files.
**Depends on:** T3 (the base class and validator framework).
**Gates:** **CDA SME required** — same forbidden-vocab posture; the X thread format introduces a new structural surface that needs vocab enforcement *per tweet*, not per thread. UI/UX not required.
**Acceptance sketch:**
- X drafter returns `SocialDraft` with `text` as a `\n---\n`-delimited thread; validator runs per-segment.
- LinkedIn drafter returns a single long-form post; same validation rules.
- Both drafters honor the existing prompt-caching and prompt-versioning conventions from T3.
**Test plan:** fixture-driven tests for each drafter; thread-segmentation tests for X (no segment exceeds 280 chars); validator runs per-segment.

### T5 — Queue + review CLI
**Goal:** Implement `cdb_social/queue.py` (atomic move helpers between queue states) and `scripts/social_review.py` (the v1 human-review CLI per §4.6 line 1215).
**Scope:** ~250 LoC: `queue.py` (~120), `scripts/social_review.py` (~130).
**Depends on:** T1.
**Gates:** **CDA SME required** for the review-CLI display — the prose the reviewer sees while making the y/n/edit call must respect §1.5.4 (e.g., column headers, framing of what the draft is doing). UI/UX not required because the CLI is operator-internal per Mark's `feedback_ui_polish_scope.md` memory — internal ops surfaces ≠ public dashboard.
**Acceptance sketch:**
- `queue.move(draft_id, from_state, to_state)` is atomic via `os.rename` within the same filesystem; raises if `from_state` is wrong.
- `scripts/social_review.py` lists `pending/` drafts oldest-first, shows each one with: trigger summary, draft text verbatim, validator results, dashboard URL, suggested posting time, confidence score. Accepts `y`/`n`/`e` (edit text in `$EDITOR`)/`s` (skip)/`q` (quit). `y` moves to `approved/`; `n` moves to `failed/` with reason; `e` opens editor, re-runs the validator on the edited text, moves to `approved/` only if validation passes (otherwise back to `pending/` with the edit history appended).
- Edits never overwrite the original `text` field; the schema supports `text_history: list[str]` for audit.
**Test plan:** pytest with `monkeypatch` on stdin/stdout for the CLI flows; queue atomicity test (kill the process mid-move, ensure no half-state).

### T6 — Bluesky publisher + cron orchestrator
**Goal:** Implement `cdb_social/publisher.py` (Bluesky-only live publish via the AT Protocol; X and LinkedIn raise `PublisherNotEnabled`) and `cdb_social/cli.py` (the entry point invoked by GitHub Actions cron).
**Scope:** ~280 LoC: `publisher.py` (~140), `cli.py` (~140); one new `.env.example` entry `BLUESKY_HANDLE` + `BLUESKY_APP_PASSWORD`.
**Depends on:** T1, T2, T3, T5.
**Gates:** No CDA SME (pure transport mechanics). UI/UX not required.
**Acceptance sketch:**
- `publisher.publish(draft) → SocialPostRecord` dispatches by `draft.platform`. For Bluesky, uses the `atproto` Python client (already a well-maintained lib). Reads creds from env; never reads from disk outside `.env`. Returns `SocialPostRecord` with the platform post URL.
- Failure handling: any HTTP error moves the draft to `queue/failed/` with the error verbatim; the cron continues to the next approved draft. Two failure modes are distinguished: transient (retry next run) and terminal (do not retry).
- `cli.py` subcommands: `run-once` (detect triggers → draft → queue), `review` (delegates to scripts/social_review.py), `publish` (drain approved → publisher → published/failed), `status` (counts per queue state).
- `--dry-run` flag on `publish` writes to `queue/published/` with `publish_status=DRY_RUN` and no API call.
- No real Bluesky API calls in tests — `tests/fixtures/social/bluesky_responses/` with `requests_mock` or equivalent.
**Test plan:** mocked-HTTP publish tests; failure-mode tests; dry-run end-to-end test; CLI subcommand smoke tests.

### T7 — GitHub Actions cron + docs
**Goal:** Add `.github/workflows/social-pipeline.yml` (cron) + boundary CI check + documentation pass. Update ARCHITECTURE.md §4.6 to reflect the realized paths and `out/social/queue/` resolution; add a CLAUDE.md §9 pitfall for the forbidden-vocab post-generation validation pattern.
**Scope:** ~150 LoC YAML + ~120 lines docs.
**Depends on:** T1–T6.
**Gates:** No CDA SME (the doc updates are descriptive, not new methodology). UI/UX not required.
**Acceptance sketch:**
- `social-pipeline.yml` runs on `cron: '0 14 * * *'` (14:00 UTC daily). Steps: checkout, install, run `python -m cdb_social.cli run-once`, commit any new state files. **The cron does not auto-publish.** Mark's CLI run is the publish trigger.
- CI boundary check: `.github/workflows/ci.yml` gets a new step `cdb-social-boundary` that greps for `from cdb_analyze` or `import cdb_analyze` inside `packages/cdb_social/` and rejects on hit (mirrors the existing `cdb_publish ← cdb_collect` check pattern). Also greps for writes to `data/raw/` and `data/processed/` from within `cdb_social`.
- ARCHITECTURE.md bumps to **v0.7.4**: §4.6 amended to record the realized `out/social/queue/` layout and the §2 boundary-rule resolution; one-line changelog entry.
- CLAUDE.md §9 gets pitfall #16: "Letting a drafter's LLM emit a bare numeric finding without uncertainty. R10 enforcement on social posts is a *post-generation validator*, not a prompt-side suggestion — the prompt asks for CI-bracketed numerics, but the validator is the gate."
- DATA_DICTIONARY.md cross-reference added if anything from T1 changed shape during implementation.
**Test plan:** workflow file YAML-lints; CI step tested via a synthetic offending diff.

---

## §4 Suggested task ordering

```
T1 (schema + paths)
 │
 ├─→ T2 (triggers)
 │    │
 │    └─→ T3 (drafter base + Bluesky drafter)
 │         │
 │         ├─→ T4 (X and LinkedIn drafters, draft-only)   ← parallelizable with T5/T6
 │         │
 │         └─→ T6 (publisher + cli)
 │              │
 │              └─→ T7 (cron + docs)
 │
 └─→ T5 (queue + review CLI)   ← parallelizable with T3/T4 once T1 lands
```

Parallelizable groups:
- **After T1:** T2 and T5 can run in parallel (independent surfaces).
- **After T3:** T4 (other drafters) and T6 (publisher) can run in parallel.

Strict-serial path is T1 → T2 → T3 → T6 → T7. T4 and T5 are off-path.

---

## §5 Schema additions (Architect sign-off required per CLAUDE.md §6 rule 6)

Three new types in `cdb_core/schemas.py`. Each requires a matching `docs/DATA_DICTIONARY.md` §13 entry in the same PR (Reviewer rule R7). Mark must ratify these before T1 starts:

1. **`SocialTrigger`** — represents a post-worthy event. Fields: `trigger_type: TriggerType`, `detected_at: datetime`, `domain_slug: str | None`, `model_id: str | None`, `evidence: dict[str, Any]`, `dedupe_key: str` (SHA256[:16] of trigger_type + domain + model + evidence content-hash).

2. **`SocialDraft`** — the JSON file persisted in `queue/pending/`. Fields: `draft_id: str`, `trigger: SocialTrigger`, `platform: Platform`, `text: str`, `text_history: list[str] = []`, `image_path: str | None`, `suggested_posting_time: datetime`, `confidence_score: float`, `methodology_url: str`, `dashboard_url: str`, `forbidden_terms_hit: list[str] = []`, `framing_check_passed: bool`, `drafter_version: str`, `prompt_version: str`, `created_at: datetime`.

3. **`SocialPostRecord`** — the publish outcome. Fields: `draft_id: str`, `published_at: datetime`, `platform_post_id: str | None`, `platform_post_url: str | None`, `publish_status: PublishStatus`, `error_message: str | None`.

Plus three enums: `TriggerType {NEW_MODEL, NEW_DOMAIN, DRIFT, DIVERGENCE, MONTHLY_ROUNDUP}`, `Platform {BLUESKY, X, LINKEDIN}`, `PublishStatus {PUBLISHED, FAILED, DRY_RUN, RETRY_PENDING}`.

**None of these touch `InformantRecord` or `GroundingRef`.** They are net-new types for a net-new package. They are still binding once landed.

---

## §6 Doctrine doc updates expected during Phase 7

| Doc | Update | When |
|---|---|---|
| `cdb_core/schemas.py` | Three new types + three enums (T1) | T1 |
| `docs/DATA_DICTIONARY.md` | New §13 — social pipeline schemas + on-disk layout (T1) | T1 |
| `ARCHITECTURE.md` | Bump to v0.7.4. §4.6 amended to record `out/social/queue/` resolution (was `data/social_queue/` in original spec; conflicts with §2 line 385 boundary rule). Changelog entry. (T7) | T7 |
| `CLAUDE.md` | §9 pitfall #16 — post-generation validator pattern for drafter forbidden-vocab compliance (T7) | T7 |
| `.env.example` | New entries: `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`. (X/LinkedIn entries commented out as decision pending.) (T6) | T6 |
| `SECURITY_AND_HARDENING.md` | Possibly: new entry in §8 for Bluesky app-password handling. To be assessed at T6 review time; if Bluesky's app-password posture is already covered by the generic "credentials live in .env + 1Password" boilerplate, no edit needed. | T6 (conditional) |

The single **path-conflict resolution** that ARCHITECTURE.md needs to record: §4.6 line 1197 says `data/social_queue/pending/`; §2 line 385 says `cdb_social` writes only to `out/social/`. The realized layout is `out/social/queue/{pending,approved,published,failed}/` + `out/social/state/`. v0.7.4 records the resolution.

---

## §7 Open decisions for Mark

These need an answer before T2 (triggers) and T3 (drafters) start substantive work. T1 can begin immediately.

1. **Platform priority. Recommendation: Bluesky-only live, X + LinkedIn draft-only.**
   - Bluesky's API is free, open, and easy to integrate. AT Protocol is well-documented; the `atproto` Python client is mature.
   - X requires paying for the API tier that allows posting (~$100/mo at the floor). Probable answer is "not now"; ship X as draft-export-only and post manually in v1.
   - LinkedIn requires partner-program approval that is hard to get. Ship LinkedIn as draft-export-only; revisit if/when traffic warrants applying.
   - **Decision needed:** confirm Bluesky-only live publishing, or override with X live (which requires X paid-tier signup before T6 can land its publisher).

2. **Static chart export — Phase 7 or Phase 7.5?**
   - Browser-side PNG export is already shipped (`apps/dashboard/src/lib/png-export.ts`).
   - Server-side rendering needs Playwright headless or a matplotlib re-implementation; both are ~1 task each.
   - **Recommendation:** defer to Phase 7.5. Phase 7 v1 ships text-only posts with the dashboard URL. The FT designer is already on the dashboard; a re-usable export module is a natural fit for that scope. Recommend Mark coordinate with the designer rather than build it twice.
   - **Decision needed:** confirm "Phase 7 = text-only posts" or override to include in-scope image generation.

3. **Drift trigger — code-only stub or skip entirely?**
   - **Recommendation:** ship the trigger function (T2) as code-only, with the cron orchestrator passing `enable_drift=False` until multi-date data exists. Threshold (0.15) is a placeholder. The function is testable today against synthetic multi-date fixtures and ready to fire the day collection produces real multi-date data.
   - **Decision needed:** confirm code-only stub.

4. **Drafter LLM choice.**
   - **Recommendation:** Claude (Opus or Sonnet, settled at drafter-instantiation time per platform) for consistency with the rest of the pipeline. The Anthropic prompt-caching requirement (§6.2) applies to drafter system prompts; this only works if the LLM is Anthropic's.
   - **Decision needed:** confirm Claude, or override.

5. **First post target.**
   - **Recommendation:** wait for the first organic trigger to fire. The pipeline is more credible if its first post is a substantive finding ("we added GPT-5.5 to the family domain; here's where it sits") than if it is a meta-announcement ("we shipped a thing").
   - Alternative: a hand-drafted "we're live" post that goes through the same review/publish path to exercise the pipeline end-to-end before any auto-detected trigger fires.
   - **Decision needed:** Mark's call.

---

## §8 Risks (top 5)

1. **Drafter forbidden-vocab leakage under LLM generation pressure.** LLMs prompted to write "engaging" social copy reach for "believes," "thinks," "worldview" because that's how training corpora describe agents. Mitigation: post-generation validator is the gate, not the prompt. Any draft containing a forbidden token is rejected, not repaired. Drafter is graded on the validation pass rate, not on creativity. **The CDA SME's review of the drafter prompts in T3 is the highest-leverage gate in Phase 7.**

2. **Platform API instability — especially X.** X's API has changed twice in the last 18 months; pricing changed three times. Even Bluesky, despite being open, is operationally young — outages and breaking changes are possible. Mitigation: the publisher's failure-handling is structured (transient vs. terminal), failed posts land in `queue/failed/` for inspection rather than getting lost, and live publishing is gated behind a CLI invocation (the cron does not auto-publish), so an API regression cannot fire a bad post.

3. **Human-review fatigue.** If the cron emits 10 drafts/day and Mark has to review each one, the pipeline becomes friction rather than leverage. Mitigation: the trigger dedupe logic (T2) is conservative — every trigger has a stable `dedupe_key`; re-firing the same event does not produce a new draft. Plus, several trigger types fire rarely by design (new model: weeks; new domain: months; monthly roundup: once a month; drift: blocked).

4. **Methodology-page-link-is-null until T1+T2 ship.** Drafters can't link to `/methodology` because it doesn't exist. Mitigation: drafters link to the per-domain article shell (`/{domain}`) instead and carry a configurable `methodology_url` field. Once T1+T2 land, a single config bump points drafters at the right URL. **Risk if not addressed:** social posts go out with broken links.

5. **Drift threshold (0.15) is unvalidated.** The §4.6 spec sets 0.15 as a placeholder; no real distribution justifies it. Drift trigger should not fire on its own until the CDA SME reviews real multi-date drift scores. T2 ships the threshold as a constant; the cron's `enable_drift=False` flag is the lockout. Removing the lockout is a future task with its own SME review.

---

## §9 Estimated timing

Per Mark's `project_campaign_timing.md` memory, LSB tasks run in hours. Per-task sub-day estimates:

| Task | Coder time | Reviewer time | Gate verdicts |
|---|---|---|---|
| T1 — schemas + queue layout | 2–3 hours | 30 min | Architect + CDA SME |
| T2 — triggers | 3–4 hours | 45 min | CDA SME |
| T3 — drafter base + Bluesky | 4–6 hours | 1 hour | CDA SME (heaviest review) |
| T4 — X + LinkedIn drafters | 2–3 hours | 30 min | CDA SME (lighter — same posture as T3) |
| T5 — queue + review CLI | 2–3 hours | 30 min | CDA SME (light) |
| T6 — publisher + cli | 3–4 hours | 30 min | none |
| T7 — cron + docs | 1–2 hours | 30 min | none |

**Total:** ~20–25 hours of Coder time plus gating overhead. Realistic calendar shape: 2–3 working days from T1 kickoff to T7 close, assuming Mark dispatches gate reviews promptly and assuming no rework cycles.

---

*End of Phase 7 kickoff. Next action: ratify §5 schema additions; resolve the §7 open decisions; then auto-dispatch T1 to the CDA SME for methodology gate, followed by Coder.*

---

## §10 Mark's ratifications (2026-05-17)

All Architect recommendations accepted as-stated.

- **§5 schema additions:** ratified. The three new types (`SocialTrigger`, `SocialDraft`, `SocialPostRecord`) and three enums (`TriggerType`, `Platform`, `PublishStatus`) land in `cdb_core/schemas.py` at T1 with matching `docs/DATA_DICTIONARY.md` §13 update in the same PR.
- **§7.1 Platform priority:** Bluesky-only live publish; X + LinkedIn draft-only.
- **§7.2 Static chart export:** deferred to Phase 7.5; Phase 7 ships text-only posts with the dashboard URL.
- **§7.3 Drift trigger:** code-only stub; cron passes `enable_drift=False` until multi-date data exists.
- **§7.4 Drafter LLM:** Claude (Opus or Sonnet, per drafter instantiation), for Anthropic prompt-caching parity.
- **§7.5 First post target:** wait for the first organic trigger; no hand-drafted "we're live" meta-announcement.

Phase 7 dispatch resumes. T1 → CDA SME → Coder → Reviewer → Tester.

