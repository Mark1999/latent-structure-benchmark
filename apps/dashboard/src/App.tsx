/**
 * LSB Dashboard — App shell.
 * Source: DESIGN_SYSTEM.md §2, §12.1 (reveal cascade), §12.2 (loading state), §12.5 (embed mode)
 *
 * Page state machine: loading → loaded | error
 * Loads manifest at mount via fetchManifest().
 * Detects ?embed=true and suppresses chrome per §12.5.
 */

import { useEffect, useState } from "react";
import "./styles/tokens.css";
import "./styles/app.css";

import { fetchManifest } from "./api/client";
import type { Manifest } from "./data/types";

import { Header } from "./components/Header";
import { ArticleHeader } from "./components/ArticleHeader";
import { Footer } from "./components/Footer";

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

export default function App() {
  const [appState, setAppState] = useState<AppState>("loading");
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const embedMode = isEmbedMode();

  useEffect(() => {
    let cancelled = false;

    fetchManifest()
      .then((m) => {
        if (!cancelled) {
          setManifest(m);
          setAppState("loaded");
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

  // Embed mode: render only the data explorer (T6+ will wire this up).
  // Per §12.5: no Header, Footer, ArticleHeader, KeyFinding, MethodologySummary.
  // For T4 (shell only, no DataExplorer yet), render a minimal embed placeholder.
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

          {appState === "loaded" && manifest !== null && (
            <div className="content-placeholder">
              {/* DataExplorer + KeyFinding + MethodologySummary render here in T5/T6+ */}
              {/* T4: placeholder showing available domains for smoke-test verification */}
              <p
                style={{
                  color: "var(--color-text-secondary)",
                  fontSize: "var(--font-size-sm)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {manifest.domains.length} domain
                {manifest.domains.length !== 1 ? "s" : ""} available:{" "}
                {manifest.domains.map((d) => d.slug).join(", ")}
              </p>
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
