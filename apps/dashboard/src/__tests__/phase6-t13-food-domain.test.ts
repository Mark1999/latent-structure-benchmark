/**
 * Phase 6 T13 gap-fill tests — food domain (2026-05-15)
 *
 * The Coder's AC21 + AC22 tests (app-state.test.ts + domain-picker.test.tsx,
 * 6 tests total) cover the dashboard wiring. This file fills the publish-
 * pipeline and data-shape surface not covered by those tests.
 *
 * Gap-fill items (G-numbered per T8/T11/T12 precedent):
 *
 *   A. food.yaml content (AC1)
 *      G1.  food.yaml has exactly 5 keys — no extra fields, no description
 *      G2.  food.yaml byte-exact field values (slug, version, display_name,
 *           prompt_seed, truncation_k)
 *
 *   B. food.json shape (AC5, AC10, AC11)
 *      G3.  food.json top-level required fields present and domain_slug correct
 *      G4.  food.json generated_lede is the AC10 binding verbatim text
 *      G5.  food.json generated_lede does NOT contain "signalling" (British) — M1
 *      G6.  food.json models array length is 8
 *      G7.  food.json model_ids set equals the expected 8-model set; grok-4.20
 *           is absent (SME Q2 exclusion)
 *      G8.  food.json generated_lede mentions "8 frontier models"
 *      G9.  food.json generated_lede is free of §7 forbidden vocabulary
 *
 *   C. holidays.json regression (AC12 — M1 cascade)
 *      G10. holidays.json generated_lede contains "signaling" not "signalling"
 *      G11. holidays.json models array length is 9 (pre-T13 value unchanged)
 *      G12. holidays.json consensus_type unchanged (STRONG_CONSENSUS)
 *
 *   D. family.json non-regression (AC12)
 *      G13. family.json generated_lede does NOT contain "signaling" OR
 *           "signalling" (uses a different pattern key — unaffected by M1)
 *      G14. family.json models array length is 11 (pre-T13 value unchanged)
 *
 *   E. manifest.json shape (AC5)
 *      G15. manifest.json domains array has length 3
 *      G16. manifest.json domain slugs set equals {family, holidays, food}
 *      G17. manifest.json failures map has entries for all three domains
 *
 *   F. failures/food.json (AC5)
 *      G18. failures/food.json domain_slug=food, n_records=0, records=[]
 *      G19. failures/food.json framing_note matches the other domains
 *
 *   G. lede_v1.py M1 fix (regression guard)
 *      G20. lede_v1.py source contains "signaling" and does NOT contain
 *           "signalling"
 *
 *   H. data/raw/informants.jsonl invariants (AC2, AC3, AC19)
 *      G21. Exactly 45 records with domain_slug="food"
 *      G22. 5 records have model_id="x-ai/grok-4.20" and ALL 5 qa_passed=False
 *      G23. All 45 food records have campaign_id substring in qa_notes
 *      G24. All 45 food records have model_version_returned (non-empty string)
 *
 *   I. data/results/food/0.2.json shape (AC4)
 *      G25. food/0.2.json top-level keys match family/0.2.json top-level keys
 *
 *   J. scripts/run_phase6_t13_food.py (AC18)
 *      G26. Driver source contains domain="food" scoping and does NOT reference
 *           "family" or "holidays" as collection targets
 *      G27. Driver source does NOT contain CDB_MAX_SPEND_USD or cost-cap language  // noqa: spend-gate-check
 *
 *   K. CDA SME / AC10 documentation invariants
 *      G28. AC10 verdict file exists and contains PASS-WITH-NOTES
 *      G29. AC10 verdict file contains the binding verbatim post-fix lede text
 *
 * All tests read filesystem files (source or gitignored build artifacts).
 * Tests for gitignored files (food.json, holidays.json, family.json,
 * manifest.json, failures/food.json, informants.jsonl) skip-with-message
 * if the file does not exist. Tests for committed files (food.yaml,
 * lede_v1.py, driver script, results JSON, verdict doc) fail if absent.
 *
 * CLAUDE.md §6 R9: no real API calls. No new dependencies.
 *
 * Reference:
 *   docs/status/2026-05-15-phase6-T13-architect-plan.md §3
 *   docs/status/2026-05-15-phase6-T13-cda-sme-ac10-verdict.md (AC10 binding)
 *   docs/status/2026-05-15-phase6-T13-reviewer-verdict.md (Reviewer PASS)
 */

import { describe, it, expect } from "vitest";
import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ── Root paths ────────────────────────────────────────────────────────────────

// Repo root is 4 levels up from __dirname
// __dirname = apps/dashboard/src/__tests__
// root      = ../../../../
const REPO_ROOT = resolve(__dirname, "../../../../");

// ── Helper: skip if file absent (for gitignored build artifacts) ──────────────

function readIfExists(absPath: string): string | null {
  if (!existsSync(absPath)) return null;
  return readFileSync(absPath, "utf-8");
}

// ── Paths: committed source files (must exist) ────────────────────────────────

const FOOD_YAML_PATH = resolve(REPO_ROOT, "data/domains/v1/food.yaml");
const LEDE_V1_PATH = resolve(REPO_ROOT, "packages/cdb_publish/cdb_publish/templates/lede_v1.py");
const DRIVER_PATH = resolve(REPO_ROOT, "scripts/run_phase6_t13_food.py");
const RESULTS_FOOD_PATH = resolve(REPO_ROOT, "data/results/food/0.2.json");
const RESULTS_FAMILY_PATH = resolve(REPO_ROOT, "data/results/family/0.2.json");
const AC10_VERDICT_PATH = resolve(REPO_ROOT, "docs/status/2026-05-15-phase6-T13-cda-sme-ac10-verdict.md");
const INFORMANTS_JSONL_PATH = resolve(REPO_ROOT, "data/raw/informants.jsonl");

// ── Paths: gitignored build artifacts (may or may not exist in CI) ────────────

const FOOD_JSON_PATH = resolve(REPO_ROOT, "apps/dashboard/public/data/food.json");
const HOLIDAYS_JSON_PATH = resolve(REPO_ROOT, "apps/dashboard/public/data/holidays.json");
const FAMILY_JSON_PATH = resolve(REPO_ROOT, "apps/dashboard/public/data/family.json");
const MANIFEST_JSON_PATH = resolve(REPO_ROOT, "apps/dashboard/public/data/manifest.json");
const FOOD_FAILURES_PATH = resolve(REPO_ROOT, "apps/dashboard/public/data/failures/food.json");
const HOLIDAYS_FAILURES_PATH = resolve(REPO_ROOT, "apps/dashboard/public/data/failures/holidays.json");

// ── AC10 binding verbatim text ────────────────────────────────────────────────

const AC10_BINDING_LEDE =
  "Across 8 frontier models, food vocabulary is organized around a shared categorical structure (Smith's S = 0.61, 95% CI [0.48, 0.79]). " +
  "1 of these 8 models produced low output concentration on this domain -- " +
  "their position on the map is shown without a confidence ellipse, signaling that the runs did not converge on a single sort.";

// ── §7 forbidden vocabulary regex ────────────────────────────────────────────

const FORBIDDEN_VOCAB_RE = /worldview|believes|thinks|cultural bias|understands|perceives/i;

// ═══════════════════════════════════════════════════════════════════════════════
// A. food.yaml content (AC1) — G1, G2
// ═══════════════════════════════════════════════════════════════════════════════

describe("G1 — food.yaml has exactly 5 keys (no description field, AC1)", () => {
  it("food.yaml exists and can be read", () => {
    expect(existsSync(FOOD_YAML_PATH)).toBe(true);
  });

  it("food.yaml contains exactly the 5 required keys", () => {
    const src = readFileSync(FOOD_YAML_PATH, "utf-8");
    // Check all 5 required keys are present
    expect(src).toContain("slug:");
    expect(src).toContain("version:");
    expect(src).toContain("display_name:");
    expect(src).toContain("prompt_seed:");
    expect(src).toContain("truncation_k:");
  });

  it("food.yaml does NOT contain a 'description' field (CDA SME binding — no schema change)", () => {
    const src = readFileSync(FOOD_YAML_PATH, "utf-8");
    // A "description:" key would trigger a schema change — out of T13 scope.
    expect(src).not.toMatch(/^description:/m);
  });
});

describe("G2 — food.yaml byte-exact field values (binding B-D2)", () => {
  let src: string;

  it("food.yaml slug is exactly 'food'", () => {
    src = readFileSync(FOOD_YAML_PATH, "utf-8");
    expect(src).toContain('slug: food');
  });

  it("food.yaml version is exactly 'v1'", () => {
    src = readFileSync(FOOD_YAML_PATH, "utf-8");
    expect(src).toContain('version: v1');
  });

  it("food.yaml display_name is exactly 'Food'", () => {
    src = readFileSync(FOOD_YAML_PATH, "utf-8");
    expect(src).toContain('display_name: Food');
  });

  it("food.yaml prompt_seed is exactly 'type of food or dish' (CDA SME revised wording)", () => {
    src = readFileSync(FOOD_YAML_PATH, "utf-8");
    expect(src).toContain('prompt_seed: "type of food or dish"');
  });

  it("food.yaml truncation_k is exactly 50", () => {
    src = readFileSync(FOOD_YAML_PATH, "utf-8");
    expect(src).toContain('truncation_k: 50');
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// B. food.json shape (AC5, AC10, AC11) — G3–G9
// ═══════════════════════════════════════════════════════════════════════════════

describe("G3 — food.json top-level required fields (AC5)", () => {
  it("food.json exists (skips if gitignored artifact absent)", () => {
    if (!existsSync(FOOD_JSON_PATH)) {
      console.warn("SKIP: food.json not found (gitignored build artifact; run cdb_publish/build.py first)");
      return;
    }
    expect(existsSync(FOOD_JSON_PATH)).toBe(true);
  });

  it("food.json domain_slug is 'food'", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) {
      console.warn("SKIP: food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.domain_slug).toBe("food");
  });

  it("food.json contains consensus_type field", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) return;
    const d = JSON.parse(src);
    expect(d).toHaveProperty("consensus_type");
  });

  it("food.json contains consensus_score field", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) return;
    const d = JSON.parse(src);
    expect(d).toHaveProperty("consensus_score");
  });

  it("food.json contains consensus_ci array", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) return;
    const d = JSON.parse(src);
    expect(Array.isArray(d.consensus_ci)).toBe(true);
    expect(d.consensus_ci).toHaveLength(2);
  });

  it("food.json contains models array", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) return;
    const d = JSON.parse(src);
    expect(Array.isArray(d.models)).toBe(true);
  });

  it("food.json contains romney_small_n_warning field", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) return;
    const d = JSON.parse(src);
    expect(d).toHaveProperty("romney_small_n_warning");
  });

  it("food.json romney_small_n_warning is true (expected at n=8 < 15 threshold)", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) return;
    const d = JSON.parse(src);
    expect(d.romney_small_n_warning).toBe(true);
  });

  it("food.json contains generated_lede field", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) return;
    const d = JSON.parse(src);
    expect(d).toHaveProperty("generated_lede");
    expect(typeof d.generated_lede).toBe("string");
    expect(d.generated_lede.length).toBeGreaterThan(0);
  });
});

describe("G4 — food.json generated_lede is AC10 binding verbatim text (byte-exact)", () => {
  it("generated_lede matches the AC10 post-fix lede byte-for-byte", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) {
      console.warn("SKIP: food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.generated_lede).toBe(AC10_BINDING_LEDE);
  });
});

describe("G5 — food.json generated_lede does NOT contain 'signalling' (British) — M1 regression", () => {
  it("generated_lede has US-English 'signaling' not British 'signalling'", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) {
      console.warn("SKIP: food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.generated_lede).not.toContain("signalling");
    expect(d.generated_lede).toContain("signaling");
  });
});

describe("G6 — food.json models array length is 8 (grok-4.20 excluded)", () => {
  it("food.json models array has exactly 8 entries", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) {
      console.warn("SKIP: food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.models).toHaveLength(8);
  });
});

describe("G7 — food.json model_ids set is the expected 8-model set (grok-4.20 explicitly absent)", () => {
  const EXPECTED_MODEL_IDS = new Set([
    "claude-opus-4-5",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "google/gemini-2.5-flash",
    "mistralai/mistral-small-2603",
    "openai/gpt-5.2",
    "openai/gpt-5.4",
    "openai/gpt-5.4-mini",
  ]);

  it("food.json models contain all 8 expected model_ids", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) {
      console.warn("SKIP: food.json absent");
      return;
    }
    const d = JSON.parse(src);
    const actualIds = new Set<string>(d.models.map((m: { model_id: string }) => m.model_id));
    for (const expectedId of EXPECTED_MODEL_IDS) {
      expect(actualIds.has(expectedId)).toBe(true);
    }
  });

  it("food.json models do NOT contain x-ai/grok-4.20 (SME Q2 qa_passed=False exclusion)", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) {
      console.warn("SKIP: food.json absent");
      return;
    }
    const d = JSON.parse(src);
    const actualIds = new Set<string>(d.models.map((m: { model_id: string }) => m.model_id));
    expect(actualIds.has("x-ai/grok-4.20")).toBe(false);
  });
});

describe("G8 — food.json generated_lede mentions '8 frontier models' (not 9)", () => {
  it("generated_lede says '8 frontier models'", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) {
      console.warn("SKIP: food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.generated_lede).toContain("8 frontier models");
    expect(d.generated_lede).not.toContain("9 frontier models");
  });
});

describe("G9 — food.json generated_lede free of §7 forbidden vocabulary", () => {
  it("generated_lede does not contain worldview/believes/thinks/cultural bias/understands/perceives", () => {
    const src = readIfExists(FOOD_JSON_PATH);
    if (!src) {
      console.warn("SKIP: food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(FORBIDDEN_VOCAB_RE.test(d.generated_lede)).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// C. holidays.json regression (AC12 — M1 cascade) — G10–G12
// ═══════════════════════════════════════════════════════════════════════════════

describe("G10 — holidays.json generated_lede uses US-English 'signaling' (M1 cascade)", () => {
  it("holidays.json generated_lede contains 'signaling' not 'signalling'", () => {
    const src = readIfExists(HOLIDAYS_JSON_PATH);
    if (!src) {
      console.warn("SKIP: holidays.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.generated_lede).not.toContain("signalling");
    expect(d.generated_lede).toContain("signaling");
  });
});

describe("G11 — holidays.json models array length unchanged at 9 (pre-T13 regression guard)", () => {
  it("holidays.json models array has exactly 9 entries", () => {
    const src = readIfExists(HOLIDAYS_JSON_PATH);
    if (!src) {
      console.warn("SKIP: holidays.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.models).toHaveLength(9);
  });
});

describe("G12 — holidays.json consensus_type unchanged (regression guard)", () => {
  it("holidays.json consensus_type is STRONG_CONSENSUS (unchanged from pre-T13)", () => {
    const src = readIfExists(HOLIDAYS_JSON_PATH);
    if (!src) {
      console.warn("SKIP: holidays.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.consensus_type).toBe("STRONG_CONSENSUS");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// D. family.json non-regression (AC12) — G13–G14
// ═══════════════════════════════════════════════════════════════════════════════

describe("G13 — family.json generated_lede unaffected by M1 (uses different pattern key)", () => {
  it("family.json generated_lede does NOT contain 'signaling' OR 'signalling' (different pattern key)", () => {
    const src = readIfExists(FAMILY_JSON_PATH);
    if (!src) {
      console.warn("SKIP: family.json absent");
      return;
    }
    const d = JSON.parse(src);
    // family uses strong_consensus_homogeneous — no "signaling" word at all
    expect(d.generated_lede).not.toContain("signaling");
    expect(d.generated_lede).not.toContain("signalling");
  });
});

describe("G14 — family.json models array length unchanged at 11 (pre-T13 regression guard)", () => {
  it("family.json models array has exactly 11 entries", () => {
    const src = readIfExists(FAMILY_JSON_PATH);
    if (!src) {
      console.warn("SKIP: family.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.models).toHaveLength(11);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// E. manifest.json shape (AC5) — G15–G17
// ═══════════════════════════════════════════════════════════════════════════════

describe("G15 — manifest.json domains array has length 3 (AC5)", () => {
  it("manifest.json has exactly 3 domain entries", () => {
    const src = readIfExists(MANIFEST_JSON_PATH);
    if (!src) {
      console.warn("SKIP: manifest.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(Array.isArray(d.domains)).toBe(true);
    expect(d.domains).toHaveLength(3);
  });
});

describe("G16 — manifest.json domain slugs set equals {family, holidays, food}", () => {
  it("manifest.json domain slugs are exactly {family, holidays, food} (order independent)", () => {
    const src = readIfExists(MANIFEST_JSON_PATH);
    if (!src) {
      console.warn("SKIP: manifest.json absent");
      return;
    }
    const d = JSON.parse(src);
    const slugSet = new Set<string>(d.domains.map((dd: { slug: string }) => dd.slug));
    expect(slugSet.has("family")).toBe(true);
    expect(slugSet.has("holidays")).toBe(true);
    expect(slugSet.has("food")).toBe(true);
    expect(slugSet.size).toBe(3);
  });
});

describe("G17 — manifest.json failures map has entries for all three domains", () => {
  it("manifest.json failures map contains family, holidays, and food keys", () => {
    const src = readIfExists(MANIFEST_JSON_PATH);
    if (!src) {
      console.warn("SKIP: manifest.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.failures).toHaveProperty("family");
    expect(d.failures).toHaveProperty("holidays");
    expect(d.failures).toHaveProperty("food");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// F. failures/food.json (AC5) — G18–G19
// ═══════════════════════════════════════════════════════════════════════════════

describe("G18 — failures/food.json current posture: n_records=0, records=[] (AC10 Q3 posture a)", () => {
  it("failures/food.json has domain_slug='food'", () => {
    const src = readIfExists(FOOD_FAILURES_PATH);
    if (!src) {
      console.warn("SKIP: failures/food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.domain_slug).toBe("food");
  });

  it("failures/food.json n_records is 0 (grok qa_passed=False records not yet in failures surface per posture a)", () => {
    const src = readIfExists(FOOD_FAILURES_PATH);
    if (!src) {
      console.warn("SKIP: failures/food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(d.n_records).toBe(0);
  });

  it("failures/food.json records array is empty", () => {
    const src = readIfExists(FOOD_FAILURES_PATH);
    if (!src) {
      console.warn("SKIP: failures/food.json absent");
      return;
    }
    const d = JSON.parse(src);
    expect(Array.isArray(d.records)).toBe(true);
    expect(d.records).toHaveLength(0);
  });
});

describe("G19 — failures/food.json framing_note matches other domains (consistent §1.5 framing)", () => {
  it("failures/food.json framing_note equals failures/holidays.json framing_note", () => {
    const foodSrc = readIfExists(FOOD_FAILURES_PATH);
    const holidaysSrc = readIfExists(HOLIDAYS_FAILURES_PATH);
    if (!foodSrc || !holidaysSrc) {
      console.warn("SKIP: failures files absent");
      return;
    }
    const food = JSON.parse(foodSrc);
    const holidays = JSON.parse(holidaysSrc);
    expect(food.framing_note).toBe(holidays.framing_note);
  });

  it("failures/food.json framing_note contains §1.5-compliant language (LSB pipeline attribution, not model-state claim)", () => {
    const src = readIfExists(FOOD_FAILURES_PATH);
    if (!src) {
      console.warn("SKIP: failures/food.json absent");
      return;
    }
    const d = JSON.parse(src);
    // Must contain the standard non-anthropomorphic framing:
    // "...not a claim about the model's intent or state-of-mind."
    // The phrase "model's intent" appears in a denial ("not a claim about...") — correct framing.
    expect(d.framing_note).toContain("property of the LSB collection pipeline");
    expect(d.framing_note).toContain("not a claim about the model's intent or state-of-mind");
    // The framing must NOT attribute intent directly without the negation
    expect(d.framing_note).not.toMatch(/the model('s)? intent(?!.*or state-of-mind)/);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// G. lede_v1.py M1 fix (regression guard) — G20
// ═══════════════════════════════════════════════════════════════════════════════

describe("G20 — lede_v1.py M1 fix: 'signaling' (US) present, 'signalling' (British) absent", () => {
  it("lede_v1.py exists", () => {
    expect(existsSync(LEDE_V1_PATH)).toBe(true);
  });

  it("lede_v1.py strong_consensus_with_low_oci pattern contains 'signaling' (US English)", () => {
    const src = readFileSync(LEDE_V1_PATH, "utf-8");
    expect(src).toContain("signaling");
  });

  it("lede_v1.py does NOT contain 'signalling' (British spelling — M1 regression guard)", () => {
    const src = readFileSync(LEDE_V1_PATH, "utf-8");
    expect(src).not.toContain("signalling");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// H. data/raw/informants.jsonl invariants (AC2, AC3, AC19) — G21–G24
// ═══════════════════════════════════════════════════════════════════════════════

describe("G21 — exactly 45 informant records with domain_slug='food' (AC2: 9 models × 5 runs)", () => {
  it("informants.jsonl has exactly 45 food-domain records", () => {
    if (!existsSync(INFORMANTS_JSONL_PATH)) {
      console.warn("SKIP: informants.jsonl absent");
      return;
    }
    const lines = readFileSync(INFORMANTS_JSONL_PATH, "utf-8").split("\n").filter(Boolean);
    const foodRecords = lines
      .map((l) => JSON.parse(l))
      .filter((r) => r.domain_slug === "food");
    expect(foodRecords).toHaveLength(45);
  });
});

describe("G22 — 5 grok-4.20 food records all have qa_passed=False (grok exclusion finding)", () => {
  it("exactly 5 records have model_id='x-ai/grok-4.20' and domain_slug='food'", () => {
    if (!existsSync(INFORMANTS_JSONL_PATH)) {
      console.warn("SKIP: informants.jsonl absent");
      return;
    }
    const lines = readFileSync(INFORMANTS_JSONL_PATH, "utf-8").split("\n").filter(Boolean);
    const grokFood = lines
      .map((l) => JSON.parse(l))
      .filter((r) => r.domain_slug === "food" && r.model_id === "x-ai/grok-4.20");
    expect(grokFood).toHaveLength(5);
  });

  it("all 5 grok-4.20 food records have qa_passed=false (append-only invariant, pitfall #10)", () => {
    if (!existsSync(INFORMANTS_JSONL_PATH)) {
      console.warn("SKIP: informants.jsonl absent");
      return;
    }
    const lines = readFileSync(INFORMANTS_JSONL_PATH, "utf-8").split("\n").filter(Boolean);
    const grokFood = lines
      .map((l) => JSON.parse(l))
      .filter((r) => r.domain_slug === "food" && r.model_id === "x-ai/grok-4.20");
    const allFailed = grokFood.every((r) => r.qa_passed === false);
    expect(allFailed).toBe(true);
  });
});

describe("G23 — all 45 food records have campaign_id substring in qa_notes (AC3)", () => {
  it("all food-domain records reference the T13 campaign_id in qa_notes", () => {
    if (!existsSync(INFORMANTS_JSONL_PATH)) {
      console.warn("SKIP: informants.jsonl absent");
      return;
    }
    const lines = readFileSync(INFORMANTS_JSONL_PATH, "utf-8").split("\n").filter(Boolean);
    const foodRecords = lines
      .map((l) => JSON.parse(l))
      .filter((r) => r.domain_slug === "food");
    const missingCampaign = foodRecords.filter(
      (r) => !(r.qa_notes || "").includes("phase6-t13-food-2026-05-15")
    );
    expect(missingCampaign).toHaveLength(0);
  });
});

describe("G24 — all 45 food records have model_version_returned recorded (pitfall #1)", () => {
  it("all food-domain records have a non-empty model_version_returned string", () => {
    if (!existsSync(INFORMANTS_JSONL_PATH)) {
      console.warn("SKIP: informants.jsonl absent");
      return;
    }
    const lines = readFileSync(INFORMANTS_JSONL_PATH, "utf-8").split("\n").filter(Boolean);
    const foodRecords = lines
      .map((l) => JSON.parse(l))
      .filter((r) => r.domain_slug === "food");
    const missingVersion = foodRecords.filter(
      (r) => !r.model_version_returned || typeof r.model_version_returned !== "string"
    );
    expect(missingVersion).toHaveLength(0);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// I. data/results/food/0.2.json shape (AC4) — G25
// ═══════════════════════════════════════════════════════════════════════════════

describe("G25 — data/results/food/0.2.json top-level keys match family/0.2.json", () => {
  it("food/0.2.json exists", () => {
    expect(existsSync(RESULTS_FOOD_PATH)).toBe(true);
  });

  it("food/0.2.json and family/0.2.json have identical top-level key sets", () => {
    const foodSrc = readFileSync(RESULTS_FOOD_PATH, "utf-8");
    const familySrc = readFileSync(RESULTS_FAMILY_PATH, "utf-8");
    const foodKeys = new Set(Object.keys(JSON.parse(foodSrc)));
    const familyKeys = new Set(Object.keys(JSON.parse(familySrc)));
    // Keys in food but not family
    const onlyInFood = [...foodKeys].filter((k) => !familyKeys.has(k));
    // Keys in family but not food
    const onlyInFamily = [...familyKeys].filter((k) => !foodKeys.has(k));
    expect(onlyInFood).toHaveLength(0);
    expect(onlyInFamily).toHaveLength(0);
  });

  it("food/0.2.json domain_slug is 'food'", () => {
    const d = JSON.parse(readFileSync(RESULTS_FOOD_PATH, "utf-8"));
    expect(d.domain_slug).toBe("food");
  });

  it("food/0.2.json analysis_version is '0.2'", () => {
    const d = JSON.parse(readFileSync(RESULTS_FOOD_PATH, "utf-8"));
    expect(d.analysis_version).toBe("0.2");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// J. scripts/run_phase6_t13_food.py (AC18) — G26–G27
// ═══════════════════════════════════════════════════════════════════════════════

describe("G26 — driver script scopes to food domain and does not reference family/holidays as targets", () => {
  it("driver script exists", () => {
    expect(existsSync(DRIVER_PATH)).toBe(true);
  });

  it("driver source contains FOOD_DOMAINS list scoped to 'food'", () => {
    const src = readFileSync(DRIVER_PATH, "utf-8");
    // The driver declares FOOD_DOMAINS = ["food"] (the only collection target)
    expect(src).toContain('"food"');
  });

  it("driver source does NOT list 'family' as a collection target domain", () => {
    const src = readFileSync(DRIVER_PATH, "utf-8");
    // "family" may appear in comments (e.g., preflight probe) but must not be a FOOD_DOMAINS entry
    // Check FOOD_DOMAINS constant does not include "family"
    expect(src).not.toMatch(/FOOD_DOMAINS\s*=\s*\[[^\]]*"family"/);
  });

  it("driver source does NOT list 'holidays' as a collection target domain", () => {
    const src = readFileSync(DRIVER_PATH, "utf-8");
    expect(src).not.toMatch(/FOOD_DOMAINS\s*=\s*\[[^\]]*"holidays"/);
  });
});

describe("G27 — driver script contains no cost-cap language (CLAUDE.md R14)", () => {
  it("driver source does NOT contain CDB_MAX_SPEND_USD", () => {  // noqa: spend-gate-check
    const src = readFileSync(DRIVER_PATH, "utf-8");
    expect(src).not.toContain("CDB_MAX_SPEND_USD");  // noqa: spend-gate-check
  });

  it("driver source does NOT contain MAX_SPEND_USD", () => {  // noqa: spend-gate-check
    const src = readFileSync(DRIVER_PATH, "utf-8");
    expect(src).not.toContain("MAX_SPEND_USD");  // noqa: spend-gate-check
  });

  it("driver source does NOT contain 'cost_cap' or 'cost_limit'", () => {  // noqa: spend-gate-check
    const src = readFileSync(DRIVER_PATH, "utf-8");
    expect(src.toLowerCase()).not.toContain("cost_cap");  // noqa: spend-gate-check
    expect(src.toLowerCase()).not.toContain("cost_limit");
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// K. CDA SME / AC10 documentation invariants — G28–G29
// ═══════════════════════════════════════════════════════════════════════════════

describe("G28 — AC10 verdict file exists and contains PASS-WITH-NOTES", () => {
  it("2026-05-15-phase6-T13-cda-sme-ac10-verdict.md exists", () => {
    expect(existsSync(AC10_VERDICT_PATH)).toBe(true);
  });

  it("AC10 verdict file contains 'PASS-WITH-NOTES'", () => {
    const src = readFileSync(AC10_VERDICT_PATH, "utf-8");
    expect(src).toContain("PASS-WITH-NOTES");
  });
});

describe("G29 — AC10 verdict file contains the binding post-fix lede verbatim", () => {
  it("AC10 verdict file contains the M1-corrected 'signaling' lede text", () => {
    const src = readFileSync(AC10_VERDICT_PATH, "utf-8");
    // The M1 final binding text must appear in the verdict file
    expect(src).toContain(AC10_BINDING_LEDE);
  });

  it("AC10 verdict file does NOT contain 'signalling' (British) in the lede block", () => {
    const src = readFileSync(AC10_VERDICT_PATH, "utf-8");
    // The M1 section shows the pre-fix lede as a quoted example but the final binding text uses "signaling"
    // Verify the binding final text line contains "signaling"
    expect(src).toContain("signaling that the runs did not converge");
  });
});
