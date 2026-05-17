# Phase 8 GitHub Settings — Mark's Runbook for Go-Public

**Filed:** 2026-05-17
**Drafted by:** Coder agent
**Approved by:** CDA SME (T4 verdict: `docs/status/2026-05-17-phase8-T4-cda-sme-verdict.md`)
**Used at:** Mark-action M10 (repo description + topics), M11 (branch protection), M12 (the public flip).

This document is the operator runbook for flipping LSB public. Mark works
through it section by section at go-public time. Each section corresponds
to a GitHub-UI surface.

Repository: `https://github.com/Mark1999/latent-structure-benchmark`

---

## Section A — Pre-flip readiness gates

Verify all of these before proceeding to Section B.

- [ ] T1 license audit landed (Architect PASS)
- [ ] T2 SECURITY.md contact resolved (M1 Cloudflare Email Routing configured + Mark self-tested receipt)
- [ ] T3 README public-readiness pass landed (CDA SME PASS)
- [ ] T4 this checklist landed (CDA SME PASS — this document)
- [ ] T5 pre-release scan green within last 24 hours (no FORBIDDEN_VOCAB / SECRET / LEAKED_PATH hits)
- [ ] All open PRs merged or closed
- [ ] Working tree clean on `master`
- [ ] T9 Cloudflare Pages production live; `https://cogstructurelab.com/` returns 200 with CSP/HSTS headers

---

## Section B — Repository settings (pre-flip configuration, M10 + M11)

### Settings → General

**Description (paste VERBATIM into Settings → General → Description, ≤350 chars):**

> Latent Structure Benchmark — applies Cultural Domain Analysis elicitation protocols to large language models as if they were informants. Surfaces the corpus lens — how a model organizes everyday vocabulary, refracted through training and alignment. Open data, reproducible, model-to-model.

(340 chars. CDA SME-ratified; §1.5 framing-checked. Trim edits from Architect draft: "as if the models were informants" → "as if they were informants"; "refracted through its training" → "refracted through training".)

- [ ] Description pasted and saved

**Website URL (paste into Settings → General → Website):**

> https://cogstructurelab.com

(NOT the Bluesky URL — the Bluesky handle lives in the README footer per CDA SME T4 §Q7 recommendation.)

- [ ] Website URL set

**Social media handles:** Leave both Twitter and Mastodon fields BLANK. GitHub has no native Bluesky support; the Bluesky handle is in the README only.

**Topics (paste each into Settings → General → Topics, one at a time; GitHub limit: 20 topics):**

```
llm-benchmark
cultural-domain-analysis
cda
large-language-models
model-comparison
free-list
pile-sort
multidimensional-scaling
mds
cognitive-anthropology
open-data
reproducible-research
corpus-analysis
salience-analysis
consensus-analysis
bootstrap
informant-elicitation
cogstructurelab
```

(18 topics. Two slots reserved — Mark may add keywords at M10 if a discovery gap surfaces.)

- [ ] All 18 topics added

**Social preview image:** Skip for v1. Defer to the FT designer track (parallel to Phase 8). Adding a custom image later does not require re-flipping visibility — it is a single Settings change.

**Features:**

- [ ] **Issues:** ON (standard contribution and bug-report path)
- [ ] **Discussions:** OFF for v1 (maintenance burden at launch; revisit Phase 9+ when traffic patterns are visible)
- [ ] **Wiki:** OFF (LSB docs live in the repo; a second source of truth invites drift)
- [ ] **Projects:** OFF / keep private (planning artifacts live in `docs/status/`)
- [ ] **Sponsorships:** OFF for v1 (can enable later if useful)

### Settings → Branches → Branch protection rules (M11)

Add a rule for the `master` branch with these settings (case-sensitive check names — verify exact names in the Actions UI before saving):

| Setting | State |
|---|---|
| Branch name pattern | `master` |
| Require a pull request before merging | YES |
| Required approvals | 0 (Mark is the sole reviewer; >0 would block all fork PRs) |
| Dismiss stale pull request approvals when new commits are pushed | YES |
| Require status checks to pass before merging | YES |
| Required status checks | `pytest`, `ruff`, `mypy`, `cdb-social-boundary`, `no-spend-gate-check` |
| Require branches to be up to date before merging | YES |
| Require conversation resolution before merging | YES |
| Require signed commits | NO (Mark's local workflow does not currently sign; enabling breaks direct-push) |
| Require linear history | NO (preserves merge-commit option for fork PRs) |
| Restrict who can push to matching branches | YES — allow list: `Mark1999` |
| Do not allow bypassing the above settings | NO (Mark must bypass the PR requirement on direct pushes from his clone) |
| Allow force pushes | NO |
| Allow deletions | NO |

**Effect:** Mark continues `git push origin master` from his clone without ceremony (CLAUDE.md §8 direct-to-master workflow preserved). External fork PRs land via standard GitHub flow with CI gating on all five required checks.

- [ ] Branch protection rule saved

### Settings → Secrets and variables → Actions

Configure before the cron's next scheduled fire:

| Secret name | Value source | Purpose |
|---|---|---|
| `LSB_SMTP_USERNAME` | Mark's Gmail address | Daily detection cron sends digest email |
| `LSB_SMTP_PASSWORD` | Gmail app password (M3: generate at https://myaccount.google.com/apppasswords) | Same |
| `LSB_DIGEST_RECIPIENT` | Mark's monitoring email address | Same |

The cron at `.github/workflows/social-pipeline.yml` references these via `${{ secrets.LSB_SMTP_* }}` syntax. Without them, the email step silently no-ops.

- [ ] `LSB_SMTP_USERNAME` set
- [ ] `LSB_SMTP_PASSWORD` set
- [ ] `LSB_DIGEST_RECIPIENT` set

### Settings → Security

- [ ] Confirm `SECURITY.md` auto-detection shows up under the "Security" tab
- [ ] Confirm `LICENSE` auto-detection shows Apache 2.0 in the sidebar

**LICENSE auto-detection note:** GitHub auto-detects exactly one file named `LICENSE` and surfaces it in the sidebar (Apache 2.0). The three additional license files (`LICENSE-DATA`, `LICENSE-PROMPTS`, `LICENSE-OPENBUNDLE`) are NOT auto-detected. The README licensing section (T3 deliverable) is the canonical multi-license discovery surface; `docs/LICENSE_COVERAGE.md` (T1 deliverable) is the path→license mapping. This is correct and honest as long as the README is unambiguous about coverage.

---

## Section C — The flip (M12)

**This is the irreversible action. Complete Sections A and B first.**

### Pre-flip forbidden-vocabulary spot-check (do this first)

- [ ] In a clean shell from `/opt/lsb-agent`, run:
  ```
  rg -iw '(worldview|believes?|thinks?)' \
    --glob '!docs/status/**' \
    --glob '!CLAUDE.md' \
    --glob '!ARCHITECTURE.md' \
    --glob '!docs/FRONTEND_DESIGNER_BRIEF*.md' \
    README.md SECURITY.md NOTICE 2>/dev/null
  ```
  Expected: 0 hits. If any hit, STOP — fix, re-run T5 scan, then proceed.

- [ ] In the GitHub UI Settings → General view:
  - Visually re-read the "Description" field as it will be rendered. Confirm no §1.5.4 left-column phrase appears: no `worldview`, `believes`, `thinks of`, `cultural bias` (standalone).
  - Visually re-read each of the 18 Topics as rendered. Same check.

- [ ] T5 pre-release scan (`scripts/prerelease_scan.py`) exit code = 0 within the prior 24 hours, with check #2 (forbidden-vocabulary grep) clean.

### Visibility flip

1. Settings → General → scroll to "Danger Zone" → "Change repository visibility".
2. Select "Make public".
3. Type `latent-structure-benchmark` to confirm.
4. Click "I understand, change repository visibility".

- [ ] Visibility flipped to public

---

## Section D — Post-flip verification (within 30 minutes)

- [ ] `https://github.com/Mark1999/latent-structure-benchmark` returns 200 in a logged-out browser

- [ ] Description renders correctly on the public repo home — no trailing ellipsis (means it fit under 350), no broken Unicode

- [ ] All 18 topics render below the description; click-through to topic pages works; no forbidden vocab visible in the rendered description or in topic labels

- [ ] `LICENSE` auto-detected — Apache 2.0 badge visible in the sidebar

- [ ] `LICENSE-DATA`, `LICENSE-PROMPTS`, `LICENSE-OPENBUNDLE` are present at repo root but NOT auto-detected by GitHub; the README licensing section is the canonical multi-license discovery surface — verify the README licensing section renders post-flip

- [ ] `SECURITY.md` auto-detected — "Security" tab visible; click to confirm the contact email `security@cogstructurelab.com` renders correctly

- [ ] Send a test email to `security@cogstructurelab.com` from an external account. Confirm ProtonMail receipt within 60 seconds via Cloudflare Email Routing. (M1 was self-tested at T2, but this is the public-surface re-verification. A silently broken forwarding address is the §7 risk #3 from the kickoff — treat as blocking.)

- [ ] Branch protection rule active: attempt a `git push origin master` from Mark's local clone — should succeed (Mark is on the allow-list bypass). Optionally verify a test fork PR would hit the CI requirement.

- [ ] README renders correctly with all badges + cross-doc links resolving

- [ ] First `social-pipeline.yml` cron fires successfully (check Actions tab; use manual `workflow_dispatch` if cron interval too long to wait)

---

## Section E — Rollback posture

If anything in Section D fails, the visibility flip is technically reversible via Settings → Change visibility → Make private. However, archivers and cache layers may have already indexed the content. **Treat M12 as irreversible per §10 of the kickoff.** A failure in Section D triggers fix-forward, not rollback.

---

## Section F — Post-flip monitoring (1-day window)

- [ ] First scheduled cron at 14:00 UTC runs successfully (visible in the Actions tab)
- [ ] If the cron produced a non-empty digest, email arrived in Mark's inbox
- [ ] If a vulnerability report arrives at `security@cogstructurelab.com`, it forwards to ProtonMail
- [ ] No Issues opened with security-flavored content that should have gone through the SECURITY.md disclosure path — triage any such issue immediately

---

## Section G — Open items (not blocking go-public)

- Phase 8 T10 methodology page placeholder ships before go-public per §5 Decision 1.
- Phase 8 T8 Zenodo DOI is minted at or shortly after go-public; README's DOI placeholder is replaced in a same-day follow-up commit.
- FT designer dashboard polish is a parallel track; the FT designer continues working independently.
- Social preview image (custom 1280×640) is a deferred FT designer deliverable; GitHub default is adequate for v1.

---

*End of GitHub settings runbook. Mark works through Sections A–G in order at M10/M11/M12.*
