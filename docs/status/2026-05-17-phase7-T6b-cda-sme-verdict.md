---
filed: 2026-05-17
reviewer: CDA SME agent (Opus)
task: Phase 7 T6b — Local Flask admin console
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 7 T6b — CDA SME verdict on the local Flask admin console

**VERDICT: PASS-WITH-NOTES**

T6b is a **light** CDA SME gate per kickoff §11.6. The admin console
is operator-internal (loopback bind, single operator), and the bulk of
its methodology-bound display copy is **already inherited verbatim
from T5 §5.5 / §5.7 (review-CLI bindings) and from T6a's
`digest.format_trigger_summary()`**. The Coder reuses both — that
inheritance is the structural correctness this verdict relies on.

The new T6b-specific surfaces the kickoff exposes are: (1) the
"Request draft" button (the only surface in the Phase 7 pipeline where
an LLM call is invoked by an operator click); (2) the "Publish"
button (the only surface where the Bluesky API is hit); (3) the four
`confirm.html` interstitials for the destructive POST actions; (4)
the error pages for drafter / Anthropic / Bluesky failures; (5) the
queue-state navigation copy; and (6) the rendered Bluesky-handle /
methodology-URL display.

Across these six new surfaces, the CDA SME finds **no hard
methodology hazard** — but there are **ten binding display-copy
narrowings** corresponding 1:1 to the Orchestrator's ten questions.
Each is listed in §5 with the exact string the Flask template
renders.

Headline rulings (highlighted by Orchestrator request):

- **Question 1 — "Request draft" button text:** **`Draft via LLM`**
  (or, if a single-line label is too terse, `Draft via LLM (Claude)`).
  Rejected: `Generate draft` (the `generate` verb obscures that an
  external LLM call is happening); `Request draft` (too generic; could
  be read as "request a hand-written draft"); `Compose draft via LLM`
  ("compose" implies the operator authors the post). The chosen label
  makes the §11.1 B-1 binding visible at the click surface: the
  operator's click is **the** moment an LLM API call is made on their
  behalf. See §5.1.

- **Question 9 — Publish irreversibility language:** **`This will
  post to Bluesky as @{handle}. Once posted, deletion is best-effort —
  the timestamp and any platform-side cache may persist.`** Rejected:
  the bare `"Once posted, this action is irreversible."` (overstates;
  Bluesky deletion works for most cases — the irreversibility is
  about *the record of having posted*, not the post text itself). The
  recommended wording is technically accurate at the platform-mechanics
  layer and methodologically neutral (no claim about the post's
  content). See §5.9.

The remaining eight rulings (Questions 2–8, 10) are narrowings of
display copy that mostly reinforce T5 / T6a bindings at the Flask
template layer. Of those eight, the only one with broader
architectural implications is Question 3's "estimated tokens"
sub-question: the answer is **omit token-count displays entirely**
(CLAUDE.md R14 — no software-side spend gates; the `est. tokens` field
on the confirmation page is a spend-cap surrogate even if no enforcement
exists).

Coder dispatch may proceed on T6b with the ten binding notes in §5
applied. The Reviewer enforces. No Architect re-planning required;
no schema-touch required.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | N/A | T6b is a Flask admin UI; no CDA elicitation protocol surface is touched. The console acts on already-validated `SocialDraft` and `SocialTrigger` objects. |
| Analytical validity | N/A | T6b performs no analytical computation. It triggers a drafter LLM call (which has its own T3-bound validation) and dispatches Bluesky publish calls. The numerics displayed (e.g., `gap_delta`, `procrustes_distance`) are read from already-computed evidence dicts via T5's `format_trigger_summary()`. |
| Claims validity | PASS-WITH-NOTES | Six new T6b-specific surfaces with display-copy methodology weight: button labels (§5.1, §5.2), confirmation pages (§5.3), error messages (§5.4), framing-check display (§5.5), URL labeling (§5.6), self-rating label (§5.7), filesystem paths (§5.8), publish-irreversibility wording (§5.9), MONTHLY_ROUNDUP wording (§5.10). All ten rulings narrow display copy; none re-architect. The Coder reuses T5 / T6a bindings verbatim where applicable and renders the §5 binding wording for the new surfaces. |
| Audience translation | PASS-WITH-NOTES | The audience is exactly one person — Mark — operating in browser, possibly under decision pressure (a real trigger fired, a real model release happened, time-of-day matters for posting). The display copy must be: scan-fast, methodology-precise, and operator-role-respecting (per the T5 §5.5 ruling — the operator is the reviewer, not the author). The "Publish" surface in particular must be unambiguous about what the second click does and what is recoverable; §5.9's wording handles this without overclaiming. |

**Register compliance:** **PASS** — T6b inherits the T5 §5.7 / T6a
`format_trigger_summary` register-compliant wording verbatim
(`max pairwise distance` for DIVERGENCE, `Procrustes distance` for
DRIFT, `monthly cross-domain categorical-structure roundup` for
MONTHLY_ROUNDUP). No new Register-1 / Register-2 surfaces are
introduced.

**Vocabulary compliance:** **PASS-WITH-NOTES** — scanned every new
T6b-authored string surface implied by §11.6 (the six routes' page
copy, button labels, confirmation interstitials, error messages,
nav copy). The single §1.5 hazard surfaced and fixed: Question 1's
button labels (some candidates — `Generate draft` — obscure the LLM
call; `Compose draft via LLM` confuses the operator role). The
binding label is `Draft via LLM` per §5.1.

The MONTHLY_ROUNDUP carry-forward from T5 §5.11 (the ARCHITECTURE.md
§4.6 line 1211 "state of cultural alignment" prose still pending T7
doc-fix) is **already defused** in T6a's `digest.format_trigger_summary`
and T5's `scripts/social_review.py`. T6b inherits the defused
wording — no T6b-specific surface re-introduces the pre-amendment
phrasing.

---

## 2. Rationale on the ten methodology questions

### 2.1. Question 1 — "Request draft" button labeling

The Orchestrator surfaced four candidates: `Request draft`,
`Draft a post`, `Generate draft`, `Compose draft via LLM`. The
constraint is that the button must make it explicit an LLM call
happens on click (per §11.1 B-1 — the **only** place an LLM gets
invoked in the social pipeline).

**Ruling — `Draft via LLM`** as the primary label; if a single-line
constraint forces fuller disclosure, **`Draft via LLM (Claude)`** is
also approved.

Rejected candidates:

- `Request draft` — too generic. "Request" implies a queue / async
  workflow ("request a report from analytics"). The operator might
  click expecting a wait state and ambient processing; instead, the
  click is a synchronous LLM API call.

- `Draft a post` — does not surface the LLM invocation. The
  operator could reasonably read this as "open a form where I
  write the post." The §11.1 B-1 binding (no autonomous LLM calls
  in production paths) loses its visible enforcement at the click
  surface.

- `Generate draft` — the verb `generate` is borderline. It is
  understood inside the AI/LLM community but ambiguous to the
  general operator. More importantly, it can read as "auto-generate
  without my input," which is the autonomy posture Mark explicitly
  rejected in §11.1.

- `Compose draft via LLM` — the verb `compose` implies operator
  authorship ("I will compose"). Conflicts with T5 §5.5's
  operator-as-reviewer-not-author posture. The compose framing also
  reads as if the operator and the LLM are co-authoring, which is
  not what the architecture does.

**Why `Draft via LLM` works:**

1. **Verb is neutral about authorship.** "Draft" is a noun-as-verb
   here — "produce a draft of." It does not claim the operator
   authors; it does not claim full autonomy. It is the right
   match for the actual operation: "instruct the LLM to draft."

2. **`via LLM` makes the API call visible.** The operator sees, at
   the click surface, that the action involves an external model
   call. This is the §11.1 B-1 transparency posture realized at
   the UI layer.

3. **Compact and scan-fast.** Three words, well under most button-
   length budgets, readable at the index page where multiple
   triggers may have their own "Draft via LLM" buttons.

**Alternative if Mark prefers more disclosure:** `Draft via LLM
(Claude)`. The parenthetical names the model family per
ratification §10 (Claude is the chosen drafter LLM). This is
acceptable. The button text is not space-constrained on a desktop
browser at the small operator population.

### 2.2. Question 2 — "Publish" button labeling

The Orchestrator surfaced four candidates: `Publish to Bluesky`,
`Publish`, `Post`, `Send to Bluesky`. The constraint is that the
label make the irreversibility / destination visible.

**Ruling — `Publish to Bluesky`** as the primary label.

Rejected candidates:

- `Publish` — too generic. Sufficient when the destination is
  unambiguous from context, but at this surface the destination is
  *the entire point* of the second click. A bare "Publish" reads
  as "save to internal queue" or "move to next state" — which
  conflates this terminal action with the intermediate "Approve"
  click.

- `Post` — matches platform vernacular but obscures the destination.
  "Post" is what users on Bluesky / X / etc. do to the platform;
  applied to the admin console it is ambiguous (post to whom?).

- `Send to Bluesky` — implies a queued / scheduled posting. The
  click is synchronous and the post is live immediately. "Send"
  understates the immediacy.

**Why `Publish to Bluesky` works:**

1. **Action verb matches the operation.** Publishing is the canonical
   verb for irreversible-on-the-public-record actions across most
   ops tooling and content systems.

2. **Destination is in the label.** The operator does not have to
   read surrounding context to know which platform receives the call.

3. **Distinguishable from "Approve."** The "Approve" button on the
   prior screen says `Approve` (no platform suffix); the "Publish"
   button on this screen says `Publish to Bluesky`. The asymmetry
   reinforces "two distinct actions."

**For X / LinkedIn drafts** (not live in Phase 7 per kickoff §10):
the publish-button equivalent should be **disabled** with a label
reading **`Publishing not enabled for {Platform}`** plus a sibling
**`Download draft text`** link. This matches kickoff §11.6 acceptance
criterion 5. See §5.2.

### 2.3. Question 3 — Confirmation pages

The Orchestrator surfaced four destructive POST actions, each
hitting a `confirm.html` interstitial. The methodology questions
were (a) whether to display token-count estimates, (b) the
confirmation wording for approve / reject / publish.

**Sub-ruling on token-count display: OMIT entirely.** No `est.
tokens: ~X` line on the "Request draft" confirmation page. Reason:
CLAUDE.md R14 (no software-side spend gates) — even a non-enforcing
display of estimated tokens is a spend-cap surrogate, and the
forbidden-token CI grep would flag any phrasing that quantifies
expected cost in a confirmation context. The §1.5.4 hazard is
secondary; the R14 hazard is primary. <!-- noqa: spend-gate-check -->

The operator does not need a token estimate to make the call. The
single trigger row already on screen is the information needed.

**Confirmation wording for each action (binding at §5.3):**

| Action | Confirmation page header | Confirmation body | Confirm button label |
|---|---|---|---|
| `Draft via LLM` | `Draft via LLM?` | `This will invoke the {drafter_version} drafter on trigger {dedupe_key} via Claude. A new draft will land in queue/pending/ on success. Drafter failures (forbidden vocabulary, missing CI, etc.) are surfaced; no draft is created on failure.` | `Yes, draft via LLM` |
| `Approve` | `Approve draft?` | `Approve draft {draft_id}. The draft moves to queue/approved/. This does not publish. You will need to click "Publish to Bluesky" on the approved-draft page to send the post.` | `Yes, approve` |
| `Reject` | `Reject draft?` | `Reject draft {draft_id}. The draft moves to queue/failed/ with the selected reason. This cannot be undone via the UI — to re-queue, copy the draft text from queue/failed/{draft_id}.json and re-submit via "Draft via LLM."` (rejection-reason `<select>` per the five-code T5 §5.3 enum follows.) | `Yes, reject` |
| `Publish to Bluesky` | `Publish to Bluesky?` | `This will post to Bluesky as @{handle}. Once posted, deletion is best-effort — the timestamp and any platform-side cache may persist. The post text below will be sent verbatim.` (full draft text rendered below; `methodology_url` / `dashboard_url` shown.) | `Yes, publish to Bluesky` |

The `Cancel` button is present on every confirmation page; cancel
returns to the prior page with no state change.

**Why each confirmation body works:**

- `Draft via LLM` body **names what happens** (a drafter call via
  Claude) and **names the failure mode** (validator rejection
  surfaces; no silent failure). It does NOT display a token
  estimate (per R14).

- `Approve` body **distinguishes approve from publish** explicitly
  ("This does not publish."). The §11.1 B-2 two-click contract is
  surfaced at the click point.

- `Reject` body **names the destination state** (queue/failed/) and
  **names the recovery path** (manual re-submit). This is the
  irreversibility-acknowledgment for the reject side.

- `Publish to Bluesky` body **uses the §5.9 binding wording** for
  irreversibility — not the overstated "this action is irreversible"
  framing.

### 2.4. Question 4 — Error messages

The Orchestrator surfaced four failure surfaces.

**Sub-ruling A — DrafterRejectedException display:**

Exposes the four canonical T3 §5.11 `framing_checks` keys verbatim
(per T5 §5.2 binding) and the matched forbidden terms. Wording:

```
Drafter call did not pass validator. No draft was created.

Failed checks:
  cognition_attribution    — matched: "believes"
  hypothesis_framing       — matched: "this proves"
  bare_numeric_without_ci  — bare numeric "0.84" without adjacent CI

The drafter produced text containing the matched terms / patterns.
This is a guardrail, not an operator error. To draft this trigger,
re-click "Draft via LLM" — the LLM may produce a clean draft on
retry. If retries persistently fail, the v1 system prompt may need
a v2 bump (see CDA SME T3 §5.8).
```

Subject is the validator (per T5 §5.5 — neutral, not operator-
shaming). The "guardrail, not an operator error" sentence is added
specifically for the admin-console surface because the click was the
operator's; absent that line, the operator might read the failure as
"I did something wrong."

**Sub-ruling B — Anthropic API failure display:**

Generic at the operator-facing layer; full error in the page-source /
log. Wording:

```
Drafter call failed (Anthropic API error).

This is a transport-layer failure, not a guardrail rejection.
The underlying error: {error_type}. The draft was not created.

You can:
  • Click "Draft via LLM" again to retry.
  • Check Anthropic status if retries keep failing.
```

The `{error_type}` is a short tag (e.g., `RateLimit`, `Auth`,
`Network`, `ServerError`) — not the full traceback in the rendered
page. Full traceback goes to the server log only. This avoids
leaking auth-related details to anyone with browser access to
loopback (the loopback bind already restricts the audience, but
defense-in-depth).

**Sub-ruling C — Bluesky publisher failure display:**

Generic at the operator-facing layer with retry guidance.
Wording:

```
Publish to Bluesky failed.

The draft was NOT posted. The draft remains in queue/approved/ and
can be retried.

Failure category: {transient_or_terminal}.
Underlying error tag: {error_type}.

Transient failures (network, rate limit) can be retried by
returning to the approved-draft page and clicking "Publish to
Bluesky" again. Terminal failures (auth, account suspension) need
operator intervention — check the server log for the full traceback
and resolve the underlying issue before retrying.
```

The transient/terminal distinction is the T6 §11.6 publisher
contract (kickoff §3 T6 + §11 amendment). The error tag is short;
the traceback is in the log.

**Sub-ruling D — Edit-flow validator failure on the admin console:**

T6b's edit flow is the Flask-template equivalent of T5's edit-then-
validate flow. The wording **must inherit T5 §5.5 verbatim** at
the page-copy layer: `Edit did not pass validator.` is the header;
`Failed checks:` is the list label; the per-check evidence lines
follow the T5 templates. The Coder reuses `_display_edit_failure`'s
logic / wording, transposed to HTML rendering.

### 2.5. Question 5 — Framing-checks display labels

The Orchestrator surfaced: keys-verbatim vs friendly-labels.

**Ruling — keys verbatim, matching T5 §5.2 binding.**

The four canonical T3 §5.11 keys (`hypothesis_framing`,
`cognition_attribution`, `bare_numeric_without_ci`,
`register_boundary`) render verbatim. Pass/fail uses a visible-
distinct rendering (the Coder picks; suggested: HTML class
`framing-pass` / `framing-fail` with CSS color, or a leading ✓ / ✗
glyph following T5's symbol choice).

**Why keys verbatim:**

1. **Audit-trail parity with T5.** The same keys appear in the CLI
   (T5), the email digest (T6a, in the embedded summary), and the
   admin console (T6b). An operator who learns the four-key
   vocabulary once can use it across all three surfaces.

2. **Friendly labels are operator-facing editorial decisions** that
   could subtly reframe the check's semantic. "Cognition attribution"
   has a precise meaning (the §1.5.4 row 1-6 boundary); "No cognition
   attribution" as a friendly label reads as a moral judgment.

3. **The operator is technical.** Per `feedback_ui_polish_scope.md`,
   the admin console is operator-internal. The display-polish
   budget is "minimum viable functional" — the keys are exactly
   the right register.

**One small addition allowed:** an optional inline tooltip / `title`
attribute on each key, rendering the T3 §5.11 docstring excerpt
(e.g., `title="Scans for §1.5.4 rows 11-12 + 3 subtler hypothesis-
framing phrases per T3 §5.3."`). The tooltip is non-binding; the
Coder may add or omit. The key itself is binding.

### 2.6. Question 6 — Bluesky handle / methodology URL display

The Orchestrator surfaced: link-label "details" / "more" (per T3
§5.5) vs raw URL display.

**Ruling — render both, distinguished by context.**

- **Inside the post text rendering** (the draft preview the
  operator sees on the draft page): render whatever the drafter
  produced **verbatim**. The drafter's prompt teaches it to label
  the link "details" or "more" (per T3 §5.5). The admin console
  does not re-label the post body — that would diverge the display
  from what gets published.

- **In the admin console's own UI chrome** (the panel showing
  `methodology_url: <url>` and `dashboard_url: <url>` as metadata
  fields): render the raw URL as a clickable link with the URL
  itself as the link text. This is the audit-affordance view; the
  operator needs to verify the URL before publishing.

The two contexts are clearly distinguished by HTML structure: the
post body lives in a `<pre>` or `<div class="post-body">` rendering
the draft `text` verbatim, while the URL audit panel lives in a
sibling `<dl>` or `<table>` block clearly outside the post body.

**Why this split works:**

1. **The published post text is what the public sees.** It must
   match exactly. Re-labeling it in the admin UI would create a
   gap between admin-UI display and the actual Bluesky post.

2. **The metadata audit panel is operator-facing only.** Showing
   the raw URL there lets the operator verify the destination
   matches expectations (e.g., the article-shell URL is right; the
   methodology URL is the expected per-domain shell until Phase 6
   T1+T2 ship).

3. **No re-labeling means no §1.5 framing hazard.** The admin
   console doesn't mint new methodology copy; it shows what the
   drafter produced + the URLs as metadata.

### 2.7. Question 7 — "Drafter self-rating" label

The Orchestrator asked for confirmation that "Drafter self-rating"
(not "Confidence") is used.

**Ruling — confirmed; binding. T1 §5.4 + T5 §5.1 carry forward to
T6b verbatim.**

Every Flask template that surfaces a `SocialDraft.drafter_self_rating`
value uses the header / label `Drafter self-rating`. Forbidden
alternates (Reviewer enforces): `Confidence`, `Confidence score`,
`Quality score`, `Rating`.

**Display format:** `Drafter self-rating: 0.50` (two decimal places,
matching T5 §5.1).

**Optional inline note** under the field (Coder may add): `(fixed
at 0.5 for v1; not calibrated — see T3 §5.6)`. Non-binding.

### 2.8. Question 8 — Filesystem paths in the UI

The Orchestrator surfaced: filesystem paths like
`out/social/queue/pending/{draft_id}.json` displayed in the UI for
operator orientation. The question was whether sanitization applies.

**Ruling — display verbatim; no sanitization needed at the loopback-
bound admin console.**

Three reasons:

1. **The audience is one person on the loopback interface.** The
   security boundary is the loopback bind. Path-information leakage
   to a remote attacker is not a threat model T6b faces.

2. **The paths are operationally informative.** When debugging
   "where did this draft go?", the operator wants to see the
   filesystem path to grep / inspect / re-route. Sanitizing the
   path defeats the operational affordance.

3. **The publish-layer redaction regex** (e.g., `data/raw/*`
   matchers) is a public-surface mechanism for the published
   failures JSON / dashboard surfaces. It does not apply to
   operator-internal admin tooling.

**Display posture:** filesystem paths render as monospace strings
in `<code>` tags. The Coder may shorten the displayed path to a
relative form (e.g., strip the project-root prefix) for readability;
this is a Coder convenience choice, non-binding.

### 2.9. Question 9 — "Irreversible" language on publish

The Orchestrator surfaced three candidates. Each was evaluated for
technical accuracy + audience-translation precision.

**Ruling — the recommended wording:**

```
This will post to Bluesky as @{handle}. Once posted, deletion is
best-effort — the timestamp and any platform-side cache may persist.
```

Rejected candidates:

- `Once posted, this action is irreversible.` — overstates the
  technical reality. Bluesky supports `deletePost` via the AT
  Protocol; the post text **can** be removed from the operator's
  view of the timeline. What is genuinely irreversible: (a) the
  timestamp on the post-record (the "I posted at T" fact survives
  even if the content is deleted, in some indexer / archiver
  caches); (b) third-party scrapers who already pulled the post;
  (c) Bluesky's own internal logs. The "irreversible" framing
  conflates "you cannot un-post" (false) with "the post leaving a
  trace is permanent" (true).

- `This will post to Bluesky.` — too matter-of-fact. The
  destination-naming is right, but the operator gets no warning
  about the durability of the action.

- `This will send a post to your Bluesky account @{handle}.` —
  acceptable, but "send a post" understates the publish posture.
  The chosen wording uses "post" as a verb (matches Bluesky
  vernacular) and names what survives if deletion is attempted.

**Why the recommended wording works:**

1. **Technically accurate.** Bluesky deletion *is* best-effort —
   the post text leaves the timeline but archival traces persist.
   This is the right framing for an operator deciding to commit.

2. **Names what survives.** "Timestamp" and "platform-side cache"
   are the two durable artifacts. The operator can decide whether
   that durability is acceptable before clicking.

3. **No §1.5 hazard.** The wording is about post mechanics, not
   about the post's content claims.

4. **Names the destination by handle.** Matches §5.2's button
   label (`Publish to Bluesky`) and adds operator-actionable
   information (which handle is being used; the operator may have
   multiple Bluesky accounts in `.env` setups).

### 2.10. Question 10 — MONTHLY_ROUNDUP trigger summary

The Orchestrator flagged that T6b must use the §5.7 binding wording
verbatim (`monthly cross-domain categorical-structure roundup`),
NOT the §1.5-violating "state of cultural alignment roundup"
phrasing still in ARCHITECTURE.md §4.6 line 1211 (T7 deferred fix).

**Ruling — verified at code-review time; T6b inherits T5 § /
T6a `format_trigger_summary` verbatim.**

The T6b admin console renders trigger summaries via the same
`format_trigger_summary()` function used by T5's CLI (or via T6a's
`digest.format_trigger_summary()` — both already correct). The
Coder MUST NOT re-author the trigger-summary string at the Flask
template layer; the template renders the output of the binding
function.

**Static check the Reviewer applies:** grep the Flask templates in
`cdb_social/admin_console/templates/` for `state of cultural
alignment` (case-insensitive). Any match = FAIL. Also grep for
`pairwise gap` (the T5 §5.7-rejected wording) — any match = FAIL.

**No T6b-specific override.** If a template wants to display the
trigger summary in a card / panel, it calls
`format_trigger_summary(trigger)` and renders the result inside the
card. The card chrome (the surrounding labels) uses operational
language not methodology copy.

---

## 3. Vocabulary compliance on T6b-authored strings

Scanned every LSB-authored string surface implied by kickoff §11.6
and the §5 binding notes:

| String | §1.5.4 reading | Verdict |
|---|---|---|
| Button label `Draft via LLM` | Operational, names the call type | Compliant |
| Button label `Draft via LLM (Claude)` (alt) | Same plus model-family disclosure | Compliant |
| Button label `Approve` | Operational | Compliant |
| Button label `Reject` | Operational | Compliant |
| Button label `Publish to Bluesky` | Operational, names destination | Compliant |
| Button label `Publishing not enabled for {Platform}` (disabled state for X/LinkedIn) | Operational | Compliant |
| Sibling link `Download draft text` | Operational | Compliant |
| Confirm header `Draft via LLM?` | Operational | Compliant |
| Confirm header `Approve draft?` | Operational | Compliant |
| Confirm header `Reject draft?` | Operational | Compliant |
| Confirm header `Publish to Bluesky?` | Operational, names destination | Compliant |
| Confirm body for "Approve" mentioning "Publish to Bluesky" as a separate action | Reinforces §11.1 B-2 two-click contract | Compliant |
| Confirm body for "Publish" using §5.9 binding wording (`Once posted, deletion is best-effort...`) | Technically accurate; no overclaim | Compliant |
| Confirm button labels (`Yes, draft via LLM`, `Yes, approve`, `Yes, reject`, `Yes, publish to Bluesky`) | Operational; mirrors the header verb | Compliant |
| Cancel button `Cancel` (on every confirm page) | Operational | Compliant |
| Error header `Drafter call did not pass validator. No draft was created.` | Neutral; validator-as-subject (T5 §5.5 inherited) | Compliant |
| Error body "guardrail, not an operator error" sentence | Operator-role preservation; not shaming | Compliant |
| Error header `Drafter call failed (Anthropic API error).` | Operational; names category | Compliant |
| Error sub-text "This is a transport-layer failure, not a guardrail rejection." | Distinguishes failure classes | Compliant |
| Error header `Publish to Bluesky failed.` | Operational | Compliant |
| Error sub-text re. transient vs terminal failure category | Operational | Compliant |
| Field label `Drafter self-rating` (NOT `Confidence`) | T1 §5.4 + T5 §5.1 carry-forward | Compliant |
| Optional note `(fixed at 0.5 for v1; not calibrated — see T3 §5.6)` | Calibration disclaimer | Compliant |
| Framing-check key labels (verbatim T3 §5.11 keys) | Schema-aligned identifiers | Compliant |
| Inline tooltip / `title` text on framing-check keys (optional) | Methodology docstring excerpt | Compliant (if added) |
| Trigger-summary text (delegated to `format_trigger_summary`) | T5 §5.7 / T6a binding | Compliant by reuse |
| MONTHLY_ROUNDUP text — `Monthly cross-domain categorical-structure roundup` | T1 §5.7-compliant; T5 §5.11-defused | Compliant by reuse |
| DIVERGENCE text — `max pairwise distance` | T5 §5.7 binding | Compliant by reuse |
| DRIFT text — `Procrustes distance` + placeholder caveat | T5 §5.7 binding | Compliant by reuse |
| Filesystem-path display in `<code>` (e.g., `out/social/queue/pending/{draft_id}.json`) | Operational; no sanitization needed on loopback | Compliant |
| Loopback-bind startup log message `Listening on 127.0.0.1:8000 (loopback only; no internet exposure)` | Operational; security disclosure | Compliant |
| Index-page nav links to queue states (`pending`, `approved`, `published`, `failed`) | Schema-aligned identifiers | Compliant |
| Rejection-reason `<select>` option labels (the five T5 §5.3 codes) | T5 §5.3 binding | Compliant by reuse |

No new §1.5.4 violations introduced. The T1 §5.7 / T5 §5.11
ARCHITECTURE.md §4.6 line 1211 doc-fix remains carry-forward to T7.

The hazard at the "Generate draft" candidate label (rejected in
§2.1) was the single methodology-loaded display-copy decision that
required a substantive ruling beyond inheritance.

---

## 4. Cross-references to T3, T5, T6a

| T6b surface | Reads from | Defined at |
|---|---|---|
| Trigger-summary strings in Jinja templates | `format_trigger_summary(trigger)` (called from view handlers) | T5 §5.7 / T6a `digest.py` |
| `Drafter self-rating` field label | `SocialDraft.drafter_self_rating` | T1 §5.4 + T5 §5.1 |
| Framing-check display | `SocialDraft.framing_checks` (four canonical keys) | T1 §5.3 + T3 §5.11 + T5 §5.2 |
| Edit-flow validator-failure page | T5 `_display_edit_failure` wording (port to HTML) | T5 §5.5 |
| Rejection-reason `<select>` options | Five-code enum (`forbidden_vocab`, `register_boundary`, `bare_numeric`, `off_topic`, `other`) | T5 §5.3 |
| Drafter-rejection error page | `DrafterRejectedException` matched terms + T3 §5.11 keys | T3 §5.1 / §5.2 / §5.3 / §5.11 |
| Bluesky publisher error page | T6-publisher transient/terminal failure categories | Kickoff §3 T6 + §11.6 |
| Methodology URL display chrome (audit panel) | `SocialDraft.methodology_url` | T3 §5.5 |
| In-post URL labeling (verbatim drafter output) | Drafter prompt's "details"/"more" instruction | T3 §5.5 |

T6b does NOT touch `cdb_core/schemas.py`. No T1 schema-additions
required.

---

## 5. Binding carry-forward notes (apply at Coder dispatch)

These notes are binding on the Coder during T6b implementation.
The Reviewer enforces.

### 5.1. **"Request draft" button text: `Draft via LLM`.** [Audience translation, Claims validity]

The Flask template renders the button on each detected trigger row
with the label **`Draft via LLM`** (the alternate **`Draft via LLM
(Claude)`** is also approved if Mark prefers the model-family
disclosure).

**Forbidden labels** (Reviewer enforces):
- `Request draft` (too generic; hides the LLM call)
- `Draft a post` (does not disclose the LLM invocation)
- `Generate draft` (verb ambiguous; can read as "auto-generate")
- `Compose draft via LLM` (verb implies operator authorship)
- Any label not naming the LLM call

**Implementation:** the button is a POST form to
`/triggers/<dedupe_key>/draft?platform=<platform>`. The button
`type="submit"` and `value="Draft via LLM"` (or HTML `<button>`
with text content `Draft via LLM`). When the trigger applies to
multiple platforms (the index view shows Bluesky + X + LinkedIn
buttons), each platform's button reads `Draft via LLM` with the
platform name in the surrounding label or row context.

### 5.2. **"Publish" button text: `Publish to Bluesky`; disabled state for X/LinkedIn.** [Audience translation, Claims validity]

The Flask template on the approved-draft page renders the publish
button as **`Publish to Bluesky`** for Bluesky drafts. The button
posts to `/draft/<draft_id>/publish`.

For X / LinkedIn drafts (no live publish per kickoff §10):
- The button is **disabled** (`disabled` HTML attribute) with label
  **`Publishing not enabled for {Platform}`** (e.g.,
  `Publishing not enabled for X`).
- A sibling **`Download draft text`** link renders next to the
  disabled button; clicking exports the draft text as `.txt` (or
  copies to clipboard via JS — Coder's choice).

**Forbidden labels** (Reviewer enforces):
- `Publish` (too generic; no destination)
- `Post` (platform-vernacular ambiguity)
- `Send to Bluesky` (understates immediacy)
- Any label that hides the destination

### 5.3. **Confirmation pages: four destructive POST actions, each with binding header + body + confirm-button label.** [Audience translation, Claims validity]

Each of the four destructive POST routes (`draft`, `approve`,
`reject`, `publish`) renders an interstitial `confirm.html`
template with the wording in the table below. The interstitial is
GET-served (so a refresh / back is safe); the form on the
interstitial is the actual POST.

| Action | Header | Body | Confirm button | Cancel button |
|---|---|---|---|---|
| Draft | `Draft via LLM?` | `This will invoke the {drafter_version} drafter on trigger {dedupe_key} via Claude. A new draft will land in queue/pending/ on success. Drafter failures (forbidden vocabulary, missing CI, etc.) are surfaced; no draft is created on failure.` | `Yes, draft via LLM` | `Cancel` |
| Approve | `Approve draft?` | `Approve draft {draft_id}. The draft moves to queue/approved/. This does not publish. You will need to click "Publish to Bluesky" on the approved-draft page to send the post.` | `Yes, approve` | `Cancel` |
| Reject | `Reject draft?` | `Reject draft {draft_id}. The draft moves to queue/failed/ with the selected reason. This cannot be undone via the UI — to re-queue, copy the draft text from queue/failed/{draft_id}.json and re-submit via "Draft via LLM."` (rejection-reason `<select>` + optional `<textarea>` for free-text note follow) | `Yes, reject` | `Cancel` |
| Publish | `Publish to Bluesky?` | `This will post to Bluesky as @{handle}. Once posted, deletion is best-effort — the timestamp and any platform-side cache may persist. The post text below will be sent verbatim.` (followed by `<pre>` of the verbatim draft text + the methodology / dashboard URL audit panel) | `Yes, publish to Bluesky` | `Cancel` |

**FORBIDDEN at any confirm-page:** any `est. tokens: ~X` /
`expected cost` / `~$X` display. CLAUDE.md R14 — no software-side
spend gates, including informational spend displays.
<!-- noqa: spend-gate-check -->

**Forbidden phrasings at the Publish confirm page:**
- `Once posted, this action is irreversible.` — overstated.
- `This is permanent.` — overstated.
- `Cannot be undone.` — overstated.

The §5.9 binding wording (`Once posted, deletion is best-effort
— the timestamp and any platform-side cache may persist.`) is the
exact text.

### 5.4. **Error pages: four distinct failure surfaces with binding wording per category.** [Audience translation, Claims validity]

**DrafterRejectedException page** (template:
`drafter_rejected.html`):

```
Drafter call did not pass validator. No draft was created.

Failed checks:
  <list of failed framing_checks keys with matched evidence,
   following T5 §5.5 wording — validator-as-subject>

The drafter produced text containing the matched terms / patterns.
This is a guardrail, not an operator error. To draft this trigger,
re-click "Draft via LLM" — the LLM may produce a clean draft on
retry. If retries persistently fail, the v1 system prompt may need
a v2 bump (see CDA SME T3 §5.8).
```

The failed-checks list reuses T5's `_display_edit_failure` per-check
formatting transposed to HTML.

**Anthropic API failure page** (template: `anthropic_failed.html`):

```
Drafter call failed (Anthropic API error).

This is a transport-layer failure, not a guardrail rejection.
The underlying error: {error_type_short_tag}. The draft was not created.

You can:
  • Click "Draft via LLM" again to retry.
  • Check Anthropic status if retries keep failing.
```

The `{error_type_short_tag}` is one of: `RateLimit`, `Auth`,
`Network`, `ServerError`, `Other`. Full traceback to server log
only; not rendered in the page.

**Bluesky publisher failure page** (template:
`bluesky_failed.html`):

```
Publish to Bluesky failed.

The draft was NOT posted. The draft remains in queue/approved/ and
can be retried.

Failure category: {transient_or_terminal}.
Underlying error tag: {error_type_short_tag}.

Transient failures (network, rate limit) can be retried by
returning to the approved-draft page and clicking "Publish to
Bluesky" again. Terminal failures (auth, account suspension) need
operator intervention — check the server log for the full
traceback and resolve the underlying issue before retrying.
```

**Edit-flow validator failure** (template:
`edit_failed.html` or inline on the edit page):

Header: `Edit did not pass validator.` (verbatim T5 §5.5).
Body: per-check evidence lines following T5 §5.5 templates.
The HTML rendering uses `<dl>` or `<table>` for the
check / evidence pairs. The `Edit again? [y/n]` CLI prompt becomes
a pair of buttons: `Edit again` (re-open edit form with the failed
text as buffer) and `Discard edit` (returns to draft view; original
draft text unchanged in `pending/`).

**Forbidden wording across all four error pages** (Reviewer
enforces, mirrors T5 §5.5):
- `You wrote forbidden vocabulary` (operator-shaming)
- `Your draft / edit violates LSB methodology` (heavyweight)
- `Bad draft / edit` (judgmental)
- `Try again` (without context)

Subject is the validator / the transport / the platform — not the
operator.

### 5.5. **Framing-checks display: keys verbatim, optional inline tooltip.** [Claims validity, Audience translation]

The Flask template renders the four T3 §5.11 canonical keys
**verbatim** in the order matching T5 §5.2:

```
hypothesis_framing       PASS / FAIL
cognition_attribution    PASS / FAIL
bare_numeric_without_ci  PASS / FAIL
register_boundary        PASS / FAIL
```

Plus the `forbidden_terms_hit: []` line (or `[BUG] Forbidden terms
hit: [...]` per T5 §5.9 if non-empty).

Visual rendering of PASS / FAIL: the Coder picks (CSS class +
color, leading ✓ / ✗ glyph, or both). The keys are binding; the
visual treatment is Coder-choice within the
`feedback_ui_polish_scope` "minimum viable functional" budget.

**Optional inline tooltip / `title` attribute** on each key:
permitted, not required. If added, the tooltip text is the T3
§5.11 docstring excerpt for that check.

**Forbidden alternates** (Reviewer enforces):
- Friendly labels like `No cognition attribution` /
  `Register boundary respected` — these reframe the check's
  semantic and are forbidden.
- Composite PASS/FAIL collapsing the four keys — forbidden per
  T5 §5.2.

### 5.6. **Methodology URL display: verbatim in post body; raw URL in audit panel.** [Audience translation]

The admin console renders the methodology URL in two distinct
contexts:

1. **Inside the post-body preview** (verbatim drafter output, the
   text that will be published): render `SocialDraft.text` exactly
   as the drafter produced it. The drafter's prompt (T3 §5.5)
   teaches it to label the link "details" / "more"; the admin
   console does NOT re-label. Use `<pre>` or `<div
   class="post-body">` for verbatim rendering.

2. **In the metadata audit panel** (operator-internal audit view
   of the draft's fields): render `SocialDraft.methodology_url` and
   `SocialDraft.dashboard_url` as `<a href="..." class="audit-
   url">{url}</a>` — the link text IS the URL. This is the
   audit-affordance view, distinct from the post body.

The HTML structure must clearly separate the two contexts (e.g.,
post body in a `<pre>` with a `Post text` header, audit panel in a
`<dl>` with a `Metadata` header).

**Forbidden:** the admin console re-labeling the link in the post
body (e.g., changing `details` to `methodology` at the template
layer). Any divergence between admin-UI display and actual
published-post content = FAIL.

### 5.7. **`Drafter self-rating` label everywhere.** [Claims validity, Audience translation]

Every Flask template that surfaces
`SocialDraft.drafter_self_rating` uses the label `Drafter
self-rating` with the value rendered as `0.50` (two decimal
places, matching T5 §5.1). The optional inline note `(fixed at
0.5 for v1; not calibrated — see T3 §5.6)` may be added.

**Forbidden labels** (Reviewer enforces):
- `Confidence`
- `Confidence score`
- `Quality score`
- `Rating`
- `Score`

This applies to **every** template that shows the field: index
view (if shown), triggers view, draft view, edit view, confirm
pages.

### 5.8. **Filesystem paths display verbatim, no sanitization, monospace rendering.** [Audience translation]

Filesystem paths in the UI (e.g., `out/social/queue/pending/
{draft_id}.json`) render verbatim in `<code>` tags. The Coder may
shorten to relative-from-project-root if useful, but no
sanitization regex is applied (the publish-layer sanitization
regex is for public surfaces, not operator-internal admin tooling).

The Coder includes filesystem paths in operator-orientation views
(e.g., a `Path: <code>out/social/queue/pending/{draft_id}.json
</code>` line on the draft-detail page).

### 5.9. **Publish-irreversibility wording.** [Audience translation, Claims validity]

The Publish-confirm-page body contains the binding sentence:

```
This will post to Bluesky as @{handle}. Once posted, deletion is
best-effort — the timestamp and any platform-side cache may persist.
```

Where `{handle}` is the Bluesky handle from `.env`
(`BLUESKY_HANDLE`). The `@` is part of the binding wording.

**Forbidden wording at this surface** (Reviewer enforces):
- `Once posted, this action is irreversible.`
- `This is permanent.`
- `Cannot be undone.`
- `This will permanently send a post.`
- Any wording that absolutely overstates platform-mechanics
  irreversibility.

The binding wording is the only approved phrasing for this
surface. A future Phase 8+ refinement may revisit if Bluesky
mechanics change.

### 5.10. **MONTHLY_ROUNDUP wording verbatim by reuse; Reviewer grep-check.** [Vocabulary compliance, Register compliance]

The admin console's Flask templates call
`format_trigger_summary(trigger)` (from either
`scripts/social_review.py` or `cdb_social/digest.py` — both are
binding-compliant; the Coder picks the import source). The
template renders the result verbatim. No template-layer rewrite of
the trigger summary.

**Reviewer enforces** via grep on `cdb_social/admin_console/
templates/`:
- `state of cultural alignment` (case-insensitive) — any match =
  FAIL.
- `pairwise gap` (case-insensitive) — any match = FAIL.
- `cultural worldview` / `cultural belief` (case-insensitive) —
  any match = FAIL (per §1.5.4 spirit).

The T7 ARCHITECTURE.md §4.6 line 1211 prose fix remains
carry-forward; T6b does not propagate the pre-amendment phrasing
at the display layer.

---

## 6. Mark-escalation note

**No Mark escalation is required for T6b Coder dispatch.**

Three items Mark should be aware of:

1. **Button-text choice between `Draft via LLM` (compact) and
   `Draft via LLM (Claude)` (model-family-disclosed).** Both are
   CDA-SME-approved. Mark may choose at the Coder hand-off; the
   compact form is the default. The parenthetical disclosure is
   useful if Mark anticipates a contractor admin operating the
   console in the future (mentioned in the Orchestrator's
   invocation), but is non-binding.

2. **The Publish-confirm wording at §5.9** is methodologically
   accurate at the Bluesky-platform-mechanics layer. If Mark
   would prefer a softer wording (e.g., omitting the "best-effort"
   technical detail for a broader future-operator audience), that
   re-styling is a Phase 7.5+ refinement under a future CDA SME
   review. The current binding is the technically-precise version.

3. **The MONTHLY_ROUNDUP wording reuse (§5.10) defuses T1 §5.7
   / T5 §5.11 at one more surface.** The T7 ARCHITECTURE.md
   §4.6 line 1211 doc-fix is still pending; T6b does not
   discharge it. The T7 task (per kickoff §11.7) lands that fix.

---

## 7. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply at T6b (10 binding notes):**
  - §5.1 ("Request draft" button = `Draft via LLM`)
  - §5.2 ("Publish" button = `Publish to Bluesky`; X / LinkedIn
    disabled state with sibling download link)
  - §5.3 (four confirm-page header/body/button strings;
    NO token-count / cost display per R14)
  - §5.4 (four error pages with binding wording per category;
    validator-as-subject; "guardrail, not operator error" framing
    on drafter-rejection)
  - §5.5 (framing-check keys verbatim; no friendly labels; no
    composite PASS/FAIL collapsing)
  - §5.6 (methodology URL: verbatim in post body; raw in audit
    panel; no re-labeling)
  - §5.7 (`Drafter self-rating` everywhere; `Confidence` forbidden)
  - §5.8 (filesystem paths verbatim; no sanitization on loopback)
  - §5.9 (publish-irreversibility wording binding;
    `Once posted, deletion is best-effort — the timestamp and any
    platform-side cache may persist.`)
  - §5.10 (MONTHLY_ROUNDUP wording reuse; Reviewer grep-check
    for `state of cultural alignment` / `pairwise gap`)
- **`cdb_core/schemas.py` change required:** **No.** T6b reads from
  T1 schemas unchanged.
- **`docs/DATA_DICTIONARY.md` change required:** **No.**
- **Architect ratification required:** **No.**
- **T7 doc-sweep carry-forward:** the T1 §5.7 / T5 §5.11
  ARCHITECTURE.md §4.6 line 1211 prose revision remains binding
  on T7.
- **Mark escalation:** §6 advisory only; non-blocking for T6b
  Coder dispatch.

---

*End of Phase 7 T6b CDA SME verdict.*
