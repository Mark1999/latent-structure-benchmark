/**
 * LSB Dashboard — App shell.
 * Source: DESIGN_SYSTEM.md §2, §12.1 (reveal cascade), §12.2 (loading state), §12.5 (embed mode)
 *
 * Page state machine: loading → loaded | error
 * Loads manifest at mount via fetchManifest(). Default domain: "family".
 * When activeSlug changes, fetches the new domain JSON via fetchDomain().
 * Detects ?embed=true and suppresses chrome per §12.5.
 */

import { useEffect, useState, useMemo } from "react";
import "./styles/tokens.css";
import "./styles/app.css";

import { fetchManifest, fetchDomain } from "./api/client";
import type { Manifest, DomainResultPublished } from "./data/types";

import { Header } from "./components/Header";
import { ArticleHeader } from "./components/ArticleHeader";
import { Footer } from "./components/Footer";
import { DomainPicker } from "./components/DomainPicker";
import type { Domain } from "./components/DomainPicker";
import { KeyFinding } from "./components/KeyFinding";
import { MDSPlot } from "./components/MDSPlot";
import { ModelSelector } from "./components/ModelSelector";

type AppState = "loading" | "loaded" | "error";

/**
 * Detect embed mode: ?embed=true suppresses page chrome.
 * Source: DESIGN_SYSTEM.md §12.5
 */
function isEmbedMode(): boolean {
  try {
    return new URLSearchParams(window.location.search).get("embed") === "true";
  } catch {
    return false;
  }
}

/**
 * Convert a slug to title case for display labels.
 * e.g. "family" → "Family", "holidays" → "Holidays"
 */
function toTitleCase(slug: string): string {
  return slug.charAt(0).toUpperCase() + slug.slice(1);
}

/**
 * Phase-6 domains that are not yet in the manifest.
 * These render as disabled pills with "coming in a future update" affordance.
 * Per §12.3 binding: disabled pills are focusable, no internal phase numbering.
 * Per task spec §2.3: at least Food, Emotion, Justice are the known future domains.
 */
const FUTURE_DOMAINS: Domain[] = [
  { slug: "food", label: "Food", available: false },
  { slug: "emotion", label: "Emotion", available: false },
  { slug: "justice", label: "Justice", available: false },
];

/**
 * Model palette slot hex values, matching tokens.css §1.2 (v0.4.1).
 * Defined at module level for stable reference in the modelColors useMemo.
 * Assignment algorithm: §12.4 — sort model_ids ascending, assign slot 1…11.
 */
const MODEL_PALETTE_SLOTS: string[] = [
  "#3360a9", // --color-model-1
  "#c0392b", // --color-model-2
  "#e67e22", // --color-model-3
  "#27ae60", // --color-model-4
  "#8e44ad", // --color-model-5
  "#16a085", // --color-model-6
  "#d35400", // --color-model-7
  "#1a5276", // --color-model-8
  "#7d3c98", // --color-model-9
  "#148f77", // --color-model-10
  "#9a7d0a", // --color-model-11 (v0.4.1 corrected from #b7950b)
];

/**
 * Build the domains list for DomainPicker from the manifest + future domains.
 * Available domains come from the manifest; future domains are appended as disabled.
 * Deduplicates: if a future domain slug appears in the manifest, it becomes available.
 */
function buildDomainList(manifest: Manifest): Domain[] {
  const manifestSlugs = new Set(manifest.domains.map((d) => d.slug));
  const available: Domain[] = manifest.domains.map((d) => ({
    slug: d.slug,
    label: toTitleCase(d.slug),
    available: true,
  }));
  const future: Domain[] = FUTURE_DOMAINS.filter(
    (fd) => !manifestSlugs.has(fd.slug)
  );
  return [...available, ...future];
}

export default function App() {
  const [appState, setAppState] = useState<AppState>("loading");
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [activeSlug, setActiveSlug] = useState<string>("family");
  const [domainResult, setDomainResult] = useState<DomainResultPublished | null>(null);
  /** T7: selected model_ids. Default to all available; reset on domain switch. */
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const embedMode = isEmbedMode();

  // Derived loading flag: result is absent or for a different domain than activeSlug.
  // True while a domain fetch is in-flight or before first fetch completes.
  const domainLoading =
    appState === "loaded" &&
    (domainResult === null || domainResult.domain_slug !== activeSlug);

  /**
   * Build modelColors per §12.4 algorithm:
   * Sort all model_ids ascending (lexicographic), assign palette slot 1…11.
   * Assignment is stable: same model_id always gets the same slot.
   * Ownership moves to DataExplorer.tsx at T9.
   */
  const modelColors = useMemo((): Record<string, string> => {
    if (!domainResult) return {};
    const sortedIds = [...Object.keys(domainResult.mds_coordinates)].sort();
    const colors: Record<string, string> = {};
    sortedIds.forEach((id, i) => {
      colors[id] = MODEL_PALETTE_SLOTS[i % MODEL_PALETTE_SLOTS.length];
    });
    return colors;
  }, [domainResult]);

  // Load manifest at mount.
  useEffect(() => {
    let cancelled = false;

    fetchManifest()
      .then((m) => {
        if (!cancelled) {
          setManifest(m);
          setAppState("loaded");
          // Default to first available domain if "family" not in manifest.
          if (m.domains.length > 0 && !m.domains.find((d) => d.slug === "family")) {
            setActiveSlug(m.domains[0].slug);
          }
        }
      })
      .catch(() => {
        if (!cancelled) {
          setAppState("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Fetch the active domain's JSON whenever manifest is loaded or activeSlug changes.
  useEffect(() => {
    if (appState !== "loaded") return;

    let cancelled = false;

    fetchDomain(activeSlug)
      .then((result) => {
        if (!cancelled) {
          setDomainResult(result);
          // T7 v0.4.2 (UI/UX F-T7-1 fix): initial selection is the first 6 model_ids by
          // §12.4 lexicographic sort order. Defaulting to all-available caused the max-6
          // warning to appear on every page load before any user interaction, which
          // contradicts §3.7's "interactive guard" intent. See DESIGN_SYSTEM.md §3.7
          // initial-state binding spec (v0.4.2) for the three rules.
          const rawCoords = result.mds_coordinates as unknown as Record<string, [number, number]>;
          setSelectedModels(Object.keys(rawCoords).sort().slice(0, 6));
        }
      })
      .catch(() => {
        // Domain fetch failure is non-fatal: keep nav functional.
        // domainLoading derived flag stays true but KeyFinding simply won't render.
      });

    return () => {
      cancelled = true;
    };
  }, [appState, activeSlug]);

  // Embed mode: render only the data explorer (T6+ will wire this up).
  // Per §12.5: no Header, Footer, ArticleHeader, KeyFinding, MethodologySummary.
  if (embedMode) {
    return (
      <div className="embed-root">
        {/* DataExplorer renders here in T6+ */}
        <p
          style={{
            color: "var(--color-text-muted)",
            fontSize: "var(--font-size-base)",
            padding: "var(--space-6)",
          }}
        >
          {appState === "loading"
            ? "Loading..."
            : appState === "error"
            ? "Could not load data. Refresh the page or check your connection."
            : "Data explorer initializing…"}
        </p>
      </div>
    );
  }

  // Full-page mode: Header + content area + Footer.
  // Content area state machine: loading → loaded | error
  // Per DESIGN_SYSTEM.md §12.2: no spinner, no shimmer.
  const domains: Domain[] = manifest !== null ? buildDomainList(manifest) : [];

  return (
    <div className="page-wrapper">
      {/* Reveal cascade — §12.1: 600ms total, 80ms stagger, ease-out, fires once */}
      <div className="reveal-cascade-item">
        <Header />
      </div>

      <main className="page-main">
        <div className="reveal-cascade-item">
          <ArticleHeader loading={appState === "loading"} />
        </div>

        {/* DomainPicker: shown once manifest is loaded, in the reveal cascade */}
        {appState === "loaded" && domains.length > 0 && (
          <div className="reveal-cascade-item">
            <DomainPicker
              domains={domains}
              activeSlug={activeSlug}
              onSelect={setActiveSlug}
            />
          </div>
        )}

        <div className="reveal-cascade-item">
          {appState === "loading" && (
            <div
              className="content-placeholder content-placeholder--loading"
              role="status"
              aria-live="polite"
              aria-label="Loading domain data"
            >
              {/* Per §12.2: "Loading..." in --color-text-muted at --font-size-base */}
              Loading...
            </div>
          )}

          {appState === "error" && (
            <div
              className="content-placeholder content-placeholder--error"
              role="alert"
              aria-live="assertive"
            >
              {/* Per §12.2: error text in --color-text-secondary */}
              Could not load data. Refresh the page or check your connection.
            </div>
          )}

          {appState === "loaded" && (
            <div className="content-area">
              {/* KeyFinding: shown when domain result is loaded */}
              {domainResult !== null && !domainLoading && (
                <div className="reveal-cascade-item">
                  <KeyFinding generatedLede={domainResult.generated_lede} />
                </div>
              )}

              {/* MDSPlot + ModelSelector: shown when domain result is loaded (T6/T7).
                  reveal-cascade-item :nth-child(2) — within bounds per F-T5-1 carry-forward.
                  §12.4: modelColors built from sorted model_ids above.
                  T7: two-column layout (mds + selector) on wide viewports, single on narrow. */}
              {domainResult !== null && !domainLoading && (
                <div className="reveal-cascade-item">
                  <div className="explorer-layout">
                    <div className="explorer-layout__viz">
                      <MDSPlot
                        domainResult={domainResult}
                        modelColors={modelColors}
                        selectedModels={selectedModels}
                      />
                    </div>
                    <div className="explorer-layout__selector">
                      <ModelSelector
                        domainResult={domainResult}
                        selectedModels={selectedModels}
                        onSelectionChange={setSelectedModels}
                        modelColors={modelColors}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Domain data loading state (per-domain fetch in progress) */}
              {domainLoading && (
                <div
                  className="content-placeholder content-placeholder--loading"
                  role="status"
                  aria-live="polite"
                  aria-label="Loading domain data"
                >
                  Loading...
                </div>
              )}

              {/* DataExplorer renders here in T9+ */}
            </div>
          )}
        </div>
      </main>

      <div className="reveal-cascade-item">
        <Footer />
      </div>
    </div>
  );
}
