/**
 * MethodologySummary — article-bottom methodology note.
 *
 * Per DESIGN_SYSTEM.md §12.7 (v0.4.4, T13):
 *   - <section> with aria-labelledby → accessible landmark.
 *   - <h2 "About this measurement"> — binding heading text.
 *   - Tagline paragraph: --color-text-caption, medium weight (WCAG AA, F-T13-7).
 *   - Body paragraph: six SME-approved sentences, verbatim.
 *   - Footnote: plain text when methodologyPageUrl is null (F-T13-5);
 *     inline link when URL is set (Phase 6+).
 *   - Cascade wrapper at App.tsx level (F-T13-6).
 *
 * Source: docs/status/2026-05-11-phase5-T13-cda-sme-verdict.md (SME PASS-WITH-NOTES)
 *         docs/status/2026-05-11-phase5-T13-uiux-plan-verdict.md (UI/UX PASS-WITH-NOTES)
 */

import { methodologySummary, methodologyFootnote, taglineQuote } from "../copy/methodology_summary";

export interface MethodologySummaryProps {
  methodologyPageUrl?: string | null;
}

export function MethodologySummary({ methodologyPageUrl = null }: MethodologySummaryProps) {
  return (
    <section
      className="methodology-summary"
      aria-labelledby="methodology-summary-heading"
    >
      <h2 id="methodology-summary-heading" className="methodology-summary__heading">
        About this measurement
      </h2>
      <p className="methodology-summary__tagline">{taglineQuote}</p>
      <p className="methodology-summary__body">{methodologySummary}</p>
      <p className="methodology-summary__footnote">
        {methodologyPageUrl ? (
          <>
            {methodologyFootnote}{" "}
            <a href={methodologyPageUrl}>Read the full methodology page →</a>
          </>
        ) : (
          methodologyFootnote
        )}
      </p>
    </section>
  );
}
