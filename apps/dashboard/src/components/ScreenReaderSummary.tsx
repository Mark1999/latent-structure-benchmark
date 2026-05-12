/**
 * ScreenReaderSummary — visually hidden prose description for screen readers.
 *
 * Phase 6 T8. Renders a sr-only <p> element containing programmatic summary
 * text for each visualization. Always present in the DOM regardless of
 * readAsTable toggle state — screen-reader users get the summary in both modes.
 *
 * The text prop is the output of one of the three template functions in
 * src/copy/screen_reader_summaries.ts (mdsScreenReaderSummary,
 * freeListScreenReaderSummary, similarityScreenReaderSummary).
 *
 * Placement: immediately after the existing <h2 className="sr-only"> bridge in
 * each viz component's root, before any conditional toggle state.
 *
 * Does NOT use generated_lede (CDA SME S11 binding).
 * Does NOT import any LLM client (CLAUDE.md §6 R11).
 *
 * Reference:
 *   docs/status/2026-05-12-phase6-T8-architect-plan.md §2.5
 *   docs/status/2026-05-12-phase6-T8-cda-sme-verdict.md §2
 *   docs/status/2026-05-12-phase6-T8-uiux-plan-verdict.md
 */

export interface ScreenReaderSummaryProps {
  /** Programmatic summary text — output of one of the three SR template functions. */
  text: string;
}

export function ScreenReaderSummary({ text }: ScreenReaderSummaryProps) {
  if (!text) return null;
  return (
    <p className="sr-only screen-reader-summary">{text}</p>
  );
}
