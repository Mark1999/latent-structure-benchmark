/**
 * Site Footer — scientific-instrument footer.
 * Source: DESIGN_SYSTEM.md §2.1 (footer section)
 *
 * License, GitHub link, citation link, contact.
 */

import { DATA_LICENSE, CODE_LICENSE, GITHUB_URL, CONTACT_EMAIL, SITE_NAME } from "../copy/framing";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="site-footer" role="contentinfo">
      <div className="site-footer__inner">
        <div className="site-footer__links">
          <a
            href="/data"
            className="site-footer__link"
            aria-label="Download raw data under CC BY 4.0"
          >
            Data ({DATA_LICENSE})
          </a>
          <a
            href={GITHUB_URL}
            className="site-footer__link"
            rel="noopener noreferrer"
            aria-label="View source code on GitHub (opens in same window)"
          >
            GitHub
          </a>
          <a
            href="#cite"
            className="site-footer__link"
            aria-label="Citation formats for this work"
          >
            Cite this
          </a>
          <a
            href="/methodology"
            className="site-footer__link"
            aria-label="Read the methodology page"
          >
            Methodology
          </a>
          <a
            href={`mailto:${CONTACT_EMAIL}`}
            className="site-footer__link"
            aria-label={`Contact ${SITE_NAME} by email`}
          >
            Contact
          </a>
        </div>

        <span className="site-footer__license">
          {SITE_NAME} {currentYear} · Data: {DATA_LICENSE} · Code: {CODE_LICENSE}
        </span>
      </div>
    </footer>
  );
}
