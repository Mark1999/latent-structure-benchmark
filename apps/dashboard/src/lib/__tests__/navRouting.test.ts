/**
 * navRouting.test.ts: pinned-output unit tests for pathToTab, tabToPath, tabToTitle.
 *
 * All functions are pure (no React, no DOM). Tests run under jsdom but need no
 * DOM features. No real API calls per CLAUDE.md §6 rule 9.
 *
 * Coverage:
 *   - All seven path-to-tab rows from Architect M3 §3 table (AC2)
 *   - Trailing-slash normalization
 *   - Case-insensitivity
 *   - Unknown-path fallback
 *   - tabToPath: one pinned row per tab (Explore -> '/', others -> '/' + tab)
 *   - tabToTitle: one pinned row per tab asserting ASCII hyphen-minus spacer (AC6)
 *
 * Title assertions use literal ASCII hyphen-minus (U+002D), not en-dash or em-dash.
 * This guards CDA SME M3-A1 / UI/UX N1 (no em-dash or en-dash in runtime strings).
 *
 * Gate verdicts (M3):
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-10-site-copy-verdicts.md (M3 section)
 *   UI/UX  PASS-WITH-NOTES:  docs/status/2026-06-10-site-copy-verdicts.md (M3 section)
 */

import { describe, it, expect } from 'vitest';
import { pathToTab, tabToPath, tabToTitle } from '../navRouting';

// -- pathToTab: Architect M3 §3 table pinned rows --------------------------------

describe('pathToTab -- M3 §3 table rows', () => {
  it('/ -> explore', () => {
    expect(pathToTab('/')).toBe('explore');
  });

  it('/explore -> explore', () => {
    expect(pathToTab('/explore')).toBe('explore');
  });

  it('/methodology -> methodology', () => {
    expect(pathToTab('/methodology')).toBe('methodology');
  });

  it('/collection-records -> collection-records', () => {
    expect(pathToTab('/collection-records')).toBe('collection-records');
  });

  it('/data -> data', () => {
    expect(pathToTab('/data')).toBe('data');
  });

  it('/about -> about', () => {
    expect(pathToTab('/about')).toBe('about');
  });

  it('unknown path falls back to explore', () => {
    expect(pathToTab('/foo/bar')).toBe('explore');
  });
});

// -- pathToTab: edge cases -------------------------------------------------------

describe('pathToTab -- edge cases', () => {
  it('trailing slash normalized: /methodology/ -> methodology', () => {
    expect(pathToTab('/methodology/')).toBe('methodology');
  });

  it('case-insensitive: /Methodology -> methodology', () => {
    expect(pathToTab('/Methodology')).toBe('methodology');
  });

  it('case-insensitive: /ABOUT -> about', () => {
    expect(pathToTab('/ABOUT')).toBe('about');
  });

  it('case-insensitive: /Collection-Records -> collection-records', () => {
    expect(pathToTab('/Collection-Records')).toBe('collection-records');
  });

  it('trailing slash on root: empty string after strip falls back to /', () => {
    // '' after stripping trailing slash -> normalized to '/' -> explore
    expect(pathToTab('')).toBe('explore');
  });

  it('deep unknown path falls back to explore: /foo/bar/baz', () => {
    expect(pathToTab('/foo/bar/baz')).toBe('explore');
  });
});

// -- tabToPath: one pinned row per tab -------------------------------------------

describe('tabToPath -- pinned rows (AC4, Architect M3 §3)', () => {
  it('explore -> / (canonical home)', () => {
    expect(tabToPath('explore')).toBe('/');
  });

  it('methodology -> /methodology', () => {
    expect(tabToPath('methodology')).toBe('/methodology');
  });

  it('collection-records -> /collection-records', () => {
    expect(tabToPath('collection-records')).toBe('/collection-records');
  });

  it('data -> /data', () => {
    expect(tabToPath('data')).toBe('/data');
  });

  it('about -> /about', () => {
    expect(tabToPath('about')).toBe('/about');
  });
});

// -- tabToTitle: one pinned row per tab, ASCII hyphen-minus spacer ---------------
// Title format: "Cognitive Structure Lab - <Label>" (U+002D, not U+2013 or U+2014)

describe('tabToTitle -- pinned rows (AC6, ASCII hyphen-minus spacer)', () => {
  it('explore -> "Cognitive Structure Lab - Explore"', () => {
    expect(tabToTitle('explore')).toBe('Cognitive Structure Lab - Explore');
  });

  it('methodology -> "Cognitive Structure Lab - Methodology"', () => {
    expect(tabToTitle('methodology')).toBe('Cognitive Structure Lab - Methodology');
  });

  it('collection-records -> "Cognitive Structure Lab - Collection records"', () => {
    // Label is FAILURES_TAB_LABEL = "Collection records" (CDA SME M1 Option A)
    expect(tabToTitle('collection-records')).toBe(
      'Cognitive Structure Lab - Collection records',
    );
  });

  it('data -> "Cognitive Structure Lab - Data"', () => {
    expect(tabToTitle('data')).toBe('Cognitive Structure Lab - Data');
  });

  it('about -> "Cognitive Structure Lab - About"', () => {
    expect(tabToTitle('about')).toBe('Cognitive Structure Lab - About');
  });

  // Guard: spacer must be ASCII hyphen-minus (U+002D), not en-dash (U+2013)
  // or em-dash (U+2014). Satisfies CDA SME M3-A1 and UI/UX N1.
  it('spacer is ASCII hyphen-minus U+002D (not en-dash or em-dash)', () => {
    const title = tabToTitle('explore');
    const spacerIndex = title.indexOf(' - ');
    expect(spacerIndex).toBeGreaterThan(-1);
    // Character between the two spaces
    const spacer = title.charCodeAt(spacerIndex + 1);
    expect(spacer).toBe(0x002d); // ASCII hyphen-minus
    expect(spacer).not.toBe(0x2013); // en-dash
    expect(spacer).not.toBe(0x2014); // em-dash
  });
});
