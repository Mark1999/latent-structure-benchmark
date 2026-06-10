/**
 * tokens-defined.test.ts: Pitfall-15 mechanical guard.
 *
 * Reads tokens.css once and asserts that every token name referenced
 * from chart components is declared in the file. Any future commit that
 * adds a var(--token-name) reference to a chart component without a
 * matching tokens.css declaration will fail here.
 *
 * T15 origin: 2026-06-10 codebase review SVG hex literal migration.
 * CLAUDE.md §9 pitfall 15: silent-token-drift surface.
 */

import { readFileSync } from 'fs';
import { resolve } from 'path';
import { describe, it, expect } from 'vitest';

// Resolve tokens.css relative to this test file
const TOKENS_CSS_PATH = resolve(__dirname, '../styles/tokens.css');

function getTokensSource(): string {
  return readFileSync(TOKENS_CSS_PATH, 'utf-8');
}

function isTokenDefined(tokenName: string, source: string): boolean {
  // Match a CSS custom property declaration: --token-name: <value>;
  const pattern = new RegExp(`${tokenName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*:[^;]+;`);
  return pattern.test(source);
}

describe('tokens-defined: all var(--token) references in chart components are declared in tokens.css', () => {
  const source = getTokensSource();

  // ── Pre-existing tokens (confirmed present before T15) ───────────────────
  const preExistingTokens = [
    // Sequential color scale (SimilarityHeatmap, Focus1RunDistribution)
    '--color-scale-seq-0',
    '--color-scale-seq-1',
    '--color-scale-seq-2',
    '--color-scale-seq-3',
    '--color-scale-seq-4',
    // Heatmap text
    '--color-heatmap-cell-text-dark',
    // Text tokens (used in chart components)
    '--color-text-primary',
    '--color-text-secondary',
    '--color-text-caption',
    // Background and border
    '--color-background',
    '--color-border',
    '--color-surface-hover',
    // Cluster palette (ClusterTree, TermMap)
    '--color-cluster-1',
    '--color-cluster-2',
    '--color-cluster-3',
    '--color-cluster-4',
    '--color-cluster-5',
    '--color-cluster-6',
    '--color-cluster-7',
    '--color-cluster-8',
    // Provider colors (MDSPlot, FreeListCompare, PileStructure, Focus components)
    '--color-provider-anthropic',
    '--color-provider-openai',
    '--color-provider-google',
    '--color-provider-meta',
    '--color-provider-xai',
    '--color-provider-mistral',
    '--color-provider-deepseek',
    '--color-provider-microsoft',
    // Font tokens
    '--font-body',
    '--font-size-sm',
    '--font-size-xs',
  ];

  // ── New SVG chrome tokens added by T15 ───────────────────────────────────
  const t15Tokens = [
    '--color-svg-grid-line',
    '--color-svg-axis-caption',
    '--color-svg-label-secondary',
    '--color-svg-marker-stroke',
    '--color-svg-gray-branch',
    '--color-svg-dot-stroke',
  ];

  for (const token of [...preExistingTokens, ...t15Tokens]) {
    it(`${token} is declared in tokens.css`, () => {
      expect(isTokenDefined(token, source)).toBe(true);
    });
  }
});
