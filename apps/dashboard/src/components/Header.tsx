/**
 * Site Header — OWID-style navigation.
 * Source: DESIGN_SYSTEM.md §2.2
 *
 * Logo left, four navigation links right.
 * No hamburger menu on desktop.
 */

import { SITE_NAME } from "../copy/framing";

/** Minimal scientific-instrument logo glyph: a circle with cross-axis ticks and an inner solid circle. */
function LogoGlyph() {
  return (
    <svg
      className="site-header__logo-glyph"
      viewBox="0 0 28 28"
      aria-hidden="true"
      focusable="false"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer ring */}
      <circle
        cx="14"
        cy="14"
        r="12"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      {/* Cross-axis tick marks */}
      <line x1="14" y1="2" x2="14" y2="5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="14" y1="23" x2="14" y2="26" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="2" y1="14" x2="5" y2="14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="23" y1="14" x2="26" y2="14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      {/* Inner solid circle */}
      <circle cx="14" cy="14" r="3.5" fill="currentColor" />
    </svg>
  );
}

interface NavLink {
  href: string;
  label: string;
}

const NAV_LINKS: NavLink[] = [
  { href: "/", label: "Explore" },
  { href: "/methodology", label: "Methodology" },
  { href: "/data", label: "Data" },
  { href: "/about", label: "About" },
];

export function Header() {
  return (
    <header className="site-header" role="banner">
      <div className="site-header__inner">
        <a href="/" className="site-header__logo" aria-label={`${SITE_NAME} — Home`}>
          <LogoGlyph />
          <span>{SITE_NAME}</span>
        </a>

        <nav className="site-header__nav" aria-label="Site navigation">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="site-header__nav-link"
            >
              {link.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
