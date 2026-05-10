/**
 * DomainPicker — horizontal pill-button domain navigation.
 *
 * Renders available domains as active pills and unavailable domains as
 * greyed-out, discoverable-but-disabled pills per DESIGN_SYSTEM.md §2.3.
 *
 * Accessibility:
 *   - Container: role="tablist" (DESIGN_SYSTEM.md §7)
 *   - Each pill: role="tab" with aria-selected and aria-label
 *   - Disabled pills: aria-disabled="true", tabIndex="0" (focusable per §12.3
 *     binding — keyboard users must be able to discover all visible affordances)
 *   - Keyboard: ArrowLeft / ArrowRight between pills, Enter / Space to activate
 *   - Tooltip on disabled pills: "Coming in a future update" (per §12.3 — no
 *     internal phase numbering in user-visible copy)
 */

import { useRef, type KeyboardEvent } from "react";

export interface Domain {
  slug: string;
  label: string;
  available: boolean;
}

export interface DomainPickerProps {
  domains: Domain[];
  activeSlug: string;
  onSelect: (slug: string) => void;
}

/**
 * Build the per-pill aria-label per DESIGN_SYSTEM.md §7 + task spec.
 *
 * Three states:
 *   - Active available: "Domain: Family — currently displayed"
 *   - Inactive available: "Domain: Holidays — switch to view"
 *   - Disabled: "Domain: Food — coming in a future update"
 */
function pillAriaLabel(domain: Domain, isActive: boolean): string {
  if (!domain.available) {
    return `Domain: ${domain.label} — coming in a future update`;
  }
  if (isActive) {
    return `Domain: ${domain.label} — currently displayed`;
  }
  return `Domain: ${domain.label} — switch to view`;
}

export function DomainPicker({ domains, activeSlug, onSelect }: DomainPickerProps) {
  const listRef = useRef<HTMLDivElement>(null);

  /** Move focus to the adjacent focusable pill (wraps around). */
  function moveFocus(currentIndex: number, direction: 1 | -1): void {
    const buttons = listRef.current?.querySelectorAll<HTMLButtonElement>("button[role='tab']");
    if (!buttons || buttons.length === 0) return;
    const total = buttons.length;
    const nextIndex = (currentIndex + direction + total) % total;
    buttons[nextIndex].focus();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLButtonElement>, index: number, domain: Domain): void {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      moveFocus(index, 1);
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      moveFocus(index, -1);
    } else if ((e.key === "Enter" || e.key === " ") && domain.available) {
      e.preventDefault();
      onSelect(domain.slug);
    }
  }

  return (
    <div className="domain-picker">
      {/* Hairline divider above the picker — visual separation between
          ArticleHeader and the explorer per task spec */}
      <div className="domain-picker__divider" aria-hidden="true" />

      <div
        ref={listRef}
        className="domain-picker__list"
        role="tablist"
        aria-label="Domain selection"
      >
        {domains.map((domain, index) => {
          const isActive = domain.slug === activeSlug && domain.available;

          return (
            <button
              key={domain.slug}
              role="tab"
              className={[
                "domain-picker__pill",
                isActive ? "domain-picker__pill--active" : "",
                !domain.available ? "domain-picker__pill--disabled" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              aria-selected={isActive ? "true" : "false"}
              aria-disabled={!domain.available ? "true" : undefined}
              aria-label={pillAriaLabel(domain, isActive)}
              /* Disabled pills remain focusable per §12.3 binding.
                 tabIndex 0 on all pills so keyboard users can discover them. */
              tabIndex={0}
              title={!domain.available ? "Coming in a future update" : undefined}
              onClick={() => {
                if (domain.available) {
                  onSelect(domain.slug);
                }
              }}
              onKeyDown={(e) => handleKeyDown(e, index, domain)}
            >
              {domain.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
