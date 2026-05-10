/**
 * Article Header — STUB for T4.
 * Source: DESIGN_SYSTEM.md §2.1
 *
 * Renders the article title, subtitle (TAGLINE excerpt or placeholder),
 * and byline strip. Domain-driven content fills in T6.
 *
 * In T4, this renders with placeholder / loading copy.
 */

import { TAGLINE, SITE_NAME } from "../copy/framing";

interface ArticleHeaderProps {
  /** Article title. Defaults to a placeholder title for T4 stub. */
  title?: string;
  /** Whether the manifest is still loading. */
  loading?: boolean;
}

export function ArticleHeader({
  title = "How frontier AI models organize cultural-domain vocabulary",
  loading = false,
}: ArticleHeaderProps) {
  return (
    <header className="article-header">
      <p className="article-header__eyebrow" aria-label="Section: Explore domains">
        DOMAIN · EXPLORE
      </p>

      <h1 className="article-header__title">{title}</h1>

      <p className="article-header__subtitle">
        {loading ? "Loading…" : TAGLINE}
      </p>

      <div className="article-header__byline-strip">
        <span>By {SITE_NAME}</span>
        <span className="article-header__byline-separator" aria-hidden="true">·</span>
        <time dateTime="2026">{new Date().getFullYear()}</time>
        <span className="article-header__byline-separator" aria-hidden="true">·</span>
        <a href="/methodology" aria-label="Read the full methodology">Methodology</a>
        <span className="article-header__byline-separator" aria-hidden="true">·</span>
        <a href="#cite" aria-label="How to cite this work">Cite</a>
        <span className="article-header__byline-separator" aria-hidden="true">·</span>
        <span>CC BY 4.0</span>
      </div>
    </header>
  );
}
