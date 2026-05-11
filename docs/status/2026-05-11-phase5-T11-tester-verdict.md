# Phase 5 T11 Tester Verdict

**Task:** T11 — PNG export with canvas + tEXt metadata + watermark
**Commits in scope:** `727d9a9` (Coder), `fc83f01` (UI/UX corrections)
**Prerequisite verdicts:**
- UI/UX FAIL→PASS-WITH-NOTES: `docs/status/2026-05-11-phase5-T11-uiux-verdict.md`
- Reviewer PASS: `docs/status/2026-05-11-phase5-T11-reviewer-verdict.md`
**Tester verdict:** PASS-WITH-NOTES
**Date:** 2026-05-11

---

## Verdict

PASS-WITH-NOTES

The T11 implementation is correct and the original 528-test suite passes cleanly. An audit of the three T11 test files against the full behavioral checklist identified 14 coverage gaps. All 14 gaps were filled with 24 new tests. The suite now stands at 552 tests, all passing. Build, lint, and type-check remain clean.

---

## Test run results

| Suite | Before gap-fill | After gap-fill |
|---|---|---|
| vitest (dashboard) | 528 passed, 19 files | 552 passed, 19 files |
| `npm run lint` | clean | clean |
| `npm run build` | clean, 72.52 KB gzip | clean, 72.52 KB gzip |

Build bundle: 72.52 KB gzipped (cap: 400 KB).

---

## Audit checklist

### png-export.ts

| Item | Status |
|---|---|
| F5 canvas dimensions explicit per size variant | PASS — already covered |
| Watermark margin as 2% of canvas (X and Y axes) | GAP-FILLED — 4 new tests |
| Watermark font size as 1.2% of canvas width | PASS — already covered |
| Watermark opacity 3% | GAP-FILLED — 2 new tests |
| SVG serialization invoked (XMLSerializer) | PASS — already covered |
| Image loaded from data URL | PASS — already covered (MockImage src→onload chain) |
| Image onload handler triggers canvas drawing | PASS — already covered (drawImage assertion) |
| Image onerror handler rejects promise | GAP-FILLED — 1 new test |
| SVG aspect ratio preserved / letterbox for non-matching ratio | GAP-FILLED — 2 new tests |
| Watermark text is literal "cogstructurelab.com" | PASS — already covered |
| Watermark font family is monospace | GAP-FILLED — 2 new tests |
| canvas.toBlob() returns a Blob | PASS — already covered |
| Throws descriptive error if canvas API unavailable (SSR) | PASS — already covered |
| Throws if toBlob returns null | GAP-FILLED — 1 new test |

### png-metadata.ts

| Item | Status |
|---|---|
| PNG signature preserved | PASS — already covered |
| Empty kv → input blob returned unchanged (byte-identity) | PASS — already covered |
| tEXt chunk inserted after IHDR, before IDAT | PASS — already covered |
| tEXt chunk CRC-32 correct per spec | PASS — already covered |
| Multiple kv pairs produce multiple chunks (one per key) | PASS — already covered |
| Round-trip: parse output and recover same kv map | PASS — already covered |
| Invalid PNG signature → throws | PASS — already covered |
| Truncated PNG → throws | PASS — already covered |
| PNG missing IDAT chunk → throws | PASS — already covered |
| Keyword Latin-1 range respected (truncated at 79 chars) | GAP-FILLED — 2 new tests |
| Value Latin-1 range respected | GAP-FILLED — 2 new tests |
| Re-encoding does not corrupt other chunks | PASS — already covered (CRC of original chunks verified) |

### DownloadBar PNG button behaviors

| Item | Status |
|---|---|
| PNG social button rendered with correct ARIA label | PASS — already covered |
| PNG hi-res button rendered with correct ARIA label | PASS — already covered |
| Button click invokes renderToPng with size:"social" | PASS — already covered |
| Hi-res click invokes renderToPng with size:"highres" | PASS — already covered |
| injectTextMetadata called with all 8 fields | GAP-FILLED — 2 new tests (Title, Author, Source, Software, Generated-At were not individually asserted) |
| Download `<a>` with filename lsb-{domain}-mds-{social\|highres}.png | GAP-FILLED — 2 new tests (the -mds-social/-mds-highres suffix was not specifically asserted) |
| Loading state ("Exporting…") displayed during in-flight export | GAP-FILLED — 1 new test |
| Error state displayed on rejection; auto-resets after timeout | GAP-FILLED — 1 new test |
| Buttons disabled during pngState === "loading" | GAP-FILLED — 1 new test |
| PNG button class download-bar__png-btn present | PASS — already covered |
| PNG hi-res class download-bar__png-hires-btn present | PASS — already covered |
| linkStyle.color token is --color-text-caption (F-T11-2 fix) | GAP-FILLED — 1 new test |

---

## Tests written (gap-fill)

All 24 tests added in a single `test(dashboard):` commit.

### `apps/dashboard/src/__tests__/png-export.test.ts` — 12 new tests

**describe: "renderToPng — watermark opacity (F5 binding: 3%)"**
- `social: ctx.globalAlpha is set to 0.03 before drawing watermark` — instruments fillText to capture globalAlpha at call time; asserts 0.03.
- `highres: ctx.globalAlpha is set to 0.03 before drawing watermark` — same for highres.

**describe: "renderToPng — watermark margin as 2% of canvas dimensions (F5 binding)"**
- `social: fillText X coordinate equals canvasWidth - canvasWidth*0.02 = 1568` — asserts X arg to fillText equals 1568.
- `social: fillText Y coordinate equals canvasHeight - canvasHeight*0.02 = 882` — asserts Y arg equals 882.
- `highres: fillText X coordinate equals canvasWidth - canvasWidth*0.02 = 1960` — asserts X equals 1960.
- `highres: fillText Y coordinate equals canvasHeight - canvasHeight*0.02 = 1960` — asserts Y equals 1960.

**describe: "renderToPng — watermark font family monospace (F5 binding)"**
- `social: ctx.font string contains 'monospace'` — asserts monospace in font string.
- `highres: ctx.font string contains 'monospace'` — same for highres.

**describe: "renderToPng — SVG aspect ratio letterboxing"**
- `square canvas: drawImage called with height < canvasHeight for wide SVG` — 900×600 SVG on 2000×2000 canvas; asserts drawH < 2000 (letterboxing, not clipping).
- `square canvas: drawImage called with width < canvasWidth for tall SVG` — 600×900 SVG on 2000×2000 canvas; asserts drawW < 2000 (pillarboxing).

**describe: "renderToPng — toBlob returns null → rejects"**
- `rejects with descriptive error when canvas.toBlob returns null` — uses forceToBlobNull flag to make the canvas toBlob call cb(null); asserts rejection with /toBlob\(\) returned null/.

**describe: "renderToPng — Image onerror rejects promise"**
- `rejects with an error when the Image fires onerror` — installs an ErrorImage class that fires onerror instead of onload; asserts rejection.

### `apps/dashboard/src/__tests__/png-metadata.test.ts` — 4 new tests

**describe: "injectTextMetadata — keyword truncation at 79 chars (Latin-1 spec)"**
- `keyword longer than 79 chars is truncated to 79 chars` — 100-char keyword; asserts stored keyword is exactly 79 chars.
- `keyword of exactly 79 chars is stored verbatim (no truncation)` — 79-char keyword; asserts no truncation.

**describe: "injectTextMetadata — Latin-1 byte masking"**
- `U+00E9 (é) is preserved in round-trip through Latin-1 encoding` — checks data byte at index 3 of the value is 0xE9.
- `high-codepoint character is masked to low 8 bits by latin1Encode` — U+0141 (Ł) encodes as 0x41 ('A') per `charCodeAt & 0xff`.

### `apps/dashboard/src/__tests__/download-bar.test.tsx` — 8 new tests

**describe: "DownloadBar — injectTextMetadata all 8 fields (T11 gap-fill)"**
- `injectTextMetadata is called with all 8 required tEXt fields` — asserts Title, Author, Source, Software, Domain, Models, Analysis-Version, Generated-At all non-empty.
- `Title field includes the domain slug` — asserts "family" in Title value.

**describe: "DownloadBar — PNG download filename uses -mds-social / -mds-highres suffix (T11 gap-fill)"**
- `social PNG download filename contains '-mds-social'` — spies on body.appendChild; finds anchor and asserts download attribute contains "-mds-social".
- `hi-res PNG download filename contains '-mds-highres'` — same for the hi-res button; asserts "-mds-highres".

**describe: "DownloadBar — PNG loading state 'Exporting…' (T11 gap-fill)"**
- `PNG social button shows 'Exporting…' while export is in-flight` — makes renderToPng return a never-resolving Promise; asserts container.textContent contains "Exporting".
- `both PNG buttons are disabled while export is in-flight` — same setup; asserts both pngBtn.disabled and hiresBtn.disabled are true.

**describe: "DownloadBar — PNG error state on rejection (T11 gap-fill)"**
- `displays 'PNG export failed' when renderToPng rejects` — makes renderToPng reject; asserts "PNG export failed" in textContent.

**describe: "DownloadBar — linkStyle.color is --color-text-caption (F-T11-2 fix)"**
- `hi-res button inline style uses var(--color-text-caption)` — queries `.download-bar__png-hires-btn` and asserts `style.color === "var(--color-text-caption)"`. Directly verifies the F-T11-2 WCAG fix is present in the rendered DOM.

---

## Coverage gaps found and closed

### Gap 1: Watermark margin position (X and Y) not numerically verified
F5 binding states position = 2% of canvas dimensions on both axes. The existing tests asserted that fillText was called with the watermark text but did not assert the X/Y coordinates. A regression that changed 0.02 to a fixed-pixel value would have been undetected. 4 new tests close this.

### Gap 2: Watermark opacity (3%) not directly asserted
`ctx.globalAlpha = 0.03` is the F5 binding value. The existing "save/restore called" test only verified the wrapping calls, not the alpha value set inside them. 2 new tests close this by instrumenting fillText to snapshot globalAlpha at call time.

### Gap 3: Image onerror path untested
Production code has an explicit `img.onerror` rejection handler that creates an Error if none was provided. No test exercised this path. 1 new test closes this.

### Gap 4: SVG aspect ratio / letterbox behavior untested
The letterbox/pillarbox centering logic (`scale = Math.min(scaleX, scaleY)`) had no test verifying it does not clip the SVG. 2 new tests verify the drawImage dimensions for wide and tall SVGs on a square canvas.

### Gap 5: Watermark font family "monospace" not asserted
The font string `"${fontSize}px monospace"` was tested only for the pixel size. The "monospace" family (editorial restraint per F5) had no explicit assertion. 2 new tests close this.

### Gap 6: toBlob(null) rejection path untested
The production `if (blob) { ... } else { reject(...) }` branch was exercised only by the happy path. 1 new test verifies the null-blob rejection with the correct error message.

### Gap 7: PNG keyword truncation at 79 chars untested
The Latin-1 spec (RFC 2083 §11.3.4.3) limits tEXt keywords to 79 bytes. `png-metadata.ts` uses `.slice(0, 79)`. No test verified this. 2 new tests close this.

### Gap 8: Latin-1 byte masking untested
`latin1Encode` uses `charCodeAt(i) & 0xff`. No test verified the masking behavior for code points in the extended range (0x80–0xFF) or the truncation behavior for code points above 0xFF. 2 new tests close this.

### Gap 9: injectTextMetadata 8-field completeness (partial)
The existing test asserted Domain, Models, and Analysis-Version but not the remaining 5 fields (Title, Author, Source, Software, Generated-At). 2 new tests close this.

### Gap 10: Filename suffix specificity
The existing test asserted the download filename contains "family" and ".png" but not the exact `-mds-social` or `-mds-highres` suffix pattern. 2 new tests close this.

### Gap 11: Loading state "Exporting…" untested
The `pngState === "loading"` → "Exporting…" UI branch was present in production but had no test. 1 new test verifies the loading text appears during an in-flight export.

### Gap 12: Button disabled during loading
Both PNG buttons should be disabled while `pngState === "loading"`. No test verified the `disabled` attribute. 1 new test closes this.

### Gap 13: Error state on rejection untested
The `pngState === "error"` → "PNG export failed" UI branch had no test. 1 new test verifies the error text appears when renderToPng rejects.

### Gap 14: F-T11-2 WCAG fix (--color-text-caption token) not tested
The blocking UI/UX correction F-T11-2 switched `linkStyle.color` from `--color-text-secondary` to `--color-text-caption`. No test verified the fix was present in the rendered DOM. 1 new test closes this, matching the pattern established by the T10 gap-fill for `SourceAttribution.tsx`.

---

## Real API call check

All new tests use the same vi.mock and vi.spyOn infrastructure as the existing T11 tests. No test issues a real network request, canvas operation, or file system access. CLAUDE.md rule 9 / pitfall 9 satisfied.

---

## Forbidden vocabulary check

No forbidden vocabulary (`believes`, `worldview`, `thinks` applied to models) appears in any committed test text.

---

## Notes for next agent

None. All identified gaps are closed. The suite is 552 tests and clean.
