# CDA SME Verdict — PROMOTE-1 (re-baseline promotion to live, 2026-05-30)

**Date:** 2026-05-30
**Scope:** Two linked asks for promotion of the 2026-05-29 staged re-baseline (NumPy 2.4.4 / SciPy 1.17.1) to live:
  - **Ask 1 (T-A data promotion):** blessing the one visible public-number change — family Smith's S rendering shifts "0.80" → "0.81" (underlying 0.803321 → 0.805244), and the matching `tests/cdb_publish/test_lede.py` L199 update.
  - **Ask 2 (T-B provenance copy):** authoring the binding methodology-page data-provenance paragraph + confirming the footer string contract.
**Companion docs:** `docs/status/2026-05-29-rebaseline-cda-sme-verdict.md` (the binding N1–N3 + T-1..T-6 origin), `docs/status/2026-05-29-rebaseline-completion.md` (guard-clear evidence), `ARCHITECTURE.md` §1.5 + §1.5.4, CLAUDE.md §7.
**Routing:** This verdict gates T-A (data promotion + lede test update) and T-B (methodology-page paragraph placement + footer string). UI/UX gates layout; Reviewer gates the test/file diff.

---

## Verdict: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| 1 — Protocol validity | PASS |
| 2 — Analytical validity | PASS |
| 3 — Claims validity | PASS-WITH-NOTES |
| 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

The PASS-WITH-NOTES axes carry forward the binding N1–N3 audience-translation rules from the 2026-05-29 verdict and operationalize them into the exact prose below. No new methodological objection; the substance of the re-baseline is the same event the 2026-05-29 verdict already blessed under the guard-clear condition (which the completion record confirms was met on all three domains).

---

## Ask 1 — public-number change is acceptable rounding-level drift. APPROVED.

**Ruling:** Shipping the family lede with "Smith's S = 0.80" → "Smith's S = 0.81" is an acceptable rounding-level reproducibility change. The Coder is authorized to promote the staged family corpus to live and update `tests/cdb_publish/test_lede.py` L198–L201 from `"Smith's S = 0.80"` to `"Smith's S = 0.81"` in the same commit as the data promotion.

**Rationale, axis by axis.**

- **Analytical validity (PASS).** The underlying shift is 0.803321 → 0.805244, a Δ of 0.0019 (~0.24% relative). The 2026-05-29 verdict Q5 sized this as "two orders of magnitude inside the published `consensus_ci` width" — invisible in the published uncertainty surface. The 2-decimal display rounding is the *only* reason this shift is publicly visible at all; on a single more decimal it would not have crossed a rendering boundary. The published 95% CI rounds identically ([0.64, 0.94] under both toolchains: 0.6406→0.6438 and 0.9433→0.9425 both round to 0.64 and 0.94). The CI bracket the lede displays is bit-stable; only the point estimate's last shown digit moves.

- **Claims validity (PASS-WITH-NOTES — note A1 below).** No classification, lede-class, or interpretive claim changes. The T-1..T-6 guard cleared on all three domains per the completion record. Family stays STRONG_CONSENSUS; the `strong_consensus_homogeneous` lede pattern is unchanged; only the rendered digit "0.80" → "0.81" moves. Holidays' rendered point estimate ("0.88") and food (bit-identical) are unaffected. This is the textbook definition of a rounding-level shift, and the 2026-05-29 verdict pre-authorized this class of change as in-scope for promotion under the audience-translation surfaces in N1–N3.

- **Audience translation (PASS-WITH-NOTES — note A2 below).** A returning reader who remembered "0.80" and now sees "0.81" is exactly the reader the N1 methodology-page paragraph and the N2 manifest link exist for. Their one-click path to "why did this number move?" must land before the promotion (Ask 2 below provides the prose).

**Note A1 (binding — claims validity).** The promotion commit body MUST reference both this verdict file and the 2026-05-29 rebaseline verdict by path, so the audit trail across the two CDA SME approvals is greppable from `git log`. The 2026-05-29 verdict pre-authorized rounding-level promotion conditional on the guard clearing; the completion record confirms the guard cleared; this verdict converts that conditional authorization into an active green light.

**Note A2 (binding — audience translation).** Ask 1 (data promotion + test update) MUST NOT ship without Ask 2 (methodology-page paragraph + footer + manifest link) landing in the same release. The "0.80" → "0.81" change without the provenance paragraph would land a number movement on the dashboard with no explanation surface; that is exactly the audience-translation hole N1–N3 were authored to close. T-A and T-B are linked, not sequential.

**Note A3 (advisory).** When updating `tests/cdb_publish/test_lede.py` L199, also update the trailing comment on L198 to reflect the new value: change `# Smith's S = 0.8033... → "0.80" (was 0.71; updated to current corpus)` to something like `# Smith's S = 0.8052... → "0.81" (was 0.80 pre-rebaseline; updated under pinned NumPy 2.4.4 / SciPy 1.17.1, 2026-05-30)`. This keeps the test file self-documenting for future researchers reading the assertion in isolation. Non-blocking — Coder may use slightly different wording — but the historical breadcrumb is worth preserving.

---

## Ask 2 — methodology-page data-provenance paragraph (binding final copy)

The paragraph below is the binding, final copy. The Coder places it verbatim; UI/UX gates layout (heading level, placement within the methodology page, link styling); Reviewer confirms byte-identity against this verdict file.

### Approved paragraph (place verbatim)

> **Data provenance.** The published corpus was recomputed on 2026-05-30 under a pinned analytical toolchain (NumPy 2.4.4, SciPy 1.17.1, Python 3.12) so that any researcher with the open data bundle can reproduce the published numerics on their own machine. The prior figures were valid under the toolchain that produced them; what changed is that LSB now pins the NumPy and SciPy versions used for all bootstrap and MDS computations, where previously those versions were whatever the host environment happened to have installed. Values shifted at the third or fourth decimal in bootstrap- and MDS-derived quantities (the smallest visible effect on this site is family's Smith's S moving from 0.80 to 0.81 at two-decimal rendering); deterministic quantities such as Smith's S point estimates before display rounding, OCI, and Romney eigenratios that drive the consensus-type classification are unaffected at any boundary, and no consensus classification, model ordering, or relative geometry on the MDS maps has changed. The pinned versions and the exact git commit are recorded in [`provenance.json`](/data/provenance.json), which is regenerated on every published bundle.

### Content audit against N1–N3 (binding requirements)

- **N1 — re-baseline date + toolchain versions verbatim:** "recomputed on 2026-05-30 under a pinned analytical toolchain (NumPy 2.4.4, SciPy 1.17.1, Python 3.12)." Satisfies. (Date is promotion date 2026-05-30, not the regen date 2026-05-29; this is correct because the methodology page describes what the *currently rendered* corpus reflects, and the currently rendered corpus is the promoted one. The exact `generated_at` timestamp lives in `provenance.json` for any reader who wants the regen-vs-promotion distinction.)
- **N3 — no "wrong/right" or "corrected" framing:** "The prior figures were valid under the toolchain that produced them; what changed is that LSB now pins the NumPy and SciPy versions…" Satisfies. The defect is named as *unpinning*, not as an error in the numerics or the methodology. No use of "incorrect," "corrected," "fixed," "bug," or "error."
- **N3 — rounding-level disclosure:** "Values shifted at the third or fourth decimal in bootstrap- and MDS-derived quantities… no consensus classification, model ordering, or relative geometry on the MDS maps has changed." Satisfies, with the additional honest disclosure of the single visible 0.80→0.81 family rendering shift so a returning reader is not surprised. This is the audience-translation move that lets the methodology paragraph also serve as the explanation surface for note A2's "one-click why-did-this-move" need.
- **N2 — manifest link:** `[`provenance.json`](/data/provenance.json)` is linked inline. UI/UX may adjust the href to match the actual published path (Mark's canonical single-artifact choice); the link must remain in the paragraph itself, not relegated to a footnote.
- **§1.5 / §7 vocabulary compliance:** No "worldview," "believes," "thinks," "cultural bias" (standalone), or any §1.5.4 forbidden phrase. Paragraph describes a numerical procedure under a pinned toolchain — no claims about what the models "think." PASS.
- **No "publishable" / "closer to human = better" claims:** N/A; paragraph is about provenance, not findings. PASS.

### Note A4 (binding — link target).

The hyperlink target `/data/provenance.json` in the paragraph is a placeholder for whatever path the Coder lands the canonical single artifact at. UI/UX and the Coder must agree on the actual public URL before promotion; the only binding rule is that the link is in-paragraph (not a footnote or "see also") and resolves to the canonical artifact, not to a redirect or to a directory listing.

### Note A5 (binding — placement).

Place the paragraph as the FIRST paragraph of a "Data provenance" section on the methodology page (creating the section if it does not yet exist), positioned above any pre-existing version-stamp / changelog block. Rationale: a reader who notices a number movement is going to search the methodology page for "provenance," "version," or "change" — landing them in a section so titled, with this paragraph as the lede, satisfies the one-click expectation in note A2. UI/UX gates the exact heading level and the typographic treatment.

---

## Footer string contract (Ask 2 supplementary) — APPROVED with refinement

**Mark's proposed footer:** "Calculated with NumPy 2.4.4 and SciPy 1.17.1"

**Ruling:** APPROVED with one binding refinement and one advisory option.

### Note A6 (binding — footer must be a link, not bare text).

The footer string itself is fine, but the 2026-05-29 verdict N2 requires that "the 'Calculated with NumPy X / SciPy Y' footer must also link to or surface the manifest." The bare-text version of the footer does not satisfy N2. The full footer contract that earns PASS is:

> Calculated with [NumPy 2.4.4 and SciPy 1.17.1](/data/provenance.json).

Where the bracketed text is the link to the canonical `provenance.json` artifact. UI/UX gates whether the link surface is the version numbers themselves or a small icon/affordance adjacent to the text; the binding requirement is that there is a one-click path from the footer to the manifest, anywhere a reader sees the "Calculated with…" string.

### Note A7 (advisory, not blocking — Python).

The 2026-05-29 verdict N4 required `python_version` in the manifest because NumPy/SciPy C-extension behavior at the rounding level is also Python-release dependent. If Mark prefers a tighter footer, the current proposed string is fine — Python's contribution is recorded in `provenance.json` and reachable in one click. If Mark prefers a stronger surface honesty, an acceptable longer form is:

> Calculated with [NumPy 2.4.4, SciPy 1.17.1, Python 3.12](/data/provenance.json).

Either form earns PASS. The bare-text variant (no link) does not.

### Note A8 (binding — single source of truth).

The footer string MUST be sourced from the manifest at build time (or read from it at runtime, depending on the dashboard's build pipeline), not hard-coded in a frontend constants file. If the manifest says NumPy 2.4.5 in a future re-baseline, the footer must say 2.4.5 without a manual code change. This is the operational mechanism that prevents the footer from drifting out of agreement with the actual computation environment between re-baselines, and it is the practical reason a manifest exists. Implementation choice (build-time injection vs. runtime fetch) is the Coder's call; UI/UX gates the visual treatment.

---

## Register & vocabulary compliance

**Register compliance — PASS.** Promotion does not move any analytical method across the R1/R2/R3 boundary. The corpus was already regenerated; this is the publication step. No register reclassification.

**Vocabulary compliance — PASS.** Both the approved paragraph and the approved footer string have been audited against §1.5.4 + CLAUDE.md §7. Zero forbidden phrases. Zero "worldview," "believes," "thinks." Zero "wrong/right" or "corrected" framing per N3. Zero "publishable" or "closer to human = better" claims.

---

## Required before promotion ships (consolidated)

1. **Note A2 (binding)** — T-A (data + test update) and T-B (paragraph + footer + manifest link) ship in the same release. Not sequential.
2. **Note A1 (binding)** — promotion commit body references both this verdict and the 2026-05-29 rebaseline verdict by path.
3. **Note A4 (binding)** — methodology-page paragraph link target resolves to the canonical published `provenance.json` artifact at whatever public path Mark/UI/UX choose.
4. **Note A5 (binding)** — paragraph placed as the lede of a "Data provenance" section on the methodology page (create the section if it does not exist).
5. **Note A6 (binding)** — footer string is a one-click link to the manifest, not bare text.
6. **Note A8 (binding)** — footer string sourced from the manifest, not hard-coded.

## Advisory (not blocking)

7. **Note A3** — update the trailing comment on `tests/cdb_publish/test_lede.py` L198 to reflect the new value and reference the pinned-toolchain re-baseline.
8. **Note A7** — Mark's choice between the short footer ("Calculated with NumPy 2.4.4 and SciPy 1.17.1") and the longer Python-inclusive footer; both earn PASS as long as A6/A8 are satisfied.

---

*PASS-WITH-NOTES. Promotion may proceed under the binding conditions above. T-A (data promotion + lede test update) and T-B (methodology-page paragraph + footer + manifest link) are linked and ship together; the Coder is authorized to bundle them in a single promotion commit since they form one atomic publishing event. Reviewer confirms byte-identity of the approved paragraph against this verdict file.*
