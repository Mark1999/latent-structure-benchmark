# LSB Security and Hardening

**Document name:** `SECURITY_AND_HARDENING.md`  
**Version:** v0.1 (first draft, aligned with `ARCHITECTURE.md` v0.7)  
**Status:** Binding for all security-sensitive work; the Reviewer agent enforces §9  
**Audience:** Coder agent, Reviewer agent, Mark, anyone touching `apps/dashboard/`, `packages/cdb_collect/`, CI/CD configuration, or any account-level credential  
**Companion docs:** `ARCHITECTURE.md` (especially §1 commitments 7 and 9, §6.3 secrets, §6.5 ethics), `HOSTING_AND_DEV_OPS.md` (where things run), `PHASE_0_TASKS.md` (P0-T9 security scaffolding)

**Section reference contract.** This document's section numbering is **stable** because `ARCHITECTURE.md` cross-references specific sub-sections by number (§3.1 CSP, §3.3 LLM sanitization, §3.4 gitleaks, §5 account hardening, §6.5 SECURITY.md, §9 Reviewer rules, §10 future hardening). Changing these section numbers breaks the architecture doc's references and is not allowed without a coordinated update to `ARCHITECTURE.md`.

**Changelog:**
- **v0.1.1** (2026-04-19) — Added infra-pivot status banner. `lsb-agent-01` is decommissioned; references to `/opt/lsb-agent/.env`, the `lsb` user, and Hetzner-specific hardening describe the prior state and will be rewritten when a new VPS is chosen. No substantive change to the Reviewer rules table (§9) or to the CSP/sanitization guarantees.
- **v0.1** — first draft. Documents the threat model, the dashboard's CSP and security headers, the LLM-output sanitization rules, the secret-scanning configuration, the dependency security posture, account hardening (YubiKey, ProtonMail, password manager), the vulnerability disclosure process, the data protection posture, the Reviewer rules table, and the deferred-to-later hardening items (paid pentest, bug bounty, Cloudflare paid tier). Aligned with `ARCHITECTURE.md` v0.7 — includes the three Slack webhook env vars and the cryptographic provenance requirements from §1 commitment 7.

> **Status banner (2026-04-19).** The Hetzner VPS `lsb-agent-01` is **decommissioned**. References to `/opt/lsb-agent/.env`, the `lsb` system user, `lsb:lsb` ownership, SSH hardening specific to Hetzner, and the Hetzner physical-compromise threat row describe the prior state. Until a new VPS is selected, LLM provider keys and Slack webhooks live only on Mark's local MS Surface Laptop Studio in `.env` (mode 600, git-ignored) and in 1Password. The dashboard-side guarantees (CSP, sanitization, Cloudflare Pages, YubiKey-secured accounts) are unaffected by the VPS pivot. See `docs/INCIDENTS/2026-04-19-test-data-loss.md` and `HOSTING_AND_DEV_OPS.md` top-of-doc banner.

---

## 1. Overview and threat model

LSB is a small research project with a public dashboard, an open data bundle, and a single VPS that runs the collection pipeline. It is **not** a high-value target in any conventional sense — there's no user data, no financial data, no health data, no credentials worth selling, no proprietary IP that would matter to a state actor. But it makes public claims about named commercial AI products, it accepts contributions from external researchers, and its credibility depends on the integrity of the data it publishes. Those three things shape what LSB defends against and what it doesn't.

### 1.1 What LSB defends against

| Threat | Why it matters | Mitigation |
|---|---|---|
| **API key compromise** | Stolen LLM provider keys can be used to run up bills against LSB's accounts before Mark notices | Single-location storage on `lsb-agent-01` (`/opt/lsb-agent/.env`, mode 600, owned `lsb:lsb`), per-provider account caps as the Tier 2 spend defense, gitleaks pre-commit + GitHub secret scanning |
| **Data tampering** | If someone alters `informants.jsonl` after the fact, LSB's findings become un-falsifiable and the project's credibility evaporates | Append-only JSONL, SHA256 manifest on every record, provider request ID as a second independent audit path, four-layer backup chain |
| **Supply-chain attack via dependencies** | A compromised package in the dependency tree could exfiltrate keys, corrupt data, or inject content into the dashboard | Dependabot, `gitleaks`, minimal dependency footprint, lockfiles, no `unsafe-eval` in CSP |
| **Researcher submission with PII** | A researcher contributing human grounding data could accidentally include subject names, emails, or other identifiers | CI runs `gitleaks` + a PII scan on every grounding submission PR; the CDA SME agent reviews; Mark merges only after both pass |
| **XSS in LLM-generated content** | The lede generator emits text into the dashboard; a malicious or accidental injection could compromise visitors | Strict sanitization wrapper for all model-generated text rendered in the dashboard, no `dangerouslySetInnerHTML` without it, strict CSP `script-src` |
| **Account takeover via phishing or credential reuse** | Compromise of the Cloudflare, GitHub, or B2 account would let an attacker push a malicious dashboard build, delete backups, or rotate the open data bundle | Two YubiKey 5C NFC keys on every critical account; dedicated ProtonMail address; password manager with unique credentials; recovery codes printed and stored in the fireproof safe |
| **DDoS / abusive traffic on the dashboard** | A motivated attacker could make the dashboard expensive or unreachable | Cloudflare's free-tier DDoS protection is enabled by default; the static-files architecture has no backend to overwhelm; the spend-cap defense covers any operational consequence |
| **Reputational attack via fake findings** | A bad actor could fabricate LSB-branded findings (fake screenshots, fake citations) | Out of LSB's technical control; mitigated by the SHA256 provenance on every published record, the open data bundle being trivially reproducible from raw, and clear public attribution at every display surface |

### 1.2 What LSB does not defend against

These are explicit non-goals for v1. Each is defensible for a research project at this scale; each becomes a real question if LSB grows into a higher-stakes deployment.

- **Nation-state adversaries.** LSB is not a hardened target. A motivated state actor with persistent access could cause real damage. Mitigation is to be small, transparent, and not interesting enough to attract that level of attention.
- **Insider threats.** LSB has exactly one insider (Mark). If Mark is compromised, the project is compromised. There is no separation-of-duties for v1.
- **Advanced supply-chain attacks** (typosquatting + delayed payload + selective targeting). LSB uses standard, well-known dependencies, but does not run independent dependency auditing beyond what Dependabot and `gitleaks` provide.
- **Side-channel attacks** on the VPS or on Mark's local machines. Out of scope.
- **Subpoena or legal compulsion.** LSB stores no user data, has no logs of dashboard visitors, and produces no records about individuals. There's nothing to compel.
- **Physical compromise** of `lsb-agent-01`. Hetzner physical security is what it is; LSB does not run in a SCIF.

---

## 2. Scope of this document

**In scope:**

- Web application security for the dashboard at `cogstructurelab.com`
- Secret management for API keys, webhook URLs, and Backblaze keys
- Account hardening for all critical accounts (GitHub, Cloudflare, B2, HuggingFace, Zenodo, the LLM providers, ProtonMail)
- Dependency security via Dependabot and lockfiles
- Provenance and integrity of collected data (the SHA256 manifest, the provider request ID, the append-only invariant)
- Researcher submission PII handling
- Vulnerability disclosure process
- The Reviewer agent's enforcement responsibilities
- Future hardening items deliberately deferred from v1

**Out of scope:**

- Operational deployment details (those live in `HOSTING_AND_DEV_OPS.md`)
- Architectural decisions about what data exists in the first place (those live in `ARCHITECTURE.md`)
- Personal security hygiene unrelated to LSB (Mark's general password practices, his email security on personal accounts, his physical safety)
- Legal compliance reviews — LSB does not collect personal data, does not target EU users specifically, does not handle health or financial data, and has no GDPR/CCPA/HIPAA obligations to manage. If that changes, this document and the project's posture both change.

---

## 3. Web and code security

### 3.1 Content Security Policy

The LSB dashboard ships with a strict CSP enforced via `apps/dashboard/public/_headers` (Cloudflare Pages reads this file at deploy time per `HOSTING_AND_DEV_OPS.md` §2.3). The Reviewer agent rejects any PR that weakens the CSP without a documented architectural decision.

**Full CSP header:**

```
Content-Security-Policy: default-src 'self';
                          connect-src 'self';
                          img-src 'self' data:;
                          style-src 'self' 'unsafe-inline';
                          script-src 'self';
                          font-src 'self';
                          frame-ancestors 'none';
                          base-uri 'self';
                          form-action 'self';
                          object-src 'none';
                          upgrade-insecure-requests;
```

**Per-directive rationale:**

| Directive | Value | Why |
|---|---|---|
| `default-src` | `'self'` | Default-deny everything not explicitly allowed |
| `connect-src` | `'self'` | The dashboard fetches its data exclusively from same-origin static JSON files (`/data/...`). No third-party API calls, no telemetry, no fonts loaded from CDNs. This is the architectural commitment from `ARCHITECTURE.md` §4.5 ("static JSON only"). |
| `img-src` | `'self' data:` | Same-origin images plus data URLs (used for inline SVG-to-data-URL exports, the watermark function). No external images. |
| `style-src` | `'self' 'unsafe-inline'` | Tailwind CSS injects inline styles that the build can't fully eliminate. `'unsafe-inline'` for `style-src` only is accepted for v1 per resolved decision #22 in `ARCHITECTURE.md` §7. The Reviewer agent tracks this; if the build moves to fully external stylesheets, drop `'unsafe-inline'`. |
| `script-src` | `'self'` | Same-origin scripts only. **No `'unsafe-inline'` and no `'unsafe-eval'`** — these are non-negotiable. Any PR that adds either is rejected. |
| `font-src` | `'self'` | Same-origin fonts. The fonts named in `DESIGN_SYSTEM.md` §1 (Lato, JetBrains Mono) are bundled with the dashboard, not loaded from Google Fonts or any other CDN. |
| `frame-ancestors` | `'none'` | The dashboard cannot be embedded in iframes by other sites. Prevents UI redress / clickjacking. |
| `base-uri` | `'self'` | Prevents `<base>` tag injection. |
| `form-action` | `'self'` | The dashboard has no forms in v1; this is defense in depth in case a form is added later without explicit submission destination. |
| `object-src` | `'none'` | No Flash, no Java applets, no `<object>` of any kind. |
| `upgrade-insecure-requests` | (flag) | Any HTTP URL is rewritten to HTTPS at the browser. |

**No `report-uri` in v1.** A CSP report endpoint would require a server, and LSB has no server. If the dashboard graduates to a setup with a backend (per `ARCHITECTURE.md` §4.4.5 deferral), a `report-to` directive can be added then.

### 3.2 Other security headers

In addition to CSP, the `_headers` file sets:

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
```

| Header | Why |
|---|---|
| `X-Frame-Options: DENY` | Backstop for `frame-ancestors 'none'` for older browsers |
| `X-Content-Type-Options: nosniff` | Prevents MIME-type sniffing, which can turn a misclassified file into an XSS vector |
| `Referrer-Policy: strict-origin-when-cross-origin` | Limits referer leakage when users click outbound links |
| `Strict-Transport-Security` | Force-HTTPS for one year, including subdomains, with HSTS preload eligibility |
| `Permissions-Policy` | Disables every permission-gated browser feature LSB does not use, including the Topics API (`interest-cohort`) for advertising-cohort participation (LSB is not an ad network) |

### 3.3 LLM-output sanitization

The dashboard renders a small amount of LLM-generated content — specifically the lede sentence (`ARCHITECTURE.md` §4.2.3) for each `DomainResult`. This is the only model-generated text the dashboard ever displays. **Every byte of LLM-generated content rendered in the dashboard must pass through the sanitization wrapper specified below.** The Reviewer agent rejects any component that renders model-generated text via `dangerouslySetInnerHTML` or via any equivalent React mechanism without this wrapper.

**The sanitization wrapper.** A single React component, `SanitizedLLMText`, lives at `apps/dashboard/src/lib/sanitizeLLMText.tsx`. It accepts a string and renders it as plain text via React's normal text node rendering (which auto-escapes everything). It does **not** pass the text through any HTML parser. It does **not** support markdown rendering. It does **not** support hyperlinks embedded in the text. If a future feature needs richer LLM-text rendering, that feature ships with a hardened markdown parser (e.g., `marked` with `sanitize: true`, or `react-markdown` with `disallowedElements`) and a separate Reviewer rule.

```tsx
// apps/dashboard/src/lib/sanitizeLLMText.tsx
import React from 'react';

interface SanitizedLLMTextProps {
  text: string;
  className?: string;
}

/**
 * Renders LLM-generated text as plain text only.
 *
 * No HTML, no markdown, no hyperlinks, no dangerouslySetInnerHTML.
 * React's text node auto-escaping is the only sanitization needed
 * because we never interpret the string as anything but plain text.
 *
 * Per SECURITY_AND_HARDENING.md §3.3, every piece of LLM-generated
 * content rendered in the dashboard must use this component or an
 * equivalently safe rendering path. Reviewer enforces.
 */
export function SanitizedLLMText({ text, className }: SanitizedLLMTextProps) {
  return <span className={className}>{text}</span>;
}
```

This is intentionally minimal. The whole point of LSB's sanitization story is that the dashboard never interprets LLM output as anything but plain text. There's no risk of XSS via `dangerouslySetInnerHTML` if you never use `dangerouslySetInnerHTML`.

**Length cap.** The sanitization wrapper does not enforce a length cap, but the lede generator system prompt (`ARCHITECTURE.md` §4.2.3) instructs the model to produce a single declarative sentence. The Reviewer agent spot-checks lede outputs per release and the §1.5.4 language guardrails apply.

**The §1.5.4 language guardrails are a separate concern from XSS.** They prevent the model from saying "Claude believes X" — that's a *content* policy enforced by the prompt and by Reviewer spot-checks. XSS prevention is a *rendering* policy enforced by the sanitization wrapper. Both apply to every piece of LLM-generated text.

### 3.4 Secret scanning (`gitleaks`)

LSB runs `gitleaks` as a pre-commit hook (configured in P0-T9 per `PHASE_0_TASKS.md`) and again as a GitHub Actions check on every push and PR. GitHub's own secret scanning is the third layer.

**Configuration (`.gitleaks.toml`):**

The default `gitleaks` ruleset catches the obvious patterns: AWS access keys, generic API keys, JWT tokens, SSH private keys, Google API keys, Slack webhook URLs, and so on. LSB adds project-specific rules:

- **Anthropic API key pattern:** matches `sk-ant-[a-zA-Z0-9_-]{50,}` to catch keys that the default ruleset might miss
- **OpenRouter API key pattern:** matches `sk-or-v1-[a-zA-Z0-9]{60,}`
- **Hugging Face token pattern:** matches `hf_[a-zA-Z0-9]{30,}`
- **Backblaze application key pattern:** matches the B2 key ID format
- **LSB Slack webhook pattern:** matches `https://hooks.slack.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+` (the Slack webhook URL format)

**Allow rules:**

- `.env.example` is allowed to contain placeholder strings that look like keys (the placeholder pattern is `<your-key-here>` or `sk-ant-PLACEHOLDER`, never a real-looking key shape)
- `tests/fixtures/` is allowed to contain plausible-but-fake values inside `RawResponse` fixtures, as long as no value matches a real key pattern
- The architecture and design system documents are allowed to mention Slack webhook URL *patterns* (e.g., `https://hooks.slack.com/services/...` with literal ellipsis) but never a real-looking webhook ID

**Pre-commit installation:**

```bash
cd /home/markd/Documents/Projects/lsb
pre-commit install
# from now on, every commit runs gitleaks before the commit lands
```

**CI integration.** `.github/workflows/ci.yml` runs `gitleaks detect --source . --no-banner --redact` after the test suite. CI failure blocks merge.

**GitHub secret scanning.** Enabled in the repository settings. If gitleaks misses something and a key reaches `main`, GitHub secret scanning catches it within minutes and notifies Mark via email and the repository security tab. Mark rotates the key immediately per the procedure in §6.3.

### 3.5 The `cdb_analyze` no-LLM-imports static check

Not strictly a "security" check in the conventional sense, but a binding architectural constraint that the Reviewer agent enforces (`ARCHITECTURE.md` §1 commitment 6, §4.2 binding constraint, §5.1 Reviewer rule 2). Implemented as `scripts/check_no_llm_imports.py` per `PHASE_0_TASKS.md` P0-T6.

The check rejects any `import` or `from` statement in `packages/cdb_analyze/` that references: `anthropic`, `openai`, `google.generativeai`, `huggingface_hub.InferenceClient`, `litellm`, `langchain`, `llama_index`, or any other LLM client library. Listed here in §3.5 because the check is enforced by the same CI pipeline that enforces the other security rules and shares the same "Reviewer rejects on failure" pattern.

---

## 4. Dependency security

### 4.1 Dependabot

Configuration lives at `.github/dependabot.yml` (created in P0-T9). Two ecosystems:

```yaml
version: 2
updates:
  - package-ecosystem: "pip"  # uv reads pip-compatible metadata
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "dependencies"
      - "python"
    open-pull-requests-limit: 5
    rebase-strategy: "auto"

  - package-ecosystem: "npm"
    directory: "/apps/dashboard"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "dependencies"
      - "npm"
    open-pull-requests-limit: 5
    rebase-strategy: "auto"
```

Dependabot opens PRs for security updates immediately and for non-security updates weekly. Each PR runs through the standard `ci.yml` pipeline; the Reviewer agent reviews and Mark merges.

### 4.2 Lockfiles

- `uv.lock` for Python — committed
- `apps/dashboard/package-lock.json` for npm — committed

Both lockfiles are mandatory. The Reviewer agent rejects any PR that touches `pyproject.toml` or `package.json` without a corresponding lockfile update.

### 4.3 Minimal dependency footprint

LSB deliberately keeps its dependency footprint small to reduce attack surface. The Coder agent should not add a dependency just for convenience; every new dependency is a small architectural decision.

**Approved Python dependencies for v1** (the list is exhaustive — adding anything else requires Architect sign-off):

- `pydantic` (schemas)
- `httpx` (HTTP client for the LLM adapters; replaces both `requests` and provider-specific SDKs where reasonable)
- `anthropic` (the official Anthropic SDK, for the Anthropic adapter only — the Reviewer's `cdb_analyze` no-LLM-imports check is what keeps this from leaking into the analysis layer)
- `numpy`, `scipy`, `scikit-learn`, `pandas` (analysis pipeline)
- `networkx` (graph operations for the analysis layer)
- `matplotlib` (only as a sanity-check tool; the dashboard does its own rendering with D3 and Plotly, so matplotlib is not user-facing)
- `pyvis` (only if needed for offline visualization debugging)
- `click` (CLI for `scripts/`)
- `python-dotenv` (loading `.env`)
- `b2sdk` (Backblaze B2 client)
- `pytest` (testing)
- `ruff`, `mypy`, `pre-commit` (dev tooling)

**Approved npm dependencies for `apps/dashboard/` v1:**

- `react`, `react-dom`
- `typescript`
- `vite`
- `tailwindcss`, `postcss`, `autoprefixer`
- `d3` (visualization)
- `plotly.js-dist-min` (visualization)
- `vitest`, `@testing-library/react` (testing)

Anything outside these lists requires Architect sign-off.

### 4.4 Supply-chain hygiene posture

LSB does not currently run independent supply-chain attack detection beyond Dependabot and `gitleaks`. Per §1.2, advanced supply-chain attacks are out of scope for v1. If LSB grows to a scale where this matters, the additions would be:

- A signing/verification system for releases (e.g., `sigstore`)
- A SBOM generation pipeline (e.g., `syft`)
- Restricting package installation to a curated mirror

These are deferred to the §10 future hardening section.

---

## 5. Account hardening

LSB has a small number of critical accounts. Each one is hardened identically per the procedure below. The procedure is binding — every account in the table must complete every step before that account holds live LSB data.

### 5.1 Account inventory

| Account | Provider | Purpose | Holds live data? |
|---|---|---|---|
| GitHub (`AILLM1999` or LSB org) | GitHub | Source code, CI/CD, issue tracking, researcher submission PRs | Yes (after first commit) |
| Cloudflare | Cloudflare | DNS, registrar, dashboard hosting (Pages), TLS certificates | Yes (after first deploy) |
| Anthropic | Anthropic | Claude API access | Yes (when collection starts) |
| OpenRouter | OpenRouter | Multi-provider routing for OpenAI, Google, DeepSeek, Mistral, etc. | Yes (when collection starts) |
| Hugging Face (`AILLM1999`) | Hugging Face | Inference Providers + Datasets mirror | Yes (when collection starts and when first dataset is published) |
| Backblaze B2 | Backblaze | Backup storage, open data distribution | Yes (after first nightly backup) |
| Zenodo | Zenodo | DOI minting for the open data bundle | Yes (after Phase 4 validation) |
| ProtonMail | Proton | Dedicated `security@cogstructurelab.ai` security contact (and standalone account before the domain is live) | Yes from day 1 |
| Hetzner Cloud | Hetzner | `lsb-agent-01` VPS | Yes (after first provisioning) |
| 1Password (or chosen password manager) | — | Credential storage | Yes from day 1 |

### 5.2 The hardening procedure (run for every account in §5.1)

For each account:

1. **Create the account** with a strong, unique password generated by the password manager. Never reuse a password from another service.
2. **Enroll two YubiKey 5C NFC keys** as the WebAuthn / FIDO2 second factors. Both keys are enrolled before the account holds any live data. One key on Mark's keychain (daily-carry); one key in the fireproof safe with the backup drives (cold-storage).
3. **Disable any weaker second factors** (SMS, TOTP, email codes) wherever the provider allows. WebAuthn / FIDO2 only.
4. **Generate and store recovery codes.** Print them to paper and put the printout in the fireproof safe. Also store them in the password manager vault. Recovery codes are the failsafe if both YubiKeys are lost.
5. **Set the account's recovery email to the dedicated ProtonMail address** (`security@cogstructurelab.ai` post-domain; the standalone ProtonMail account before the domain is live). Never the personal email.
6. **Enable login notifications** wherever the provider supports them. New-device login notifications go to the dedicated ProtonMail address.
7. **Document the account in the password manager** with the username, the recovery email, the recovery code location ("fireproof safe + 1Password vault"), and the hardening completion date.

After this procedure, no account in the §5.1 table is logged into without a YubiKey present. There is no SMS-second-factor option enabled anywhere.

### 5.3 Why YubiKey, why two

- **YubiKey blocks credential phishing.** A WebAuthn assertion is bound to the legitimate origin; phishing sites can't replay it. SMS, TOTP, and email codes are all replayable.
- **Two keys** because losing one without a backup means losing the account. Cold-storage in the fireproof safe is the backstop. Three or more keys is overkill at LSB's scale.
- **5C NFC** specifically because it covers desktop USB-C, mobile NFC, and recent iPhones via NFC — the broadest device support without needing a separate model.
- **Hardware tokens, not authenticator apps.** Authenticator apps on a phone are vulnerable to phone compromise, OS-level malware, and SIM-swap-adjacent attacks. Hardware tokens are not.

### 5.4 ProtonMail security contact

The dedicated ProtonMail address is `security@cogstructurelab.ai` once the domain is live. Before the domain is live, a standalone ProtonMail account is used. The address is **not connected to Mark's personal email** in any way — separate password, separate recovery, separate device sessions.

This address is used for:

- All security-related disclosures (vulnerability reports, secret scanning alerts, dependabot security advisories)
- All provider account registrations (so a compromise of Mark's personal email doesn't cascade into LSB's operational accounts)
- The `SECURITY.md` contact field at the repo root
- Account recovery emails for every entry in the §5.1 table

The address is not used for:

- General project correspondence (use a separate `hello@` or `contact@` address for that, or a Discussion on the GitHub repo)
- Newsletters or marketing
- Anything that would dilute the signal-to-noise ratio of a security-only inbox

### 5.5 Password manager

- **Choice:** 1Password, Bitwarden, or KeePassXC. Mark picks based on personal workflow; the project does not mandate one.
- **Vault:** dedicated LSB vault, separate from Mark's personal vault, so that LSB credentials can be revoked or shared independently of personal ones.
- **Master password:** strong, memorized, never written down except in the fireproof safe printout (which is kept *only* as a last-resort recovery for catastrophic memory loss).
- **Vault export:** monthly export to an encrypted file stored on the USB SSD in the fireproof safe. This is the last-resort credential restore path if the password manager's cloud sync is lost.
- **Recovery codes for every account:** stored in the vault as attachments to each account entry, AND printed to paper in the fireproof safe.

### 5.6 The fireproof safe

Physical security of last resort. Holds:

- One of the two YubiKey 5C NFC keys
- The USB SSD with the encrypted backup snapshots and the password manager export
- A printed sheet with all recovery codes for all critical accounts
- A printed sheet with the password manager master password (sealed envelope, only for catastrophic memory loss)

The safe is rated for the storage type (paper + electronics). Physical access is Mark only. Combined with the second YubiKey on Mark's keychain and the password manager, this gives the project a credible disaster-recovery posture without becoming operationally heavy.

---

## 6. Vulnerability disclosure

### 6.1 Where reports go

Security disclosures go to **`security@cogstructurelab.ai`** (the dedicated ProtonMail address from §5.4). Before the domain is live, the address is published as the standalone ProtonMail account.

### 6.2 What LSB commits to

LSB is a small project with one maintainer. The disclosure SLA reflects that.

| Severity | Acknowledgment | Mitigation target |
|---|---|---|
| Critical (active exploitation, data tampering, key compromise) | Within 24 hours | As fast as possible; Mark drops other work |
| High (exploitable vulnerability, no active exploitation yet) | Within 72 hours | Within 7 days |
| Medium (vulnerability requires unusual conditions) | Within 7 days | Within 30 days |
| Low (theoretical or low-impact) | Within 14 days | Best-effort, included in the next release cycle |

LSB does not pay bounties in v1 (per resolved decision #20 in `ARCHITECTURE.md` §7). LSB does credit reporters by name in release notes if they want credit, or keep them anonymous if they prefer.

### 6.3 What happens after a credible report

1. Mark acknowledges receipt within the SLA window above.
2. Mark and the reporter agree on a coordinated disclosure timeline, typically 90 days for non-active issues and "as fast as possible" for active issues.
3. Mark investigates, develops a fix, and tests it. If the issue requires changes to data already on the dashboard or in the open data bundle, Mark pulls the affected data immediately and re-publishes after the fix.
4. Mark publishes the fix and a security advisory in the GitHub repo's Security tab. The advisory describes the issue, the fix, the affected versions, and credit to the reporter.
5. Any credentials potentially exposed by the issue are rotated per the rotation procedure below.

### 6.4 Credential rotation procedure

When a credential may have been exposed:

1. **Immediately revoke the existing credential** at the provider's dashboard. Do not wait for the new one to be ready.
2. **Generate a new credential** with the minimum necessary scope.
3. **Update the new credential everywhere it's used** — `lsb-agent-01:.env`, GitHub Actions secrets, the password manager. Use the password manager's "find usages" feature to make sure no location is missed.
4. **Restart any running processes** that loaded the old credential into memory.
5. **Audit recent activity** at the provider's dashboard for any usage of the old credential between the time of suspected compromise and the revocation.
6. **Document the rotation** in the password manager with the date, the reason, and the audit findings.
7. If the rotation was triggered by a confirmed compromise (not just a suspicion), file a security advisory per §6.3.

### 6.5 `SECURITY.md` at the repo root

The `SECURITY.md` file at the repo root has a fixed minimal format:

```markdown
# Security Policy

## Supported versions

Only the `main` branch is supported pre-launch. After the v1 dashboard launches, the most recent release tag is supported.

## Reporting a vulnerability

Please report security vulnerabilities by email to:

**security@cogstructurelab.ai**

Do not open public GitHub issues for security vulnerabilities.

We will acknowledge your report within 72 hours (sooner for critical issues).
We will work with you on a coordinated disclosure timeline, typically 90 days
for non-active issues.

LSB does not currently offer bug bounties. We do credit reporters by name in
release notes if you want credit, or keep your report anonymous if you prefer.

For full details see SECURITY_AND_HARDENING.md §6 in this repository.
```

The Reviewer agent rejects any PR that materially weakens this file (e.g., points the contact at a non-ProtonMail address, removes the "Do not open public issues" line, or removes the SLA commitment).

---

## 7. Data integrity and provenance

This section is the security expression of `ARCHITECTURE.md` §1 commitment 7 ("cryptographic provenance for every collection run") and §1 commitment 9 ("open data for researchers"). Both commitments depend on the data being verifiably untampered.

### 7.1 The append-only invariant

`data/raw/informants.jsonl` is **append-only by convention and by tooling**. New runs append; existing records are never edited or deleted. This is a binding architectural commitment per `ARCHITECTURE.md` §4.3.

**Enforcement mechanisms:**

1. **The collection runner** (`cdb_collect/runner.py`) opens the file in append mode (`"a"`) and never seeks. There is no code path in `cdb_collect` that opens the file for writing in any other mode.
2. **A pre-commit hook in CI** (added in P0-T6) checks any PR that modifies `data/raw/informants.jsonl` and rejects modifications that touch existing lines — only additions at the end are allowed. This catches the case where a Coder accidentally edits the file by hand.
3. **The nightly backup to Backblaze B2** uses content-addressable upload. If a previously-backed-up line is later modified, the backup catches the divergence on the next run.
4. **The four-layer backup strategy** (`HOSTING_AND_DEV_OPS.md` §4) means a tampered version of the file can be compared against earlier backed-up versions and the tampering identified.

### 7.2 The SHA256 manifest

Every `InformantRecord` carries a `sha256_manifest` dict per `ARCHITECTURE.md` §3.2 and `docs/DATA_DICTIONARY.md` §1.5. The manifest hashes eight required pieces of the record:

- The verbatim prompt and verbatim response for each of the three CDA steps (six entries)
- The request parameters (one entry, JSON-canonicalized)
- The full serialized `InformantRecord` minus the manifest field itself (one entry)

The manifest is computed at write time by `cdb_collect/runner.py` and stored alongside the raw record. Any later challenge to the record's authenticity is answered by recomputing the SHA256 and comparing.

**Manifest verification tool.** `scripts/verify_manifest.py` (Phase 1 deliverable) reads an `InformantRecord` from a file or from stdin, recomputes all eight manifest entries, and reports any mismatches. Researchers using the open data bundle can run this against any record they want to verify.

### 7.3 The provider request ID as a second audit path

Every `InformantRecord` also stores `provider_request_id` — the request ID returned by the LLM provider in the response (Anthropic's `x-request-id`, OpenAI's `id`, etc.). This is the **independent audit path through the provider's logs**. A researcher who suspects tampering can:

1. Locally recompute the SHA256 manifest and verify the verbatim fields (the local audit path)
2. Send the `provider_request_id` to the provider's support team and ask them to confirm the request and response from their logs (the independent audit path)

The two paths together give two independent ways to verify a record's authenticity. Tampering would have to compromise both — local files and provider logs simultaneously — to go undetected.

### 7.4 Researcher submission PII handling

When a researcher submits human grounding data via the GitHub PR workflow (`ARCHITECTURE.md` §4.2.5, `docs/grounding_submission_template.md`), the CI pipeline runs three checks:

1. **`gitleaks` scan** — catches accidentally-committed API keys, OAuth tokens, or other credential-shaped strings
2. **PII scan** — a custom check that looks for patterns suggesting subject-identifying content: email addresses (other than the submitter's contact), phone numbers, full names in unexpected fields, free-text demographic identifiers in the per-subject CSV. Implemented as `scripts/check_grounding_pii.py` (Phase 6 deliverable, listed in `PHASE_0_TASKS.md` only as a placeholder until then)
3. **Schema validation** — confirms `grounding_ref.json` validates against the `GroundingRef` schema, which has no field for a subject-identifying string and so structurally constrains submissions

**The CDA SME agent reviews** the submission for methodological soundness (`ARCHITECTURE.md` §5.1). The combination of automated PII scanning and human-in-the-loop review is the project's protection against accidentally publishing subject identifiers.

**If PII is discovered post-merge** (e.g., a researcher inadvertently included a subject's name in a `source.md` paragraph that the PII scan missed), the procedure is: pull the file from `main` immediately, post a security advisory, file a Zenodo retraction request for any release that included the file, and notify the researcher.

---

## 8. Operational secrets

### 8.1 What counts as a secret

For LSB, a secret is anything that grants access to a billed account, a write-capable API surface, or a private data store. The full list:

- **LLM provider API keys** — `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `HUGGINGFACE_API_KEY`, optionally `OPENAI_API_KEY` and `GOOGLE_API_KEY`
- **Backblaze B2 credentials** — `B2_KEY_ID`, `B2_APPLICATION_KEY`
- **Slack webhook URLs** — `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`. Webhook URLs are themselves credentials — anyone with the URL can post to the channel — and must be treated like API keys.
- **Cloudflare API token** — only used if Phase 6 moves the publish flow to a Cloudflare API call rather than git-push (currently not used)
- **GitHub Actions secrets** — managed via the GitHub repo settings, never copy-pasted out of the GitHub UI
- **SSH private keys** — Mark's main SSH key for `lsb-agent-01`, the rsync-only key for the Synology NAS
- **Password manager master password** — the meta-secret

### 8.2 Where secrets live

| Secret | Lives in | Lives nowhere else |
|---|---|---|
| LLM provider API keys | `lsb-agent-01:/opt/lsb-agent/.env`, mode 600, owned `lsb:lsb` | Not on Mark's local machine, not in any GitHub Actions secret, not in any cloud sync |
| B2 credentials | Same as above | Same |
| Slack alerts webhook URL | Both `lsb-agent-01:/opt/lsb-agent/.env` AND GitHub Actions secrets (because both `qa_check.py` on the VPS and `weekly-cost-alert.yml` on GitHub Actions need it) | Nowhere else |
| Slack CDA SME webhook URL | Mark's local Claude Code environment (the agent runtime reads it from there) | Not on the VPS |
| Slack UI/UX webhook URL | Mark's local Claude Code environment | Not on the VPS |
| SSH private keys | Mark's local `~/.ssh/` directory, encrypted at rest by the OS keychain | The matching public keys are in `~/.ssh/authorized_keys` on the VPS and on the NAS |
| Password manager master password | In Mark's head | Plus a sealed-envelope printout in the fireproof safe (last resort) |

The principle is **single-location storage by default**. A secret should live in exactly one place unless there's a specific reason for it to live in two places (which is true for the alerts webhook URL because it's read by two different runtimes).

### 8.3 What never goes near secrets

- **No secret is ever committed to git.** `.env` is in `.gitignore`; `.env.example` is the tracked template with placeholder values.
- **No secret is ever logged.** The adapter base class scrubs keys from any request payload before writing to the raw lake (`ARCHITECTURE.md` §6.3). Custom logging in `cdb_collect` must not log raw request headers.
- **No secret is ever included in an error message displayed to a user.** The dashboard does not error-message at users; CLI error messages on `lsb-agent-01` go to journald and are not surfaced to the dashboard or to Slack.
- **No secret is ever sent to a third-party service** (no error tracking SaaS, no APM, no log aggregation outside what's already trusted).

### 8.4 Rotation cadence

Secrets are rotated:

- **Immediately** on any suspected compromise per the §6.4 procedure
- **Every 12 months** as a hygiene practice, even with no suspected compromise. Rotation is calendared on Mark's personal calendar with a 30-day reminder.
- **Whenever a credential leaves Mark's exclusive control** (e.g., if the password manager's cloud sync is suspected of being accessed by anyone else)

The 12-month hygiene rotation is best-effort, not a hard rule. The immediate-on-compromise rotation is a hard rule.

---

## 9. Reviewer agent rules table

The Reviewer agent enforces the following rules on every PR. This table is **the canonical reference** for what the Reviewer is checking; if a rule is not listed here, the Reviewer is not enforcing it. Rules are numbered for easy citation in PR review comments.

| # | Rule | Where defined |
|---|---|---|
| **R1** | **No secret in any committed file.** `gitleaks` is the mechanical enforcement; the Reviewer agent backs it up by visually scanning any file containing key-shaped strings. | §3.4, §8 |
| **R2** | **No `dangerouslySetInnerHTML`** (or React equivalent) **anywhere in the dashboard.** All LLM-generated text uses the `SanitizedLLMText` wrapper from §3.3. | §3.3 |
| **R3** | **No CSP weakening.** Any change to `apps/dashboard/public/_headers` that adds `'unsafe-eval'`, removes `frame-ancestors 'none'`, removes the script-src restriction, or otherwise broadens the CSP requires Architect sign-off and a noted architectural decision in `ARCHITECTURE.md`. | §3.1 |
| **R4** | **No edits to existing lines in `data/raw/informants.jsonl`.** The append-only check in CI is the mechanical enforcement; the Reviewer agent backs it up by rejecting any diff that modifies pre-existing lines. | §7.1 |
| **R5** | **No new dependency without Architect sign-off.** Any change to `pyproject.toml`, `uv.lock`, `apps/dashboard/package.json`, or `apps/dashboard/package-lock.json` that adds a new top-level dependency requires Architect sign-off and an entry in §4.3. | §4.3 |
| **R6** | **No LLM client imports in `cdb_analyze/`.** The static check in CI is the mechanical enforcement; the Reviewer agent backs it up by rejecting any PR that imports an LLM client library inside `packages/cdb_analyze/`. | §3.5, `ARCHITECTURE.md` §1 commitment 6 |
| **R7** | **`InformantRecord` and `GroundingRef` schema changes co-update `docs/DATA_DICTIONARY.md`.** Any PR that touches these schemas in `cdb_core/schemas.py` must include a matching update to the data dictionary in the same PR. | `ARCHITECTURE.md` §5.1 Reviewer rule 5 |
| **R8** | **Frontend PRs carry a UI/UX agent verdict.** Any PR touching `apps/dashboard/`, `DESIGN_SYSTEM.md`, or any visual component must have a UI/UX agent PASS or PASS-WITH-NOTES verdict in `#lsb-ui-ux` linked from the PR description. | `ARCHITECTURE.md` §5.1 Reviewer rule 6 |
| **R9** | **Researcher grounding submission PRs run the full validation suite.** CI must run schema check, format check, item-intersection report, `gitleaks`, AND the PII scan (`scripts/check_grounding_pii.py`) on every PR that adds files under `data/grounding/`. The CDA SME agent must also have reviewed and posted a verdict to `#lsb-cda-sme`. | §7.4, `ARCHITECTURE.md` §4.2.5 |
| **R10** | **Webhook URL secrets are never committed.** Specific case of R1, listed separately because Slack webhook URLs are easy to mistake for non-secret configuration. | §8.1 |
| **R11** | **`SECURITY.md` at the repo root cannot be materially weakened.** Changes to the contact email, the SLA, or the disclosure process require Architect sign-off. | §6.5 |
| **R12** | **The §1.5.4 language guardrails apply to every piece of generated text.** This is enforced by both the CDA SME agent (during plan review) and the Reviewer agent (during PR review). The Reviewer specifically checks generated ledes, social posts, dashboard copy, README content, commit messages, and PR descriptions. | `ARCHITECTURE.md` §1.5.4 |

A FAIL on any of R1–R12 blocks merge. PASS-WITH-NOTES is acceptable as long as the notes are addressed in a follow-up commit before merge. PASS is the only verdict that allows merge unmodified.

---

## 10. Future hardening (deferred from v1)

These are real security improvements that LSB does not adopt in v1. Each has a defensible reason for deferral and a trigger condition that would make it worth revisiting.

### 10.1 Paid penetration test

**v1 status:** deferred. Friendly review only — Mark or a trusted collaborator walks through the dashboard and the deployment looking for obvious issues. Per resolved decision #19 in `ARCHITECTURE.md` §7.

**Trigger to revisit:** the project gets significant traction (sustained traffic in the high four-figure / low five-figure unique visitors per month), or a high-profile finding draws specific adversarial attention.

**Estimated cost when triggered:** $5K–15K for a focused web application pentest from a reputable firm. Higher for a broader engagement.

### 10.2 Bug bounty program

**v1 status:** deferred. Per resolved decision #20.

**Trigger to revisit:** sustained traffic that justifies the operational overhead of triaging reports, or a security incident that suggests structured external review would help.

**Cost when triggered:** typically a flat platform fee plus per-bounty payouts. HackerOne and Bugcrowd are the established platforms; Bountysource is the open-source-friendly option.

### 10.3 Cloudflare paid tier (WAF, bot management, image optimization)

**v1 status:** deferred. Free tier covers v1 traffic per resolved decision #21.

**Trigger to revisit:** sustained reputational attacks (abusive traffic, scraping, distributed credential stuffing against any future auth surface), or growth past the free tier's traffic envelope.

**Cost when triggered:** $20/month for Cloudflare Pro, more for Business or Enterprise tiers depending on what features become necessary.

### 10.4 Eliminate `'unsafe-inline'` from `style-src`

**v1 status:** deferred. Tailwind forces `'unsafe-inline'` for styles per resolved decision #22; LSB accepts this for v1 with Reviewer tracking.

**Trigger to revisit:** the dashboard build moves to fully external stylesheets (Tailwind compiles to a single CSS bundle and the inline-style usage is eliminated), or a CSP-related vulnerability emerges that makes eliminating inline styles worth the build complexity.

**Effort when triggered:** moderate — requires a Tailwind build configuration change and verification that no component is using inline styles via `style={...}` props.

### 10.5 Independent supply-chain attack detection

**v1 status:** deferred. Dependabot + `gitleaks` are the v1 defense; per §1.2 advanced supply-chain attacks are explicitly out of scope.

**Trigger to revisit:** a confirmed supply-chain compromise of a Python or npm package LSB depends on (transitively or directly), or general LSB visibility growing to the point where supply-chain attackers might target the project specifically.

**When triggered:** add `sigstore` for release signing, `syft` for SBOM generation, and a curated package-mirror policy. Significant operational overhead; not justified at v1 scale.

### 10.6 Hardened observability stack

**v1 status:** deferred. Structured logging to journald + the QA_Runner alert path are sufficient per `ARCHITECTURE.md` §6.4.

**Trigger to revisit:** sustained operational issues that require historical metric analysis (e.g., latency degradation over time across providers, slow drift in collection success rates).

**When triggered:** add Prometheus + Grafana on `lsb-agent-01`, or a hosted alternative. Avoid Datadog and other commercial observability SaaS for cost reasons.

### 10.7 Multi-region hosting

**v1 status:** deferred. Single Helsinki VPS is fine.

**Trigger to revisit:** the project has SLA commitments that single-region deployment can't meet, or the Helsinki region has sustained reliability issues.

**When triggered:** add a second VPS in a different region, set up active-passive replication for `data/raw/`, switch DNS to a load-balancing or failover configuration. Significant operational overhead.

---

## 11. The security posture in one paragraph

LSB is a small research project that makes public claims about commercial AI products and accepts contributions from external researchers. Its security posture is built around three commitments: data integrity (append-only canonical raw data with cryptographic provenance and a four-layer backup chain), credential isolation (single-location secret storage, no SMS-second-factor anywhere, two YubiKeys on every critical account, dedicated security email separate from Mark's personal life), and small attack surface (static dashboard with strict CSP, no LLM-generated HTML, no realtime backend, minimal dependency footprint, single-VPS collection runner). The project does not defend against nation-state adversaries, insider threats, or advanced supply-chain attacks. It does defend against the realistic threats: credential phishing, accidental key commits, dependency vulnerabilities, LLM-output XSS, researcher submissions with PII, and tampering with the raw data lake. The Reviewer agent enforces twelve specific rules on every PR; the §10 deferred items are real improvements that v1 doesn't need yet.

---

*End of `SECURITY_AND_HARDENING.md` v0.1. Section numbering is stable per the contract at the top — `ARCHITECTURE.md` cross-references depend on it. The Reviewer agent enforces §9. The §10 deferred items are revisited if the trigger conditions in each subsection are met.*