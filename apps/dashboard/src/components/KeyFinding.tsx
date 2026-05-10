/**
 * KeyFinding — the lede sentence strip per DESIGN_SYSTEM.md §3.8.
 *
 * Renders the pre-generated lede from the published domain JSON. Styled with
 * a 4px --color-model-1 border-left, light gray background, 780px max-width.
 *
 * Domain-switch animation:
 *   200ms fade-out then fade-in when generatedLede changes (§3.8 binding).
 *   Implemented via key-change strategy: the inner content element receives a
 *   key prop derived from the lede string, forcing a remount and restarting the
 *   CSS animation. Per prefers-reduced-motion: reduce — animation is disabled.
 *
 * Accessibility:
 *   - Outer wrapper: role="region" aria-label="Key finding" (§7)
 *   - Inner content: aria-live="polite" so screen readers announce the new lede
 *     on domain switch without requiring the user to navigate to the element.
 */

export interface KeyFindingProps {
  generatedLede: string;
}

/**
 * Produce a short, stable key string from the lede so the inner element
 * remounts (triggering the CSS fade animation) when the domain changes.
 * We use the first 40 characters as a cheap discriminator; full string
 * equality would also work but first-40 avoids allocating a hash.
 */
function ledeKey(lede: string): string {
  return lede.slice(0, 40);
}

export function KeyFinding({ generatedLede }: KeyFindingProps) {
  return (
    <section
      className="key-finding"
      role="region"
      aria-label="Key finding"
    >
      {/*
        The inner element receives key={ledeKey(generatedLede)}.
        When the domain switches and generatedLede changes, React unmounts
        and remounts this element, restarting the key-finding-fade CSS animation.
        The animation is wrapped in a prefers-reduced-motion guard in app.css.
      */}
      <p
        key={ledeKey(generatedLede)}
        className="key-finding__content"
        aria-live="polite"
      >
        {generatedLede}
      </p>
    </section>
  );
}
