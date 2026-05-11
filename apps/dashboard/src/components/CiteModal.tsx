/**
 * CiteModal — citation formats modal per DESIGN_SYSTEM.md §5 and §7.
 *
 * Four tabs: APA / MLA / Chicago / BibTeX.
 * Each tab has a "Copy" button that writes to navigator.clipboard.writeText.
 * "Copied!" feedback for ~1.5s on success.
 *
 * Modal behavior (§7):
 *   - Renders via ReactDOM.createPortal at document.body.
 *   - Backdrop: rgba(0,0,0,0.5). Click backdrop → close.
 *   - Escape key → close.
 *   - Focus trap: Tab/Shift+Tab cycle only within modal.
 *   - Initial focus on active tab button.
 *   - Focus returns to trigger button on close.
 *   - ARIA: role="dialog", aria-modal="true", aria-labelledby heading.
 *   - Tabs: role="tablist" / role="tab" / role="tabpanel".
 *
 * Citation strings are pure functions from citation.ts (§1.6 naming binding).
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T12
 * Reference: ARCHITECTURE.md §1.6, DESIGN_SYSTEM.md §5, §7
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { createPortal } from "react-dom";
import type { DomainResultPublished } from "../data/types";
import {
  buildApa,
  buildMla,
  buildChicago,
  buildBibtex,
} from "../lib/citation";
import type { CitationContext } from "../lib/citation";

// ── Props ─────────────────────────────────────────────────────────────────────

export interface CiteModalProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
  isOpen: boolean;
  onClose: () => void;
  /** Trigger element — focus returns here on close. */
  triggerRef?: React.RefObject<HTMLButtonElement | null>;
}

// ── Tab config ─────────────────────────────────────────────────────────────────

type TabId = "apa" | "mla" | "chicago" | "bibtex";

const TABS: { id: TabId; label: string }[] = [
  { id: "apa",     label: "APA"     },
  { id: "mla",     label: "MLA"     },
  { id: "chicago", label: "Chicago" },
  { id: "bibtex",  label: "BibTeX"  },
];

// ── Helpers ───────────────────────────────────────────────────────────────────

function toTitleCase(slug: string): string {
  return slug.charAt(0).toUpperCase() + slug.slice(1);
}

function buildCtx(
  domainResult: DomainResultPublished,
  selectedModels: string[]
): CitationContext {
  return {
    domain: domainResult.domain_slug,
    domainTitle: toTitleCase(domainResult.domain_slug),
    analysisVersion: domainResult.analysis_version,
    generatedAt: domainResult.generated_at,
    selectedModels,
  };
}

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
  maxWidth: "560px",
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

const tabListStyle: React.CSSProperties = {
  display: "flex",
  gap: "0",
  borderBottom: "2px solid var(--color-border)",
  marginBottom: "var(--space-4)",
};

function tabBtnStyle(active: boolean): React.CSSProperties {
  return {
    padding: "var(--space-2) var(--space-4)",
    background: "transparent",
    border: "none",
    borderBottom: active ? "2px solid var(--color-info)" : "2px solid transparent",
    marginBottom: "-2px",
    cursor: "pointer",
    fontFamily: "var(--font-body)",
    fontSize: "var(--font-size-sm)",
    fontWeight: active ? "var(--font-weight-bold)" : "var(--font-weight-regular)",
    color: active ? "var(--color-info)" : "var(--color-text-secondary)",
    transition: "color 0.15s ease",
  };
}

const panelStyle: React.CSSProperties = {
  fontFamily: "var(--font-mono)",
  fontSize: "var(--font-size-sm)",
  background: "var(--color-surface)",
  border: "1px solid var(--color-border)",
  borderRadius: "var(--border-radius-sm)",
  padding: "var(--space-4)",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
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

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * CiteModal renders a WCAG-accessible dialog with four citation format tabs.
 * Returns null when isOpen=false.
 */
export function CiteModal({
  domainResult,
  selectedModels,
  isOpen,
  onClose,
  triggerRef,
}: CiteModalProps) {
  const [activeTab, setActiveTab] = useState<TabId>("apa");
  const [copied, setCopied] = useState(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const headingId = "cite-modal-heading";

  // Build citation strings for active tab.
  const ctx = buildCtx(domainResult, selectedModels);
  const citations: Record<TabId, string> = {
    apa:     buildApa(ctx),
    mla:     buildMla(ctx),
    chicago: buildChicago(ctx),
    bibtex:  buildBibtex(ctx),
  };
  const currentCitation = citations[activeTab];

  // Close on Escape key.
  useEffect(() => {
    if (!isOpen) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
      // Focus trap: Tab / Shift+Tab cycles within dialog.
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
      // Arrow key tab navigation (APA ← → MLA ← → Chicago ← → BibTeX ← → APA).
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        const idx = TABS.findIndex((t) => t.id === activeTab);
        if (idx !== -1) {
          const next =
            e.key === "ArrowRight"
              ? (idx + 1) % TABS.length
              : (idx - 1 + TABS.length) % TABS.length;
          setActiveTab(TABS[next].id);
        }
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, activeTab]);

  // Set initial focus to first tab button when modal opens.
  useEffect(() => {
    if (!isOpen || !dialogRef.current) return;
    const focusable = getFocusableElements(dialogRef.current);
    if (focusable.length > 0) {
      // Small timeout to let the DOM settle after portal mount.
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

  // Reset copied state and tab when closed.
  // Setting state in response to a prop change is the documented React pattern
  // for derived resets (https://react.dev/reference/react/useState#storing-information-from-previous-renders).
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (!isOpen) {
      setCopied(false);
      setActiveTab("apa");
    }
  }, [isOpen]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(currentCitation).then(
      () => {
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      },
      () => {
        // Clipboard unavailable — silently ignore.
      }
    );
  }, [currentCitation]);

  if (!isOpen) return null;

  return createPortal(
    <div
      className="cite-modal__backdrop"
      style={backdropStyle}
      onClick={(e) => {
        // Close when clicking on the backdrop, not the dialog.
        if (e.target === e.currentTarget) onClose();
      }}
      data-testid="cite-modal-backdrop"
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={headingId}
        className="cite-modal__dialog"
        style={dialogStyle}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Heading */}
        <h2 id={headingId} style={headingStyle}>
          Cite this data
        </h2>

        {/* Close button */}
        <button
          type="button"
          className="cite-modal__close-btn"
          aria-label="Close citation modal"
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

        {/* Tab list */}
        <div
          role="tablist"
          aria-label="Citation formats"
          style={tabListStyle}
        >
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`cite-tab-${tab.id}`}
              aria-selected={activeTab === tab.id}
              aria-controls={`cite-panel-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              style={tabBtnStyle(activeTab === tab.id)}
              onMouseEnter={(e) => {
                if (activeTab !== tab.id) {
                  (e.currentTarget as HTMLButtonElement).style.color =
                    "var(--color-text-primary)";
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== tab.id) {
                  (e.currentTarget as HTMLButtonElement).style.color =
                    "var(--color-text-secondary)";
                }
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab panels — render one per format; hide non-active with aria-hidden */}
        {TABS.map((tab) => (
          <div
            key={tab.id}
            id={`cite-panel-${tab.id}`}
            role="tabpanel"
            aria-labelledby={`cite-tab-${tab.id}`}
            hidden={activeTab !== tab.id}
          >
            <pre style={panelStyle}>{citations[tab.id]}</pre>
            <button
              type="button"
              className="cite-modal__copy-btn"
              aria-label={`Copy ${tab.label} citation`}
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
              {copied ? "✓ Copied!" : "Copy"}
            </button>
          </div>
        ))}
      </div>
    </div>,
    document.body
  );
}
