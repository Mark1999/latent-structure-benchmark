/**
 * LSB Dashboard — App shell.
 * Source: DESIGN_SYSTEM.md §2, §12.1 (reveal cascade), §12.2 (loading state), §12.5 (embed mode)
 *
 * Page state machine: loading → loaded | error
 * Loads manifest at mount via fetchManifest(). Default domain: "family".
 * When activeSlug changes, fetches the new domain JSON via fetchDomain().
 * Detects ?embed=true and suppresses chrome per §12.5.
 *
 * T9: explorer-internal state (selectedModels, activeVizTab, modelColors) moved
 * to DataExplorer.tsx. App.tsx passes only `domainResult` to DataExplorer.
 */

import { useEffect, useState } from "react";
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
import { DataExplorer } from "./components/DataExplorer";

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

/**
 * Read the initial domain slug from the URL (?domain= param) if present.
 * Falls back to "family" if absent or unreadable.
 * T10: permalink restore — App.tsx reads ?domain= to set the initial activeSlug.
 */
function readInitialDomainFromUrl(): string {
  try {
    const params = new URLSearchParams(window.location.search);
    const domain = params.get("domain");
    if (domain && domain.trim().length > 0) return domain.trim();
  } catch {
    // URLSearchParams unavailable — ignore.
  }
  return "family";
}

export default function App() {
  const [appState, setAppState] = useState<AppState>("loading");
  const [manifest, setManifest] = useState<Manifest | null>(null);
  // T10: initial domain reads from URL ?domain= param; falls back to "family".
  // The useState<string>("family") default is the canonical fallback used when
  // no URL param is present (per T5 binding and app-state test assertions).
  const [activeSlug, setActiveSlug] = useState<string>("family");
  const [domainResult, setDomainResult] = useState<DomainResultPublished | null>(null);
  const embedMode = isEmbedMode();

  // T10: read URL domain on mount and set activeSlug if a valid ?domain= param exists.
  // Runs once at mount — after this, DomainPicker onSelect drives the value.
  // set-state-in-effect: intentional — reading the URL once at mount to restore
  // a permalink-provided domain is exactly the use case the React docs describe.
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const urlDomain = readInitialDomainFromUrl();
    if (urlDomain !== "family") {
      setActiveSlug(urlDomain);
    }
  }, []);
  /* eslint-enable react-hooks/set-state-in-effect */

  // Derived loading flag: result is absent or for a different domain than activeSlug.
  // True while a domain fetch is in-flight or before first fetch completes.
  const domainLoading =
    appState === "loaded" &&
    (domainResult === null || domainResult.domain_slug !== activeSlug);

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
          // T9: selectedModels reset is now handled in DataExplorer.tsx via a
          // useEffect on domainResult.domain_slug. App.tsx no longer owns that state.
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

  // Embed mode: render only the DataExplorer per §12.5.
  // No Header, Footer, ArticleHeader, KeyFinding, MethodologySummary.
  if (embedMode) {
    return (
      <div className="embed-root">
        {appState === "loading" && (
          <p
            style={{
              color: "var(--color-text-muted)",
              fontSize: "var(--font-size-base)",
              padding: "var(--space-6)",
            }}
          >
            Loading...
          </p>
        )}
        {appState === "error" && (
          <p
            style={{
              color: "var(--color-text-secondary)",
              fontSize: "var(--font-size-base)",
              padding: "var(--space-6)",
            }}
          >
            Could not load data. Refresh the page or check your connection.
          </p>
        )}
        {appState === "loaded" && domainResult !== null && !domainLoading && (
          <DataExplorer domainResult={domainResult} isEmbed={true} />
        )}
        {appState === "loaded" && domainLoading && (
          <p
            style={{
              color: "var(--color-text-muted)",
              fontSize: "var(--font-size-base)",
              padding: "var(--space-6)",
            }}
          >
            Loading...
          </p>
        )}
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

              {/* DataExplorer: T9 — composes VizSwitcher + MDSPlot + ModelSelector + Legend.
                  Manages all explorer-internal state (selectedModels, activeVizTab,
                  modelColors). App.tsx passes only domainResult.
                  reveal-cascade-item within cascade bounds per F-T5-1 carry-forward.
                  §12.4 palette ownership lives in DataExplorer per UI/UX F-T6-2. */}
              {domainResult !== null && !domainLoading && (
                <div className="reveal-cascade-item">
                  <DataExplorer domainResult={domainResult} />
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
