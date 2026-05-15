// DESIGN_SYSTEM.md §8.2 — mobile bottom-drawer overlay for ModelSelector (dialog pattern, focus trap, scroll lock).

import { useEffect, useRef, type ReactNode } from "react";
import {
  MOBILE_MODEL_DRAWER_PANEL_LABEL,
  MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN,
} from "../copy/mobile_model_drawer";
import "../styles/mobile-model-drawer.css";

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

export interface MobileModelSelectorDrawerProps {
  id: string;
  onClose: () => void;
  children: ReactNode;
}

export function MobileModelSelectorDrawer({
  id,
  onClose,
  children,
}: MobileModelSelectorDrawerProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const btn = closeBtnRef.current;
    if (btn) {
      btn.focus();
    }
  }, []);

  useEffect(() => {
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prevOverflow;
    };
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
    <>
      <div
        className="mobile-model-drawer__scrim"
        aria-hidden="true"
        onPointerDown={onClose}
      />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label={MOBILE_MODEL_DRAWER_PANEL_LABEL}
        id={id}
        className="mobile-model-drawer__panel mobile-model-drawer__panel--open"
        onPointerDown={(e) => e.stopPropagation()}
      >
        <div className="mobile-model-drawer__header">
          <button
            ref={closeBtnRef}
            className="mobile-model-drawer__close"
            aria-label={MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN}
            onClick={onClose}
            type="button"
          >
            <span aria-hidden="true">{"×"}</span>
          </button>
        </div>
        <div className="mobile-model-drawer__body">{children}</div>
      </div>
    </>
  );
}
