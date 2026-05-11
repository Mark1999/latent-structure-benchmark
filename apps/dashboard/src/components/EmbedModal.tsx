/**
 * EmbedModal — embed snippet modal per DESIGN_SYSTEM.md §5 and §7.
 *
 * Shows an <iframe> embed snippet for the current domain + selected models.
 * The snippet includes ?embed=true so that App.tsx suppresses chrome per §12.5.
 * Copy button writes snippet to clipboard.
 *
 * Modal behavior (§7):
 *   - Renders via ReactDOM.createPortal at document.body.
 *   - Backdrop: rgba(0,0,0,0.5). Click backdrop → close.
 *   - Escape key → close.
 *   - Focus trap: Tab/Shift+Tab cycle only within modal.
 *   - Initial focus on first interactive element.
 *   - Focus returns to trigger button on close.
 *   - ARIA: role="dialog", aria-modal="true", aria-labelledby heading.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T12
 * Reference: DESIGN_SYSTEM.md §5, §7, §12.5
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { createPortal } from "react-dom";

// ── Props ─────────────────────────────────────────────────────────────────────

export interface EmbedModalProps {
  domain: string;
  selectedModels: string[];
  isOpen: boolean;
  onClose: () => void;
  /** Trigger element — focus returns here on close. */
  triggerRef?: React.RefObject<HTMLButtonElement | null>;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Get all focusable elements inside a container. */
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

/**
 * Build the embed <iframe> snippet.
 * The src encodes domain + models as URL params and adds embed=true.
 * Models are joined with comma (URL-encoded via encodeURIComponent of the value).
 */
function buildEmbedSnippet(domain: string, selectedModels: string[]): string {
  const baseUrl = "https://cogstructurelab.com";
  const params = new URLSearchParams();
  params.set("domain", domain);
  params.set("models", selectedModels.join(","));
  params.set("embed", "true");
  const src = `${baseUrl}/?${params.toString()}`;
  const domainTitle =
    domain.charAt(0).toUpperCase() + domain.slice(1);
  return [
    `<iframe`,
    `  src="${src}"`,
    `  width="900"`,
    `  height="700"`,
    `  frameborder="0"`,
    `  loading="lazy"`,
    `  title="LSB: ${domainTitle} domain MDS"`,
    `></iframe>`,
  ].join("\n");
}

// ── Styles ─────────────────────────────────────────────────────────────────────

const backdropStyle: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  backgroundColor: "rgba(0,0,0,0.5)",
  zIndex: 1000,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const dialogStyle: React.CSSProperties = {
  background: "var(--color-background)",
  borderRadius: "var(--border-radius-md)",
  boxShadow: "var(--shadow-lg)",
  padding: "var(--space-6)",
  maxWidth: "580px",
  width: "calc(100% - 2 * var(--space-6))",
  position: "relative",
  maxHeight: "90vh",
  overflowY: "auto",
};

const headingStyle: React.CSSProperties = {
  fontSize: "var(--font-size-xl)",
  fontWeight: "var(--font-weight-bold)",
  color: "var(--color-text-primary)",
  marginBottom: "var(--space-4)",
  marginRight: "var(--space-8)",
};

const closeBtnStyle: React.CSSProperties = {
  position: "absolute",
  top: "var(--space-4)",
  right: "var(--space-4)",
  background: "transparent",
  border: "none",
  cursor: "pointer",
  fontSize: "var(--font-size-lg)",
  lineHeight: 1,
  color: "var(--color-text-secondary)",
  padding: "var(--space-1)",
  borderRadius: "var(--border-radius-sm)",
};

const snippetStyle: React.CSSProperties = {
  fontFamily: "var(--font-mono)",
  fontSize: "var(--font-size-sm)",
  background: "var(--color-surface)",
  border: "1px solid var(--color-border)",
  borderRadius: "var(--border-radius-sm)",
  padding: "var(--space-4)",
  whiteSpace: "pre",
  overflowX: "auto",
  color: "var(--color-text-primary)",
  lineHeight: "var(--line-height-data)",
  marginBottom: "var(--space-3)",
  userSelect: "text",
};

const copyBtnStyle: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: "4px",
  padding: "var(--space-2) var(--space-4)",
  fontSize: "var(--font-size-sm)",
  fontFamily: "var(--font-body)",
  fontWeight: "var(--font-weight-medium)",
  color: "var(--color-text-primary)",
  background: "transparent",
  border: "1px solid var(--color-border)",
  borderRadius: "var(--border-radius-sm)",
  cursor: "pointer",
  lineHeight: 1.4,
  transition: "background-color 0.15s ease",
};

const noteStyle: React.CSSProperties = {
  marginTop: "var(--space-4)",
  fontSize: "var(--font-size-xs)",
  color: "var(--color-text-caption)",
  lineHeight: "var(--line-height-body)",
};

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * EmbedModal renders a WCAG-accessible dialog showing an <iframe> embed snippet.
 * Returns null when isOpen=false.
 */
export function EmbedModal({
  domain,
  selectedModels,
  isOpen,
  onClose,
  triggerRef,
}: EmbedModalProps) {
  const [copied, setCopied] = useState(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const headingId = "embed-modal-heading";

  const snippet = buildEmbedSnippet(domain, selectedModels);

  // Close on Escape key + focus trap.
  useEffect(() => {
    if (!isOpen) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
      if (e.key === "Tab" && dialogRef.current) {
        const focusable = getFocusableElements(dialogRef.current);
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
  }, [isOpen, onClose]);

  // Set initial focus to first focusable element when modal opens.
  useEffect(() => {
    if (!isOpen || !dialogRef.current) return;
    const focusable = getFocusableElements(dialogRef.current);
    if (focusable.length > 0) {
      const id = setTimeout(() => focusable[0].focus(), 10);
      return () => clearTimeout(id);
    }
  }, [isOpen]);

  // Return focus to trigger on close.
  const prevIsOpen = useRef(isOpen);
  useEffect(() => {
    if (prevIsOpen.current && !isOpen) {
      triggerRef?.current?.focus();
    }
    prevIsOpen.current = isOpen;
  }, [isOpen, triggerRef]);

  // Reset copied state when closed.
  // eslint-disable react-hooks/set-state-in-effect
  useEffect(() => {
    // Setting state in response to a prop change is the documented React pattern
    // for derived resets (https://react.dev/reference/react/useState#storing-information-from-previous-renders).
    /* eslint-disable react-hooks/set-state-in-effect */
    if (!isOpen) setCopied(false);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [isOpen]);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(snippet).then(
      () => {
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      },
      () => {
        // Clipboard unavailable — silently ignore.
      }
    );
  }, [snippet]);

  if (!isOpen) return null;

  return createPortal(
    <div
      className="embed-modal__backdrop"
      style={backdropStyle}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      data-testid="embed-modal-backdrop"
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={headingId}
        className="embed-modal__dialog"
        style={dialogStyle}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Heading */}
        <h2 id={headingId} style={headingStyle}>
          Embed this chart
        </h2>

        {/* Close button */}
        <button
          type="button"
          className="embed-modal__close-btn"
          aria-label="Close embed modal"
          onClick={onClose}
          style={closeBtnStyle}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor =
              "var(--color-surface-hover)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
          }}
        >
          ✕
        </button>

        {/* Snippet */}
        <pre
          className="embed-modal__snippet"
          style={snippetStyle}
          tabIndex={0}
          aria-label="Embed iframe code snippet"
        >
          <code>{snippet}</code>
        </pre>

        {/* Copy button */}
        <button
          type="button"
          className="embed-modal__copy-btn"
          aria-label={copied ? "Embed code copied" : "Copy embed code"}
          onClick={handleCopy}
          style={copyBtnStyle}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor =
              "var(--color-surface-hover)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "transparent";
          }}
        >
          {copied ? "✓ Copied!" : "Copy embed code"}
        </button>

        {/* Attribution note */}
        <p style={noteStyle}>
          Embed code permitted by CC-BY 4.0; please retain the LSB attribution.
        </p>
      </div>
    </div>,
    document.body
  );
}
