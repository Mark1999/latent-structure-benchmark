/**
 * MethodologyPagePlaceholder — rendered at /methodology.
 * Source: DESIGN_SYSTEM.md §2.1 (Header + Footer chrome, max-prose-width),
 *         Phase 8 T10.1 plan, UI/UX verdict 2026-05-19-phase8-T10-ui-ux-verdict.md.
 *
 * Placeholder state: <h1> + "in preparation" prose + ARCHITECTURE.md §1.5 link.
 * Full copy ships in T10.3 after CDA SME sign-off.
 *
 * No new visual decisions: uses page-wrapper / page-main / methodology-summary
 * container classes already defined in app.css (methodology-summary block
 * provides max-prose-width, margin, padding consistent with home-page chrome).
 */

import { Header } from "./Header";
import { Footer } from "./Footer";
import { pageTitle, pageBody, archLinkText, archLinkHref } from "../copy/methodology_page";

export function MethodologyPagePlaceholder() {
  return (
    <div className="page-wrapper">
      <Header />
      <main className="page-main">
        <div className="methodology-summary">
          <h1 className="methodology-summary__heading">{pageTitle}</h1>
          <p className="methodology-summary__body">{pageBody}</p>
          <p className="methodology-summary__body">
            See{" "}
            <a
              href={archLinkHref}
              rel="noopener noreferrer"
            >
              {archLinkText}
            </a>{" "}
            for the current methodology specification.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
