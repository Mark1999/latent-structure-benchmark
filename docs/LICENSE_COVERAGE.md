# LSB License Coverage

This document enumerates which license applies to each file path in the LSB
repository. It is the source of truth for license attribution and supersedes
any inline guesses.

The repository is multi-licensed by intent. Four licenses cover four distinct
categories of content; a fifth license covers third-party fonts vendored into
the dashboard. `ARCHITECTURE.md` §6.6 is the upstream specification of this
coverage.

**Document version:** v1.0 (Phase 8 T1, 2026-05-17)

---

## License files at repo root

| File | License | Covers |
|---|---|---|
| `LICENSE` | Apache License 2.0 | All Python source code, TypeScript/React source, CI/CD configuration, configuration files, and scripts |
| `LICENSE-DATA` | CC-BY-4.0 | All data outputs: raw informant responses, processed results, analysis results, grounding data, and project documentation |
| `LICENSE-PROMPTS` | CC0 1.0 Universal | CDA elicitation prompt templates (`packages/cdb_collect/prompts/`) and domain definition files (`data/domains/`) |
| `LICENSE-OPENBUNDLE` | CC0 1.0 Universal | The open data bundle (`data/open_bundle/`) and its Backblaze B2 / Zenodo distribution |
| `apps/dashboard/public/fonts/LICENSE.txt` | SIL OFL 1.1 | Vendored fonts: Lato (Lukasz Dziedzic) and JetBrains Mono (JetBrains s.r.o.) |

---

## Coverage by path (canonical mapping)

### Apache License 2.0 (code and configuration)

- `packages/cdb_core/**` — Python source (schemas, utilities)
- `packages/cdb_collect/**` — Python source; **except** `packages/cdb_collect/cdb_collect/prompts/v{N}/` and `packages/cdb_collect/cdb_collect/prompts/decline/v{N}/` (those are under CC0 per LICENSE-PROMPTS)
- `packages/cdb_analyze/**` — Python source
- `packages/cdb_publish/**` — Python source
- `packages/cdb_social/**` — Python source, including `cdb_social/drafters/prompts/v{N}/` (see Note 1 below)
- `apps/dashboard/src/**` — TypeScript/React source, tests, snapshots
- `apps/dashboard/index.html`
- `apps/dashboard/eslint.config.js`, `apps/dashboard/postcss.config.js`, `apps/dashboard/package.json`, `apps/dashboard/package-lock.json`
- `scripts/**` — Python scripts (see Note 2 below)
- `tests/**` — Python test code and fixtures
- `.github/workflows/**` — CI/CD pipeline definitions (ci.yml, social-pipeline.yml, dependabot.yml)
- `main.py`
- Top-level config files: `pyproject.toml`, `.gitleaks.toml`, `.pre-commit-config.yaml`, `.env.example`, `.python-version`
- `.claude/settings.json`

### CC-BY-4.0 (data outputs and documentation)

**Data outputs:**
- `data/raw/informants.jsonl` (when published; gitignored per SECURITY_AND_HARDENING.md §3.3 — license applies when distributed)
- `data/raw/failures.jsonl` (same)
- `data/raw/decline_interviews.jsonl` (same)
- `data/derived/**` — derived classification files
- `data/results/**` — processed analysis result JSON files
- `data/grounding/**` — grounding reference data, including `data/grounding/family/romney_1996/**` (which carries the additional Romney et al. 1996 attribution requirement; see Note 3 below)
- `data/models/registry.json`

**Documentation:**
- `README.md`
- `ARCHITECTURE.md`
- `CLAUDE.md`
- `DESIGN_SYSTEM.md`
- `HOSTING_AND_DEV_OPS.md`
- `SECURITY_AND_HARDENING.md`
- `SECURITY.md`
- `PHASE_0_TASKS.md`
- `docs/**` — all files under `docs/`, including `DATA_DICTIONARY.md`, `status/**`, `AGENT_PIPELINE.md`, `briefings/**`, etc.
- `scripts/phase4a1_note_j_crosstab.SUPERSEDED.md`

**Dashboard generated/published data (gitignored; license applies when distributed):**
- `apps/dashboard/public/data/manifest.json` — dashboard data manifest
- `apps/dashboard/public/data/{domain}/*.json` — per-domain analysis outputs
- `apps/dashboard/public/data/failures/{domain}.json` — sanitized failure summaries

### CC0 1.0 Universal (prompts / domain definitions)

- `packages/cdb_collect/cdb_collect/prompts/v1/**` — canonical v1 collection prompt templates
- `packages/cdb_collect/cdb_collect/prompts/v1_s1/**` through `v1_s8/**` — sensitivity-study prompt variants
- `packages/cdb_collect/cdb_collect/prompts/v2_soft1/**` — v2 soft-prompt variant
- `packages/cdb_collect/cdb_collect/prompts/decline/v1/**` — decline-interview prompt
- `data/domains/v1/**` — domain YAML definition files (family, holidays, food)

### CC0 1.0 Universal (open bundle)

- `data/open_bundle/` directory (when populated; the `.gitkeep` placeholder is Apache 2.0 as a build artifact)
- `data/open_bundle/lsb_open_bundle_v1.tar.gz` (when built at T6; not yet in repo)
- `data/open_bundle/README.md` (when written at T6; not yet in repo)
- The bundle's tarball internals: the tarball as a whole is CC0 per LICENSE-OPENBUNDLE; constituent data files inside the bundle are CC-BY-4.0 per their origin, but the bundle distribution as a complete collection is CC0 (see §6.6 rationale: "CC0 removes the attribution requirement entirely and makes downstream reuse maximally frictionless")

### SIL OFL 1.1 (third-party fonts)

- `apps/dashboard/public/fonts/lato/lato-regular.woff2`
- `apps/dashboard/public/fonts/lato/lato-bold.woff2`
- `apps/dashboard/public/fonts/jetbrains-mono/jetbrains-mono-regular.woff2`
- `apps/dashboard/public/fonts/jetbrains-mono/jetbrains-mono-bold.woff2`
- `apps/dashboard/public/fonts/LICENSE.txt` (the OFL text itself)

The OFL attribution requirement is satisfied by the bundled `LICENSE.txt`. The fonts may not be sold by themselves; they may be embedded, redistributed, and modified as part of a larger work.

---

## NOTICE file determination

Apache License 2.0 §4(d) requires that Derivative Works include a readable copy of any NOTICE file if the original work includes one. Two conditions trigger a NOTICE file at repo root:

1. The work itself includes a NOTICE file with attribution requirements.
2. The work vendors third-party Apache-licensed code that includes a NOTICE file.

**Verification performed (2026-05-17):**

- `grep -rn "Apache License" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.css" packages/ apps/` returns only two LSB-authored references (`apps/dashboard/src/copy/framing.ts` which exports `CODE_LICENSE = "Apache 2.0"` and its corresponding test). No third-party Apache-licensed source files are vendored in the tracked tree.
- `.venv/` (untracked, gitignored) contains Apache-licensed dependencies (e.g., `requests`). These are runtime dependencies installed from PyPI; they are not vendored source in the repo. They do not create a repo-level NOTICE obligation.
- The font files are under SIL OFL 1.1, which has its own attribution mechanism (the bundled `LICENSE.txt`). SIL OFL files do not require an Apache-level NOTICE file.

**Determination: No `NOTICE` file is required at repo root.** LSB does not vendor any Apache-licensed third-party source code with attribution requirements. The sole Apache 2.0 obligation is that downstream Derivative Works of LSB include a copy of `LICENSE`; no NOTICE text needs to be propagated.

---

## License file content assessment

### `LICENSE` (Apache 2.0)

The file contains:
- Lines 1–9: LSB project preamble (identifies scope and points to ARCHITECTURE.md §6.6)
- Lines 10–186: The canonical Apache License Version 2.0 §§1–9 body text, matching the text at https://www.apache.org/licenses/LICENSE-2.0.txt
- Lines 187–199: Project copyright notice (`Copyright 2026 Cognitive Structure Lab`) and the standard boilerplate notice

The "APPENDIX: How to apply the Apache License to your work" template section from the upstream apache.org source is intentionally omitted. This section is a template, not a license term; omitting it is standard practice when a project provides its own copyright statement. The §§1–9 legal terms are complete and intact.

**Assessment: Canonically correct. The complete license terms are present.**

### `LICENSE-DATA` (CC-BY-4.0)

The file contains an LSB scope description, the Romney et al. (1996) additional attribution requirement, and a plain-English summary of CC-BY-4.0 terms with a reference to the full legal text at `https://creativecommons.org/licenses/by/4.0/legalcode`. Creative Commons licenses are distributed by reference to the canonical legal code; summary + URL is the standard form. The full legal code is at the URL provided.

**Assessment: Canonically correct per CC distribution convention.**

### `LICENSE-PROMPTS` (CC0 1.0 Universal)

The file contains an LSB scope description and the CC0 1.0 plain-language deed, with a reference to the full legal code at `https://creativecommons.org/publicdomain/zero/1.0/legalcode`. The plain-language deed covers the waiver of all rights "to the extent allowed by law."

**Assessment: Canonically correct per CC0 distribution convention.**

### `LICENSE-OPENBUNDLE` (CC0 1.0 Universal)

The file contains an LSB scope description specific to the open bundle (referencing ARCHITECTURE.md §6.7) and the same CC0 1.0 plain-language deed as LICENSE-PROMPTS, with a reference to the full legal code URL.

**Assessment: Canonically correct per CC0 distribution convention.**

---

## Notes for Architect review

**Note 1 — `cdb_social/drafters/prompts/v{N}/` license.** Three prompt files exist at `packages/cdb_social/cdb_social/drafters/prompts/v1/` (bluesky.md, linkedin.md, x.md). Currently mapped under Apache 2.0 as project source code. These could be argued as "prompt templates" under LICENSE-PROMPTS (CC0), but differ from the CDA elicitation prompts in a material way: they are tightly coupled to the `cdb_social` drafter code, platform-specific, and not intended as reusable CDA elicitation protocols. **Default recommendation: Apache 2.0.** The CC0 dedication in LICENSE-PROMPTS was designed for the free-list / pile-sort / interview prompts that independent researchers would want to replicate without any obligation. Social drafter prompts are LSB operational tooling. Architect should confirm or override.

**Note 2 — `scripts/` license.** All scripts are mapped under Apache 2.0. Some (e.g., `scripts/social_review.py`, `scripts/lsb_inspect.py`) are operational convenience scripts that future contributors might want to fork freely. Apache 2.0 is permissive enough for all practical purposes; no action recommended.

**Note 3 — Romney et al. (1996) attribution requirement.** The `data/grounding/family/romney_1996/` directory retains historical reference data per the 2026-05-07 amendment (ARCHITECTURE.md §1.5.5). The CC-BY-4.0 license covers these files, but they carry an additional scholarly attribution requirement documented in `data/grounding/family/romney_1996/source.md`. Any redistribution must cite: Romney, A. K., Boyd, J. P., Moore, C. C., Batchelder, W. H., & Brazill, T. J. (1996). PNAS 93(10), 4699–4705 (PMC: PMC39344).

**Note 4 — `data/raw/*.jsonl` files are gitignored.** Per CLAUDE.md R8 and SECURITY_AND_HARDENING.md §3.3, raw JSONL files are not committed to the repo. They will appear in the open bundle distribution (CC-BY-4.0 for the working data; CC0 for the bundle as a whole). LICENSE_COVERAGE documents the license that applies when they are distributed.

**Note 5 — `apps/dashboard/public/data/` is gitignored.** This directory is populated by the publish pipeline at deploy time. It contains generated analysis JSON files (CC-BY-4.0) that are served by Cloudflare Pages. The directory is explicitly gitignored in the repo root `.gitignore`.

**Note 6 — ARCHITECTURE.md §6.6 maps `docs/` under CC-BY-4.0 ("Documentation and methodology text").** This is consistent with the mapping in this document. The Architect's intent is that methodology documentation, the data dictionary, and status/audit files all carry CC-BY-4.0 so that researchers can cite and excerpt from them with standard scholarly attribution.

---

*This document is itself covered by CC-BY-4.0 as project documentation per ARCHITECTURE.md §6.6 and the mapping above.*
