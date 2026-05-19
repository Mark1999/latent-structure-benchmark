/**
 * Site Header — OWID-style navigation.
 * Source: DESIGN_SYSTEM.md §2.2, §8.1 (T11 mobile hamburger nav)
 *
 * Logo left, four navigation links right on desktop.
 * At <768px: desktop nav hidden; hamburger trigger shown; MobileNav panel on open.
 */

import { useState, useRef, useEffect } from "react";
import { SITE_NAME } from "../copy/framing";
import {
  MOBILE_NAV_TRIGGER_LABEL_CLOSED,
  MOBILE_NAV_TRIGGER_LABEL_OPEN,
} from "../copy/mobile_nav";
import { MobileNav } from "./MobileNav";

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

/** Three horizontal lines per DESIGN_SYSTEM.md §8.1.2. */
function HamburgerGlyph() {
  return (
    <svg
      viewBox="0 0 20 16"
      width="20"
      height="16"
      aria-hidden="true"
      focusable="false"
      xmlns="http://www.w3.org/2000/svg"
    >
      <line x1="0" y1="2"  x2="20" y2="2"  stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <line x1="0" y1="8"  x2="20" y2="8"  stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <line x1="0" y1="14" x2="20" y2="14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export interface NavLink {
  href: string;
  label: string;
}

export const NAV_LINKS: NavLink[] = [
  { href: "/", label: "Explore" },
  { href: "/methodology", label: "Methodology" },
  { href: "/data", label: "Data" },
  { href: "/about", label: "About" },
];

export function Header() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const prevMobileNavOpen = useRef(mobileNavOpen);

  useEffect(() => {
    if (prevMobileNavOpen.current && !mobileNavOpen) {
      triggerRef.current?.focus();
    }
    prevMobileNavOpen.current = mobileNavOpen;
  }, [mobileNavOpen]);

  return (
    <header className="site-header" role="banner">
      <div className="site-header__inner">
        <a href="/" className="site-header__logo" aria-label={`${SITE_NAME} — Home`}>
          <LogoGlyph />
          <span>{SITE_NAME}</span>
        </a>

        <nav className="site-header__nav" aria-label="Site navigation">
          {NAV_LINKS.map((link) => {
            const isActive =
              typeof window !== "undefined" &&
              window.location.pathname === link.href;
            return (
              <a
                key={link.href}
                href={link.href}
                className="site-header__nav-link"
                aria-current={isActive ? "page" : undefined}
              >
                {link.label}
              </a>
            );
          })}
        </nav>

        <button
          ref={triggerRef}
          type="button"
          className="site-header__hamburger"
          aria-label={mobileNavOpen ? MOBILE_NAV_TRIGGER_LABEL_OPEN : MOBILE_NAV_TRIGGER_LABEL_CLOSED}
          aria-expanded={mobileNavOpen}
          aria-controls="mobile-nav-panel"
          aria-haspopup="dialog"
          style={{ display: mobileNavOpen ? "none" : undefined }}
          onClick={() => setMobileNavOpen(true)}
        >
          <HamburgerGlyph />
        </button>
      </div>

      {mobileNavOpen && (
        <MobileNav
          id="mobile-nav-panel"
          links={NAV_LINKS}
          onClose={() => setMobileNavOpen(false)}
          triggerRef={triggerRef}
        />
      )}
    </header>
  );
}
