/**
 * displayModel.test.ts — canonical model label function tests (T8, 2026-06-08).
 *
 * DESIGN_SYSTEM.md §18 (v0.14.0): pinned-output table + re-drift grep guards.
 * CLAUDE.md §6 rule 9: no real API calls.
 *
 * Two categories:
 *   1. Pinned-output assertions for every row in the UI/UX verdict worked-examples
 *      table (binding).
 *   2. Re-drift grep guards: no component may reintroduce a local shortName /
 *      shortModelName function or a bare .split('/').pop() reinvention.
 */

import { describe, it, expect } from 'vitest';
import { displayModel, displayProvider } from '../familyUtils';

// ── 1. Pinned-output assertions (binding — UI/UX verdict §18.4) ───────────────

describe('displayModel — pinned outputs (DESIGN_SYSTEM.md §18.4)', () => {
  // Anthropic models: strip 'claude-' prefix
  it('claude-opus-4-5 → opus-4-5', () => {
    expect(displayModel('claude-opus-4-5')).toBe('opus-4-5');
  });
  it('claude-opus-4-6 → opus-4-6', () => {
    expect(displayModel('claude-opus-4-6')).toBe('opus-4-6');
  });
  it('claude-sonnet-4-6 → sonnet-4-6', () => {
    expect(displayModel('claude-sonnet-4-6')).toBe('sonnet-4-6');
  });

  // OpenAI: strip org prefix, keep gpt- token
  it('openai/gpt-5.2 → gpt-5.2', () => {
    expect(displayModel('openai/gpt-5.2')).toBe('gpt-5.2');
  });
  it('openai/gpt-5.4 → gpt-5.4', () => {
    expect(displayModel('openai/gpt-5.4')).toBe('gpt-5.4');
  });
  it('openai/gpt-5.4-mini → gpt-5.4-mini', () => {
    expect(displayModel('openai/gpt-5.4-mini')).toBe('gpt-5.4-mini');
  });

  // Google: strip org prefix, keep gemini- token
  it('google/gemini-2.5-flash → gemini-2.5-flash', () => {
    expect(displayModel('google/gemini-2.5-flash')).toBe('gemini-2.5-flash');
  });
  it('google/gemini-2.5-pro → gemini-2.5-pro', () => {
    expect(displayModel('google/gemini-2.5-pro')).toBe('gemini-2.5-pro');
  });

  // Meta: strip org prefix, keep llama- token
  it('meta-llama/llama-4-maverick → llama-4-maverick', () => {
    expect(displayModel('meta-llama/llama-4-maverick')).toBe('llama-4-maverick');
  });

  // xAI: strip org prefix, keep grok- token (no collision with phi-4 → phi-4)
  it('x-ai/grok-4 → grok-4', () => {
    expect(displayModel('x-ai/grok-4')).toBe('grok-4');
  });
  it('x-ai/grok-4.20 → grok-4.20', () => {
    expect(displayModel('x-ai/grok-4.20')).toBe('grok-4.20');
  });

  // Mistral: strip org prefix, keep mistral- token
  it('mistralai/mistral-large-2512 → mistral-large-2512', () => {
    expect(displayModel('mistralai/mistral-large-2512')).toBe('mistral-large-2512');
  });
  it('mistralai/mistral-small-2603 → mistral-small-2603', () => {
    expect(displayModel('mistralai/mistral-small-2603')).toBe('mistral-small-2603');
  });

  // DeepSeek: strip org prefix, keep deepseek- token (NOT 'ds-')
  it('deepseek/deepseek-v3.2 → deepseek-v3.2 (not ds-v3.2)', () => {
    expect(displayModel('deepseek/deepseek-v3.2')).toBe('deepseek-v3.2');
  });

  // Microsoft: strip org prefix, keep phi- token
  it('microsoft/phi-4 → phi-4', () => {
    expect(displayModel('microsoft/phi-4')).toBe('phi-4');
  });

  // Edge cases
  it('unknown-model → unknown-model (no slash, no claude-)', () => {
    expect(displayModel('unknown-model')).toBe('unknown-model');
  });
  it('org/unknown-model → unknown-model (slash stripped)', () => {
    expect(displayModel('org/unknown-model')).toBe('unknown-model');
  });
  it('"" → "" (empty guard)', () => {
    expect(displayModel('')).toBe('');
  });
});

// ── 2. Re-drift grep guards (DESIGN_SYSTEM.md §18.2) ─────────────────────────
//
// Use import.meta.glob to load ALL component source files as raw strings
// (Vite built-in, no @types/node needed). The ?raw suffix yields file content.
//
// Round 2 (2026-06-08): expanded from 13 to ALL components/**/*.tsx so future
// components are automatically covered. Guards ban three local-helper patterns:
//   shortName / shortModelName / shortModelDisplayName (all three function names)
// and the inline split-pop / replace-prefix model-label idioms.

const allComponentSources = import.meta.glob(
  '../../components/**/*.tsx',
  { query: '?raw', import: 'default', eager: true },
) as Record<string, string>;

describe('re-drift grep guards — ALL components must not reintroduce local helpers (§18.2)', () => {
  it('loaded at least 16 component files for grep guard', () => {
    expect(Object.keys(allComponentSources).length).toBeGreaterThanOrEqual(16);
  });

  it('no component defines a local shortName / shortModelName / shortModelDisplayName function', () => {
    const violations: string[] = [];
    const rePattern = /^function\s+(shortName|shortModelName|shortModelDisplayName)\s*\(/m;
    for (const [filePath, content] of Object.entries(allComponentSources)) {
      if (rePattern.test(content)) {
        violations.push(filePath);
      }
    }
    expect(violations).toEqual([]);
  });

  it("no component reinvents the split-pop model-label pattern (.split('/').pop())", () => {
    const violations: string[] = [];
    // Match bare .split('/').pop() usage — the reinvention pattern for model
    // labels that §18.2 forbids in all components.
    const splitPopPattern = /\.split\(['"]\/['"]\)\.pop\(\)/;
    for (const [filePath, content] of Object.entries(allComponentSources)) {
      if (splitPopPattern.test(content)) {
        violations.push(filePath);
      }
    }
    expect(violations).toEqual([]);
  });

  it('no component reinvents the replace-prefix model-label pattern (.replace(/^[a-z]+-/)', () => {
    const violations: string[] = [];
    // Match bare .replace(/^[a-z]+-/, ...) usage — the stripping idiom from
    // Timeline.tsx:47/63 that produced grok-4→4 / phi-4→4 collisions.
    const replacePrefixPattern = /\.replace\(\/\^\[a-z\]\+-\//;
    for (const [filePath, content] of Object.entries(allComponentSources)) {
      if (replacePrefixPattern.test(content)) {
        violations.push(filePath);
      }
    }
    expect(violations).toEqual([]);
  });

  it('no component defines a local displayProvider or resolveProvider function (T7 guard)', () => {
    const violations: string[] = [];
    const rePattern = /^function\s+(displayProvider|resolveProvider)\s*\(/m;
    for (const [filePath, content] of Object.entries(allComponentSources)) {
      if (rePattern.test(content)) {
        violations.push(filePath);
      }
    }
    expect(violations).toEqual([]);
  });
});

// ── 3. Pinned-output assertions for displayProvider (T7, 2026-06-08) ──────────

describe('displayProvider — pinned outputs', () => {
  // OpenRouter family-to-provider mappings
  it('openrouter gpt → openai', () => {
    expect(displayProvider({ provider: 'openrouter', family: 'gpt' })).toBe('openai');
  });
  it('openrouter llama → meta', () => {
    expect(displayProvider({ provider: 'openrouter', family: 'llama' })).toBe('meta');
  });
  it('openrouter mistral → mistral', () => {
    expect(displayProvider({ provider: 'openrouter', family: 'mistral' })).toBe('mistral');
  });
  it('openrouter deepseek → deepseek', () => {
    expect(displayProvider({ provider: 'openrouter', family: 'deepseek' })).toBe('deepseek');
  });
  it('openrouter phi → microsoft', () => {
    expect(displayProvider({ provider: 'openrouter', family: 'phi' })).toBe('microsoft');
  });
  it('openrouter qwen → openrouter (unmapped fall-through)', () => {
    expect(displayProvider({ provider: 'openrouter', family: 'qwen' })).toBe('openrouter');
  });

  // Non-openrouter pass-through
  it('anthropic/claude → anthropic', () => {
    expect(displayProvider({ provider: 'anthropic', family: 'claude' })).toBe('anthropic');
  });
  it('google/gemini → google', () => {
    expect(displayProvider({ provider: 'google', family: 'gemini' })).toBe('google');
  });
  it('xai/grok → xai', () => {
    expect(displayProvider({ provider: 'xai', family: 'grok' })).toBe('xai');
  });
});
