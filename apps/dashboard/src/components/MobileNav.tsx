// DESIGN_SYSTEM.md §8.1 — mobile hamburger nav panel (full-screen overlay, dialog pattern, focus trap).

import { useEffect, useRef, type RefObject } from "react";
import type { NavLink } from "./Header";
import {
  MOBILE_NAV_TRIGGER_LABEL_OPEN,
  MOBILE_NAV_PANEL_LABEL,
} from "../copy/mobile_nav";
import "../styles/mobile-nav.css";

function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const selector = [
    "button:not([disabled])",
    "[href]",
    "input:not([disabled])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    '[tabindex]:not([tabindex="-1"])',
  ].join(",");
  return Array.from(container.querySelectorAll<HTMLElement>(selector)).filter(
    (el) => !el.closest("[aria-hidden]")
  );
}

export interface MobileNavProps {
  id: string;
  links: NavLink[];
  onClose: () => void;
  triggerRef: RefObject<HTMLButtonElement | null>;
}

export function MobileNav({ id, links, onClose }: MobileNavProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const btn = closeBtnRef.current;
    if (btn) {
      btn.focus();
    }
  }, []);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      if (e.key === "Tab" && panelRef.current) {
        const focusable = getFocusableElements(panelRef.current);
        if (focusable.length === 0) {
          e.preventDefault();
          return;
        }
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div
      ref={panelRef}
      role="dialog"
      aria-modal="true"
      aria-label={MOBILE_NAV_PANEL_LABEL}
      id={id}
      className="mobile-nav__panel"
    >
      <button
        ref={closeBtnRef}
        className="mobile-nav__close"
        aria-label={MOBILE_NAV_TRIGGER_LABEL_OPEN}
        onClick={onClose}
        type="button"
      >
        <span aria-hidden="true">{"×"}</span>
      </button>
      <nav className="mobile-nav__links" aria-label={MOBILE_NAV_PANEL_LABEL}>
        {links.map((link) => (
          <a key={link.href} href={link.href} className="mobile-nav__link">
            {link.label}
          </a>
        ))}
      </nav>
    </div>
  );
}
