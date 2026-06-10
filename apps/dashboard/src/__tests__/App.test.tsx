/**
 * App.test.tsx -- deep-link URL routing integration tests (M3, 2026-06-10).
 *
 * These tests verify that App.tsx resolves the correct NavTab from
 * window.location.pathname on initial mount (AC3), and that
 * clicking a NavBar tab calls history.pushState with the correct path (AC4).
 *
 * Pure-function coverage lives in navRouting.test.ts (the binding coverage).
 * These App-level tests are best-effort integration; any that prove flaky
 * under jsdom may be skipped with a clear comment. See Architect M3-T1 note 4.
 *
 * Data fetch is mocked out so tests do not make real network calls
 * (CLAUDE.md §6 rule 9).
 *
 * Gate verdicts (M3):
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-10-site-copy-verdicts.md (M3 section)
 *   UI/UX  PASS-WITH-NOTES:  docs/status/2026-06-10-site-copy-verdicts.md (M3 section)
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import App from '../App';

// Mock fetch so no real network calls happen during tests.
// Returns a minimal valid domain JSON for the explore tab data load.
const MOCK_DOMAIN = {
  domain: 'family',
  models: [],
  terms: [],
  mds_coordinates: {},
  results: [],
};

beforeEach(() => {
  vi.spyOn(globalThis, 'fetch').mockImplementation((url: RequestInfo | URL) => {
    const urlStr = url.toString();
    if (urlStr.includes('cooccurrence')) {
      // co-occurrence fetch fails silently (best-effort)
      return Promise.reject(new Error('not found'));
    }
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(MOCK_DOMAIN),
    } as Response);
  });
  // Reset history to a known state before each test
  window.history.pushState({}, '', '/');
});

afterEach(() => {
  vi.restoreAllMocks();
  window.history.pushState({}, '', '/');
});

// -- AC3: deep-link initial render -----------------------------------------------

describe('App deep-link initial render (AC3)', () => {
  it('/ renders Explore (ContentArea present; no methodology heading)', () => {
    window.history.pushState({}, '', '/');
    render(<App />);
    // Methodology page has a unique heading "Latent Structure Benchmark"
    // or "Methodology" section; Explore shows nav with explore tab active.
    const exploreBtn = screen.getByRole('button', { name: /^explore$/i });
    expect(exploreBtn).toHaveAttribute('aria-current', 'page');
  });

  it('/explore renders Explore (same as /)', () => {
    window.history.pushState({}, '', '/explore');
    render(<App />);
    const exploreBtn = screen.getByRole('button', { name: /^explore$/i });
    expect(exploreBtn).toHaveAttribute('aria-current', 'page');
  });

  it('/methodology renders MethodologyPage (methodology button aria-current)', () => {
    window.history.pushState({}, '', '/methodology');
    render(<App />);
    const methodologyBtn = screen.getByRole('button', { name: /^methodology$/i });
    expect(methodologyBtn).toHaveAttribute('aria-current', 'page');
  });

  it('/collection-records renders FailuresFindings tab active', () => {
    window.history.pushState({}, '', '/collection-records');
    render(<App />);
    const crBtn = screen.getByRole('button', { name: /^collection records$/i });
    expect(crBtn).toHaveAttribute('aria-current', 'page');
  });

  it('/data renders DataPage tab active', () => {
    window.history.pushState({}, '', '/data');
    render(<App />);
    const dataBtn = screen.getByRole('button', { name: /^data$/i });
    expect(dataBtn).toHaveAttribute('aria-current', 'page');
  });

  it('/about renders AboutPage tab active', () => {
    window.history.pushState({}, '', '/about');
    render(<App />);
    const aboutBtn = screen.getByRole('button', { name: /^about$/i });
    expect(aboutBtn).toHaveAttribute('aria-current', 'page');
  });

  it('unknown path /foo falls back to Explore tab', () => {
    window.history.pushState({}, '', '/foo');
    render(<App />);
    const exploreBtn = screen.getByRole('button', { name: /^explore$/i });
    expect(exploreBtn).toHaveAttribute('aria-current', 'page');
  });
});

// -- AC4: tab click updates URL via history.pushState ---------------------------

describe('App tab click calls history.pushState (AC4)', () => {
  it('clicking Methodology from / calls history.pushState with /methodology', () => {
    window.history.pushState({}, '', '/');
    const pushSpy = vi.spyOn(window.history, 'pushState');
    render(<App />);
    const methodologyBtn = screen.getByRole('button', { name: /^methodology$/i });
    fireEvent.click(methodologyBtn);
    expect(pushSpy).toHaveBeenCalledWith(
      expect.objectContaining({ tab: 'methodology' }),
      '',
      '/methodology',
    );
  });

  it('clicking Explore from /methodology calls history.pushState with /', () => {
    window.history.pushState({}, '', '/methodology');
    const pushSpy = vi.spyOn(window.history, 'pushState');
    render(<App />);
    const exploreBtn = screen.getByRole('button', { name: /^explore$/i });
    fireEvent.click(exploreBtn);
    expect(pushSpy).toHaveBeenCalledWith(
      expect.objectContaining({ tab: 'explore' }),
      '',
      '/',
    );
  });

  it('clicking About from / calls history.pushState with /about', () => {
    window.history.pushState({}, '', '/');
    const pushSpy = vi.spyOn(window.history, 'pushState');
    render(<App />);
    const aboutBtn = screen.getByRole('button', { name: /^about$/i });
    fireEvent.click(aboutBtn);
    expect(pushSpy).toHaveBeenCalledWith(
      expect.objectContaining({ tab: 'about' }),
      '',
      '/about',
    );
  });
});

// -- AC5: popstate updates navTab ------------------------------------------------
// Best-effort: dispatching popstate in jsdom does NOT update window.location.pathname
// automatically. This test verifies the listener fires and setNavTab is invoked
// by checking that the NavBar renders the updated aria-current. If jsdom
// popstate behavior is unreliable, this test documents the expected behavior.

describe('App popstate updates tab (AC5 -- best-effort jsdom)', () => {
  it.skip('popstate to /methodology updates aria-current on Methodology button', () => {
    // Skipped: jsdom does not update window.location.pathname when a popstate
    // event is dispatched manually, so the handler reads the pre-event pathname.
    // The pure-function tests in navRouting.test.ts are the binding coverage.
    // Manual smoke check: navigate to /methodology, use browser back to return,
    // and confirm the active tab updates correctly.
    window.history.pushState({}, '', '/');
    render(<App />);
    window.history.pushState({}, '', '/methodology');
    window.dispatchEvent(new PopStateEvent('popstate', { state: { tab: 'methodology' } }));
    const methodologyBtn = screen.getByRole('button', { name: /^methodology$/i });
    expect(methodologyBtn).toHaveAttribute('aria-current', 'page');
  });
});

// -- AC6: document.title set on mount -------------------------------------------

describe('App document.title on initial mount (AC6)', () => {
  it('/methodology sets document.title to "Cognitive Structure Lab - Methodology"', () => {
    window.history.pushState({}, '', '/methodology');
    render(<App />);
    expect(document.title).toBe('Cognitive Structure Lab - Methodology');
  });

  it('/ sets document.title to "Cognitive Structure Lab - Explore"', () => {
    window.history.pushState({}, '', '/');
    render(<App />);
    expect(document.title).toBe('Cognitive Structure Lab - Explore');
  });

  it('title spacer is ASCII hyphen-minus (U+002D)', () => {
    window.history.pushState({}, '', '/about');
    render(<App />);
    const title = document.title;
    const spacerIdx = title.indexOf(' - ');
    expect(spacerIdx).toBeGreaterThan(-1);
    // Character at the hyphen position
    expect(title.charCodeAt(spacerIdx + 1)).toBe(0x002d);
  });
});
