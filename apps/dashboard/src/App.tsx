/**
 * LSB Dashboard — App shell.
 *
 * Phase 9a layout restructure: full-viewport app shell with 260px sidebar +
 * content grid, replacing the article-scroll layout on the Explore page.
 *
 * Source: DESIGN_SYSTEM.md §2, §12.1 (reveal cascade), §12.2 (loading state),
 *         §12.5 (embed mode), docs/slicer-prototype.html (layout reference)
 *
 * Page state machine: loading → loaded | error
 * Loads manifest at mount via fetchManifest(). Default domain: "family".
 * When activeSlug changes, fetches the new domain JSON via fetchDomain().
 * Detects ?embed=true and suppresses chrome per §12.5.
 *
 * App-shell layout (Explore page):
 *   - 48px top nav bar (brand + nav tabs)
 *   - 260px left sidebar (domain dropdown + ProviderModelTree)
 *   - 1fr content area (VizSwitcher + selection bar + DataExplorer)
 *   - No page scrolling (height: 100vh, overflow: hidden)
 *
 * App.tsx owns selectedModels and activeVizTab in app-shell mode so the
 * sidebar (ProviderModelTree) and content (DataExplorer) can share state.
 * These are passed as controlled props to DataExplorer.
 */

import { useEffect, useState, useMemo } from "react";
import "./styles/tokens.css";
import "./styles/app.css";
import "./styles/app-layout.css";

import { fetchManifest, fetchDomain } from "./api/client";
import type { Manifest, DomainResultPublished } from "./data/types";

import type { Domain } from "./components/DomainPicker";
import { DataExplorer } from "./components/DataExplorer";
import { ProviderModelTree } from "./components/ProviderModelTree";
import { MethodologyPagePlaceholder } from "./components/MethodologyPagePlaceholder";
import { InspectRoot } from "./components/InspectRoot";
import type { ActiveVizTab } from "./components/VizSwitcher";
import { resolveFragmentOnMount } from "./components/VizSwitcher";
import { encodePermalink, decodePermalink } from "./lib/permalink";
import "./styles/inspect.css";

// ── Model palette (§12.4) ────────────────────────────────────────────────────

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
  "#9a7d0a", // --color-model-11
];

// ── Mode detection helpers ────────────────────────────────────────────────────

function isEmbedMode(): boolean {
  try {
    return new URLSearchParams(window.location.search).get("embed") === "true";
  } catch {
    return false;
  }
}

function isMethodologyPage(): boolean {
  try {
    return typeof window !== "undefined" && window.location.pathname === "/methodology";
  } catch {
    return false;
  }
}

function isInspectMode(): string | null {
  try {
    const slug = new URLSearchParams(window.location.search).get("inspect");
    if (slug === null || slug.trim() === "") return null;
    return slug.trim();
  } catch {
    return null;
  }
}

// ── Domain helpers ────────────────────────────────────────────────────────────

function toTitleCase(slug: string): string {
  return slug.charAt(0).toUpperCase() + slug.slice(1);
}

const FUTURE_DOMAINS: Domain[] = [
  { slug: "food", label: "Food", available: false },
  { slug: "emotion", label: "Emotion", available: false },
  { slug: "justice", label: "Justice", available: false },
];

function buildDomainList(manifest: Manifest): Domain[] {
  const manifestSlugs = new Set(manifest.domains.map((d) => d.slug));
  const available: Domain[] = manifest.domains.map((d) => ({
    slug: d.slug,
    label: toTitleCase(d.slug),
    available: true,
  }));
  const future: Domain[] = FUTURE_DOMAINS.filter((fd) => !manifestSlugs.has(fd.slug));
  return [...available, ...future];
}

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

// ── URL state helpers ─────────────────────────────────────────────────────────

function readSelectedModelsFromUrl(
  currentDomain: string,
  availableModelIds: Set<string>
): string[] | null {
  try {
    const searchAndHash = window.location.search + window.location.hash;
    const state = decodePermalink(searchAndHash);
    if (state === null) return null;
    if (state.domain !== currentDomain) return null;
    const valid = state.models.filter((id) => availableModelIds.has(id));
    if (valid.length === 0) return null;
    return valid;
  } catch {
    return null;
  }
}

function writePermalinkState(
  domain: string,
  models: string[],
  vizTab: ActiveVizTab
): void {
  try {
    const encoded = encodePermalink({ domain, models, vizTab });
    window.history.replaceState(null, "", encoded);
  } catch {
    // history API unavailable in some test environments — ignore.
  }
}

// ── App state type ────────────────────────────────────────────────────────────

type AppState = "loading" | "loaded" | "error";

// ── Component ─────────────────────────────────────────────────────────────────

export default function App() {
  const [appState, setAppState] = useState<AppState>("loading");
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [activeSlug, setActiveSlug] = useState<string>("family");
  const [domainResult, setDomainResult] = useState<DomainResultPublished | null>(null);

  // App-shell mode state: selected models and active viz tab.
  // These are lifted here so the sidebar and content area share them.
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [activeVizTab, setActiveVizTab] = useState<ActiveVizTab>(
    () => resolveFragmentOnMount()
  );
  const [openWeightsOnly, setOpenWeightsOnly] = useState(false);

  const embedMode = isEmbedMode();
  const inspectSlug = isInspectMode();
  const methodologyPage = isMethodologyPage();

  // Read URL domain on mount.
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    const urlDomain = readInitialDomainFromUrl();
    if (urlDomain !== "family") {
      setActiveSlug(urlDomain);
    }
  }, []);
  /* eslint-enable react-hooks/set-state-in-effect */

  // Derived loading flag
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
          if (m.domains.length > 0 && !m.domains.find((d) => d.slug === "family")) {
            setActiveSlug(m.domains[0].slug);
          }
        }
      })
      .catch(() => {
        if (!cancelled) setAppState("error");
      });
    return () => { cancelled = true; };
  }, []);

  // Fetch domain JSON whenever manifest is loaded or activeSlug changes.
  useEffect(() => {
    if (appState !== "loaded") return;
    let cancelled = false;
    fetchDomain(activeSlug)
      .then((result) => {
        if (!cancelled) {
          setDomainResult(result);
        }
      })
      .catch(() => {
        // Non-fatal domain fetch failure.
      });
    return () => { cancelled = true; };
  }, [appState, activeSlug]);

  // Reset selectedModels to all-available when domain changes (app-shell mode: no max-6 limit).
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (domainResult === null) return;
    const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
    const sortedIds = Object.keys(rawCoords).sort();
    const availableSet = new Set(sortedIds);
    // Attempt permalink restore on domain change.
    const fromUrl = readSelectedModelsFromUrl(domainResult.domain_slug, availableSet);
    if (fromUrl !== null) {
      setSelectedModels(fromUrl);
      return;
    }
    // App-shell default: all models selected (no MAX_SELECTED limit).
    setSelectedModels(sortedIds);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainResult?.domain_slug]);
  /* eslint-enable react-hooks/set-state-in-effect */

  // Sync URL whenever selectedModels or activeVizTab changes.
  useEffect(() => {
    if (!domainResult) return;
    writePermalinkState(domainResult.domain_slug, selectedModels, activeVizTab);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainResult?.domain_slug, selectedModels, activeVizTab]);

  // Build modelColors (§12.4 algorithm) — needed for selection chips.
  const modelColors = useMemo((): Record<string, string> => {
    if (!domainResult) return {};
    const rawCoords = domainResult.mds_coordinates as unknown as Record<string, [number, number]>;
    const sortedIds = [...Object.keys(rawCoords)].sort();
    const colors: Record<string, string> = {};
    sortedIds.forEach((id, i) => {
      colors[id] = MODEL_PALETTE_SLOTS[i % MODEL_PALETTE_SLOTS.length];
    });
    return colors;
  }, [domainResult]);

  const domains: Domain[] = manifest !== null ? buildDomainList(manifest) : [];

  // ── Special page modes ─────────────────────────────────────────────────────

  if (methodologyPage) {
    return <MethodologyPagePlaceholder />;
  }

  if (inspectSlug !== null) {
    return <InspectRoot mode={inspectSlug} manifest={manifest} />;
  }

  // Embed mode: keep the existing article-style render.
  if (embedMode) {
    return (
      <div className="embed-root">
        {appState === "loading" && (
          <p style={{ color: "var(--color-text-muted)", fontSize: "var(--font-size-base)", padding: "var(--space-6)" }}>
            Loading...
          </p>
        )}
        {appState === "error" && (
          <p style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-base)", padding: "var(--space-6)" }}>
            Could not load data. Refresh the page or check your connection.
          </p>
        )}
        {appState === "loaded" && domainResult !== null && !domainLoading && (
          <DataExplorer domainResult={domainResult} isEmbed={true} />
        )}
        {appState === "loaded" && domainLoading && (
          <p style={{ color: "var(--color-text-muted)", fontSize: "var(--font-size-base)", padding: "var(--space-6)" }}>
            Loading...
          </p>
        )}
      </div>
    );
  }

  // ── App-shell layout (Explore page) ───────────────────────────────────────

  // Determine the current page for nav tab active state.
  const currentPath = typeof window !== "undefined" ? window.location.pathname : "/";

  return (
    <div className="app-shell">
      {/* 48px top nav bar */}
      <nav className="app-nav" aria-label="Site navigation">
        <a href="/" className="app-nav__brand" aria-label="Cognitive Structure Lab — Home">
          Cognitive Structure Lab <span className="app-nav__brand-sub">/ LSB</span>
        </a>
        <div className="app-nav__right" role="list">
          <a
            href="/"
            className={`app-nav__tab${currentPath === "/" ? " app-nav__tab--active" : ""}`}
            aria-current={currentPath === "/" ? "page" : undefined}
            role="listitem"
          >
            Explore
          </a>
          <a
            href="/methodology"
            className={`app-nav__tab${currentPath === "/methodology" ? " app-nav__tab--active" : ""}`}
            aria-current={currentPath === "/methodology" ? "page" : undefined}
            role="listitem"
          >
            Methodology
          </a>
          <a
            href="/data"
            className={`app-nav__tab${currentPath === "/data" ? " app-nav__tab--active" : ""}`}
            aria-current={currentPath === "/data" ? "page" : undefined}
            role="listitem"
          >
            Data
          </a>
        </div>
      </nav>

      {/* Main grid: sidebar + content */}
      <div className="app-main">
        {/* Left sidebar */}
        <aside className="app-sidebar" aria-label="Domain and model controls">
          {appState === "loading" && (
            <div className="sidebar-domain">
              <span className="sidebar-domain__label">Domain</span>
              <p style={{ color: "var(--color-text-muted)", fontSize: "var(--font-size-xs)", padding: "var(--space-2)" }}>
                Loading...
              </p>
            </div>
          )}

          {appState === "error" && (
            <div className="sidebar-domain">
              <p style={{ color: "var(--color-text-secondary)", fontSize: "var(--font-size-xs)", padding: "var(--space-2)" }}>
                Could not load data.
              </p>
            </div>
          )}

          {appState === "loaded" && domainResult !== null && (
            <ProviderModelTree
              domainResult={domainResult}
              selectedModels={selectedModels}
              onSelectionChange={setSelectedModels}
              modelColors={modelColors}
              domains={domains}
              activeSlug={activeSlug}
              onDomainSelect={setActiveSlug}
              openWeightsOnly={openWeightsOnly}
              onOpenWeightsToggle={setOpenWeightsOnly}
            />
          )}

          {appState === "loaded" && domainLoading && (
            <div className="sidebar-domain">
              <span className="sidebar-domain__label">Domain</span>
              <p style={{ color: "var(--color-text-muted)", fontSize: "var(--font-size-xs)", padding: "var(--space-2)" }}>
                Loading...
              </p>
            </div>
          )}
        </aside>

        {/* Content area */}
        <div className="app-content">
          {appState === "loading" && (
            <div
              className="content-placeholder content-placeholder--loading"
              role="status"
              aria-live="polite"
              aria-label="Loading domain data"
              style={{ margin: "var(--space-8)", fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)" }}
            >
              Loading...
            </div>
          )}

          {appState === "error" && (
            <div
              className="content-placeholder content-placeholder--error"
              role="alert"
              aria-live="assertive"
              style={{ margin: "var(--space-8)", fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)" }}
            >
              Could not load data. Refresh the page or check your connection.
            </div>
          )}

          {appState === "loaded" && !domainLoading && domainResult !== null && (
            <>
              {/* Selection summary bar */}
              <SelectionBar
                domainResult={domainResult}
                selectedModels={selectedModels}
                onRemoveModel={(id) => setSelectedModels(selectedModels.filter((m) => m !== id))}
                modelColors={modelColors}
              />

              {/* DataExplorer in app-shell mode: pass external state */}
              <div className="app-explorer-content">
                <DataExplorer
                  domainResult={domainResult}
                  externalSelectedModels={selectedModels}
                  onExternalSelectionChange={setSelectedModels}
                  externalActiveVizTab={activeVizTab}
                  onExternalVizTabChange={setActiveVizTab}
                />
              </div>
            </>
          )}

          {appState === "loaded" && domainLoading && (
            <div
              className="content-placeholder content-placeholder--loading"
              role="status"
              aria-live="polite"
              aria-label="Loading domain data"
              style={{ margin: "var(--space-8)", fontSize: "var(--font-size-sm)", color: "var(--color-text-muted)" }}
            >
              Loading...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Selection summary bar ────────────────────────────────────────────────────

interface SelectionBarProps {
  domainResult: DomainResultPublished;
  selectedModels: string[];
  onRemoveModel: (id: string) => void;
  modelColors: Record<string, string>;
}

import { modelShortName } from "./lib/modelShortName";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function SelectionBar({ domainResult: _domainResult, selectedModels, onRemoveModel, modelColors }: SelectionBarProps) {
  const CHIP_LIMIT = 8;

  if (selectedModels.length === 0) {
    return (
      <div className="selection-bar" role="status" aria-live="polite">
        <span className="selection-bar__label">No models selected</span>
      </div>
    );
  }

  const visible = selectedModels.slice(0, CHIP_LIMIT);
  const overflow = selectedModels.length - CHIP_LIMIT;

  return (
    <div className="selection-bar" role="status" aria-live="polite" aria-label={`${selectedModels.length} models selected`}>
      <span className="selection-bar__label">Showing</span>
      {visible.map((id) => (
        <span key={id} className="selection-chip">
          <span
            className="selection-chip__dot"
            style={{ backgroundColor: modelColors[id] ?? "#888" }}
            aria-hidden="true"
          />
          {modelShortName(id)}
          <button
            type="button"
            className="selection-chip__remove"
            aria-label={`Remove ${modelShortName(id)}`}
            onClick={() => onRemoveModel(id)}
          >
            ×
          </button>
        </span>
      ))}
      {overflow > 0 && (
        <span className="selection-chip selection-chip--overflow">
          +{overflow} more
        </span>
      )}
    </div>
  );
}
