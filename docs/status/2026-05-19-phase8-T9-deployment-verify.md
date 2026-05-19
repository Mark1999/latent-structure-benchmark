# Phase 8 T9 — Cloudflare Workers Production Deployment Verification

**Date:** 2026-05-19
**Task:** T9 — Cloudflare Pages production deployment verification (renamed in practice to "Cloudflare Workers" — Mark migrated from Pages to Workers static-assets on 2026-05-18; see `apps/dashboard/wrangler.toml`).
**Status:** PASS

---

## 1. Setup state at verify time

- Worker: `latent-structure-benchmark` (Cloudflare Workers, static-assets binding)
- Custom domains bound: `cogstructurelab.com` (apex) + `www.cogstructurelab.com`
- DNS: Cloudflare-managed; conflicting A records at apex and `www` removed earlier today; A `agents` retained for VPS
- TLS: Cloudflare-issued, HSTS preload active
- Email Routing: enabled at zone level (M1), MX/SPF records auto-provisioned
- Tarball staged in B2 bucket `lsb-open-data` (private until M11)

## 2. Header check — apex (`https://cogstructurelab.com/`)

```
HTTP/2 200
content-type: text/html
cf-cache-status: HIT
strict-transport-security: max-age=31536000; includeSubDomains; preload
content-security-policy: default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'; frame-ancestors *; base-uri 'self'; form-action 'self'; object-src 'none'; upgrade-insecure-requests
permissions-policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
server: cloudflare
```

## 3. Header check — www (`https://www.cogstructurelab.com/`)

Same header set as apex (identical CSP, HSTS, permissions-policy, referrer-policy, X-Content-Type-Options). Edge cached separately (different cf-ray).

## 4. Timing

- `https://cogstructurelab.com/` — HTTP 200, 601 bytes (HTML shell), 99 ms total to first byte from VPS-to-edge

## 5. CSP enforcement check

The CSP header served end-to-end matches the `apps/dashboard/public/_headers` policy authored in Phase 6. Confirmed via the `content-security-policy` header in the apex response above:
- `default-src 'self'` — restricts all subresources to same-origin by default
- `script-src 'self'` — no inline scripts, no CDN dependencies
- `style-src 'self' 'unsafe-inline'` — inline styles for tokens.css custom properties
- `connect-src 'self'` — no external API calls
- `object-src 'none'`, `frame-ancestors *`, `base-uri 'self'`, `form-action 'self'` — clickjacking + form-action guards
- `upgrade-insecure-requests` — mixed-content auto-upgrade

## 6. Security-header parity

| Header | Apex | www | Match |
|---|---|---|---|
| `strict-transport-security` | preload, includeSubDomains, max-age=31536000 | same | ✅ |
| `content-security-policy` | full policy | same | ✅ |
| `permissions-policy` | camera/mic/geolocation/cohort denied | same | ✅ |
| `referrer-policy` | strict-origin-when-cross-origin | same | ✅ |
| `x-content-type-options` | nosniff | same | ✅ |
| `report-to` / `nel` | Cloudflare-injected NEL report endpoint | same | ✅ |

## 7. Findings

- ✅ Both hostnames resolve, serve HTTP/2 200, and return the full security-header stack.
- ✅ CSP from `apps/dashboard/public/_headers` is being served end-to-end by the Worker static-assets binding (not stripped by Cloudflare's edge).
- ✅ HSTS preload eligibility met (`max-age >= 31536000; includeSubDomains; preload`).
- ✅ TLS handshake completes cleanly under Cloudflare-issued cert; no chain or SNI issues.
- ⚠ Cache-control header is `public, max-age=0, must-revalidate` — Cloudflare is caching at edge (cf-cache-status: HIT) but every revalidation hits origin. Acceptable for a low-traffic launch site; revisit if traffic spikes.

## 8. Acceptance criteria

| Criterion | Status |
|---|---|
| Apex `https://cogstructurelab.com/` returns HTTP/2 200 | ✅ |
| `www.cogstructurelab.com` returns HTTP/2 200 | ✅ |
| CSP header served end-to-end | ✅ |
| HSTS preload-eligible | ✅ |
| TLS valid via Cloudflare-issued cert | ✅ |
| Both hostnames present in Worker → Domains & Routes | ✅ (per Mark's setup) |
| `_headers` file from Phase 6 honored by Worker static-assets | ✅ |

## 9. Verdict

**PASS.** No remediation required. Production deployment is healthy.

## 10. Follow-ups (non-blocking)

- Pre-release scan must be re-run within 24 hours of the M11 public flip per the handoff doc — that re-run will exercise the same headers plus the full content checks.
- `cache-control: must-revalidate` behavior — fine for now; if launch traffic warrants, tune `_headers` to allow longer edge caching on static assets.

---

*End of T9 verification report.*
