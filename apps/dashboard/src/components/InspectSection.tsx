/**
 * InspectSection — wrapper component for a named section on the operator inspect page.
 *
 * Renders <section aria-labelledby={id}> with a single <h2> heading.
 * No <h3> or lower-level headings are produced by this component.
 *
 * UI/UX binding F-T0-A1: id is derived from title via
 *   title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
 * All section titles on a single page must be unique (caller's responsibility;
 * the §2.4 field coverage table guarantees uniqueness for all known sections).
 *
 * Design system tokens: DESIGN_SYSTEM.md §1.
 */

import type { ReactNode } from "react";

interface InspectSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
}

/**
 * Derive a valid HTML id from a section title.
 * Lowercases, replaces spaces with hyphens, strips non-alphanumeric/hyphen chars.
 */
function titleToId(title: string): string {
  return title
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "");
}

export function InspectSection({ title, description, children }: InspectSectionProps) {
  const id = titleToId(title);
  return (
    <section className="inspect-section" aria-labelledby={id}>
      <h2 id={id} className="inspect-section__heading">
        {title}
      </h2>
      {description && (
        <p className="inspect-section__description">{description}</p>
      )}
      {children}
    </section>
  );
}
