/**
 * PROMOTE-FOOD-V02 vitest tests (T2 + T3).
 *
 * T2: Byte-identity assertions for all five CDA SME binding strings:
 *   F3-R3-A  generated_lede rendered by ContentArea (domain fixture)
 *   F3-R3-B  NOT rendered in the dashboard; tested in T1 Python tests
 *   F3-R3-C  CI_DISCLOSURE_TEXT constant imported from consensus_disclosure.ts
 *   F3-R3-D  SMALL_N_TEXT constant imported from consensus_disclosure.ts
 *   F3-R3-E  methodology footnote rendered by MethodologyPage
 *
 *   U+2014 em-dash absence assertion across all five strings (CLAUDE.md hard rule).
 *
 * T3: Heatmap maverick-drop disclosure assertion.
 *   When domain.models contains a model absent from domain.mds_coordinates,
 *   ContentArea renders a heatmap-exclusion-caption paragraph for it.
 *
 * CLAUDE.md §6 rule 9: no real API calls. All data is fixture-based.
 * ARCHITECTURE.md §4.2: lede logic in cdb_publish; these tests assert the
 *   string surfaces correctly in the component tree.
 *
 * Gate verdicts:
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-11-promote-food-v02-cda-sme-verdict.md
 *   UI/UX PASS-WITH-NOTES:   docs/status/2026-06-11-promote-food-v02-uiux-verdict.md
 */

import { render } from "@testing-library/react";
import { ContentArea } from "../components/ContentArea";
import { MethodologyPage } from "../components/MethodologyPage";
import { CI_DISCLOSURE_TEXT_V02, CI_DISCLOSURE_TEXT_V03, SMALL_N_TEXT } from "../copy/consensus_disclosure";
import { FABLE_DISCLOSURE_FRAMING, FABLE_DISCLOSURE_BOUND } from "../copy/failures_findings";
import type { DomainExtended, PublishedModel } from "../data/types";

// ---------------------------------------------------------------------------
// F3-R3 binding strings (CDA SME adjudication round 3).
// ANY edit to these constants requires a fresh CDA SME pass.
// Source: .claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md
// PROMOTE-FOOD-V02 (2026-06-11).
// ---------------------------------------------------------------------------

/** F3-R3-A: food v0.2 generated_lede (WEAK_CONSENSUS with straddling CI). */
const F3_R3_A =
  "The food domain shows broad agreement across the 12-model slate. The" +
  " point estimate sits comfortably on the strong-consensus side of our" +
  " threshold, but the uncertainty band crosses it. The honest read is" +
  " that the strength of agreement is not nailed down at this collection" +
  " width.";

/** F3-R3-C: eigenratio CI disclosure line (re-exported from consensus_disclosure.ts). */
const F3_R3_C =
  "Romney CCM eigenratio 9.48, 95 percent bootstrap interval [4.91, 10.34], B=500. The interval crosses the 5.0 strong/weak threshold.";

/** F3-R3-D: small-n warning line (re-exported from consensus_disclosure.ts). */
const F3_R3_D =
  "The slate is 12 models, below the 15-model floor where Romney CCM eigenratios become statistically reliable. Read the classification with that floor in mind.";

/**
 * F3-R3-E: methodology footnote. Must match MethodologyPage id="food-v02-footnote"
 * paragraph text content verbatim (after whitespace normalization).
 * The comparison in test T2f uses .replace(/\s+/g, " ").trim() to handle JSX
 * multi-line whitespace collapsing.
 */
const F3_R3_E =
  "For the food domain at v0.2, the cross-model similarity basis is" +
  " the 12-model mode-coherent slate. One additional model" +
  " (meta-llama/llama-4-maverick) is in the corpus for this domain but" +
  " does not appear in the similarity basis because it has no single-pass" +
  " collection records for food. That model still contributes to its own" +
  " within-model output-distribution analysis and to the pooled term map." +
  " The Romney CCM eigenratio is 9.48 with a 95 percent bootstrap interval" +
  " of [4.91, 10.34] over B=500 model-resamples. The lower interval bound" +
  " crosses the 5.0 strong-consensus threshold, so the classification is" +
  " published as weak-consensus with the indeterminacy disclosed rather" +
  " than published as strong-consensus with a hidden uncertainty caveat." +
  " A separate open question on how to canonicalize the published" +
  " eigenratio against its bootstrap distribution is tracked under" +
  " FOOD-FIX-A2.";

// ---------------------------------------------------------------------------
// F3-V3 binding strings (CDA SME adjudication batch A, 2026-07-13).
// ANY edit to these constants requires a fresh CDA SME pass.
// Source: docs/status/2026-07-13-batchA-promotion-cda-sme-verdict.md ruling B.
// ---------------------------------------------------------------------------

/** F3-V3-C: food v0.3 eigenratio CI disclosure line. */
const F3_V3_C =
  "Romney CCM eigenratio 5.44, 95 percent bootstrap interval [2.75, 10.25], B=500. The interval crosses the 5.0 strong/weak threshold and the median replicate sits below it.";

/**
 * F3-V3-E: food v0.3 methodology footnote. Must match MethodologyPage id="food-v03-footnote"
 * paragraph text content verbatim (after whitespace normalization).
 */
const F3_V3_E =
  "For the food domain at v0.3, the cross-model similarity basis is the" +
  " 19-model approved slate. Two additional models present in the domain" +
  " corpus are outside the v0.3 approved slate: meta-llama/llama-4-maverick," +
  " which was outside the v0.2 mode-coherent similarity basis and is not" +
  " on the v0.3 curator-maintained slate, and claude-fable-5, which is" +
  " excluded from the batch A slate across all three domains under a" +
  " separate ruling on provider deployment-side output filtering. At v0.3" +
  " the approved-slate filter is applied to the record set before the" +
  " analysis pipeline runs, so records from off-slate models do not enter" +
  " the similarity basis, the model-level analyses, or the pooled term" +
  " map for this domain; the raw records remain in the corpus and are" +
  " visible on the collection-records and failures surfaces. This is a" +
  " scope change from v0.2, where only the similarity basis was" +
  " mode-filtered. The Romney CCM eigenratio is 5.44 with a 95 percent" +
  " bootstrap interval of [2.75, 10.25] over B=500 model-resamples. The" +
  " point estimate sits just above the 5.0 strong-consensus threshold," +
  " the median bootstrap replicate sits below it, and 66 percent of" +
  " replicates fall below the threshold. The classification is therefore" +
  " published as weak-consensus with the indeterminacy disclosed rather" +
  " than as strong-consensus with a hidden uncertainty caveat. A separate" +
  " open question on how to canonicalize the published eigenratio against" +
  " its bootstrap distribution remains tracked under FOOD-FIX-A2.";

// ---------------------------------------------------------------------------
// Minimal fixture helper for ContentArea
// ---------------------------------------------------------------------------

function makeModel(id: string): PublishedModel {
  return { model_id: id, provider: "fixture-provider", family: "fixture" } as PublishedModel;
}

function makeFoodDomain({
  overrideSet = true,
  smallNWarning = true,
  excludedModel = "meta-llama/llama-4-maverick",
}: {
  overrideSet?: boolean;
  smallNWarning?: boolean;
  excludedModel?: string | null;
} = {}): DomainExtended {
  // 12 mode-coherent models (in mds_coordinates) + optional excluded model in models list
  const coherentIds = Array.from({ length: 12 }, (_, i) => `fixture-model-${i}`);
  const allModels = excludedModel
    ? [...coherentIds, excludedModel].map(makeModel)
    : coherentIds.map(makeModel);

  const mdsCoordinates: Record<string, [number, number]> = {};
  for (const id of coherentIds) {
    mdsCoordinates[id] = [0, 0];
  }

  return {
    domain_slug: "food",
    analysis_version: "0.2",
    models: allModels,
    free_lists: {},
    mds_coordinates: mdsCoordinates,
    mds_uncertainty: {},
    similarity_matrix: Array.from({ length: 12 }, () => Array(12).fill(0.8)),
    similarity_ci: Array.from({ length: 12 }, () =>
      Array.from({ length: 12 }, () => [0.7, 0.9] as [number, number])
    ),
    consensus_score: 0.75,
    consensus_ci: [0.5, 0.9],
    consensus_type: "STRONG_CONSENSUS",
    consensus_type_override: overrideSet ? "WEAK_CONSENSUS" : null,
    consensus_type_override_reason: overrideSet
      ? "Point estimate is on the strong-consensus side of the 5.0 threshold; the 95 percent bootstrap interval crosses 5.0. We publish the conservative classification and disclose the indeterminacy rather than claim a category the uncertainty does not support."
      : "",
    sutrop_csi: {},
    cultural_centrality_scores: {},
    within_model_results: [],
    groundings: [],
    generated_lede: F3_R3_A,
    generated_at: "2026-06-11T00:00:00Z",
    romney_small_n_warning: smallNWarning,
    display: {
      r1_states: {},
      top_terms: {},
      top_terms_metric: "sutrop_csi",
    },
  } as unknown as DomainExtended;
}

// Minimal ContentArea props for Focus-3 rendering
const BASE_PROPS = {
  loading: false,
  error: null,
  selectedModelIds: new Set<string>(),
  onRemoveModel: () => {},
  activeVizTab: "mds-plot" as const,
  onVizTabChange: () => {},
  activeFocus: "focus-3" as const,
  onFocusChange: () => {},
  selectedModelId: null,
  onSelectModel: () => {},
  activeDomain: "food",
};

// ---------------------------------------------------------------------------
// T2: byte-identity assertions for F3-R3 binding strings
// ---------------------------------------------------------------------------

describe("PROMOTE-FOOD-V02 T2: F3-R3 binding string byte-identity", () => {
  // ---- T2a: CI_DISCLOSURE_TEXT_V02 constant (food v0.2, retained for citation stability) ----
  it("T2a: CI_DISCLOSURE_TEXT_V02 module constant is byte-identical to F3-R3-C (food v0.2)", () => {
    expect(CI_DISCLOSURE_TEXT_V02).toBe(F3_R3_C);
  });

  // ---- T2a-v3: CI_DISCLOSURE_TEXT_V03 constant (food v0.3 active surface) ----
  it("T2a-v3: CI_DISCLOSURE_TEXT_V03 module constant is byte-identical to F3-V3-C (food v0.3)", () => {
    expect(CI_DISCLOSURE_TEXT_V03).toBe(F3_V3_C);
  });

  // ---- T2b: SMALL_N_TEXT constant ----
  it("T2b: SMALL_N_TEXT module constant is byte-identical to F3-R3-D", () => {
    expect(SMALL_N_TEXT).toBe(F3_R3_D);
  });

  // ---- T2c: F3-R3-A rendered in ContentArea lede ----
  it("T2c: ContentArea renders generated_lede verbatim (F3-R3-A)", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeFoodDomain()}
      />
    );
    const lede = document.querySelector('p.chart-lede[aria-live="polite"]');
    expect(lede).not.toBeNull();
    expect(lede!.textContent).toBe(F3_R3_A);
  });

  // ---- T2d: F3-V3-C (CI_DISCLOSURE_TEXT_V03) rendered as CI disclosure paragraph ----
  // ContentArea.tsx now imports CI_DISCLOSURE_TEXT_V03 for all active override surfaces.
  it("T2d: ContentArea renders CI disclosure line verbatim (F3-V3-C / CI_DISCLOSURE_TEXT_V03) when override is set", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeFoodDomain({ overrideSet: true })}
      />
    );
    const disclosure = document.querySelector("p.content-area__ci-disclosure");
    expect(disclosure).not.toBeNull();
    expect(disclosure!.textContent).toBe(F3_V3_C);
  });

  // ---- T2e: F3-R3-D rendered as small-n warning paragraph ----
  it("T2e: ContentArea renders small-n warning verbatim (F3-R3-D) when romney_small_n_warning is true", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeFoodDomain({ smallNWarning: true })}
      />
    );
    const smallN = document.querySelector("p.content-area__small-n-line");
    expect(smallN).not.toBeNull();
    expect(smallN!.textContent).toBe(F3_R3_D);
  });

  // ---- T2f: F3-R3-E rendered in MethodologyPage ----
  it("T2f: MethodologyPage renders food-v02-footnote paragraph byte-identical to F3-R3-E", () => {
    render(<MethodologyPage />);
    const footnote = document.getElementById("food-v02-footnote");
    expect(footnote).not.toBeNull();
    // Compare normalized (collapse whitespace to handle possible wrapping)
    const actual = footnote!.textContent?.replace(/\s+/g, " ").trim() ?? "";
    const expected = F3_R3_E.replace(/\s+/g, " ").trim();
    expect(actual).toBe(expected);
  });

  // ---- T2f-v3: F3-V3-E rendered in MethodologyPage food-v03-footnote ----
  it("T2f-v3: MethodologyPage renders food-v03-footnote paragraph byte-identical to F3-V3-E", () => {
    render(<MethodologyPage />);
    const footnote = document.getElementById("food-v03-footnote");
    expect(footnote).not.toBeNull();
    // Compare normalized (collapse whitespace to handle possible wrapping)
    const actual = footnote!.textContent?.replace(/\s+/g, " ").trim() ?? "";
    const expected = F3_V3_E.replace(/\s+/g, " ").trim();
    expect(actual).toBe(expected);
  });

  // ---- T2g: CI disclosure absent when override is null ----
  it("T2g: CI disclosure paragraph absent when consensus_type_override is null", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeFoodDomain({ overrideSet: false })}
      />
    );
    expect(document.querySelector("p.content-area__ci-disclosure")).toBeNull();
  });

  // ---- T2h: small-n line absent when romney_small_n_warning is false ----
  it("T2h: small-n paragraph absent when romney_small_n_warning is false", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeFoodDomain({ smallNWarning: false })}
      />
    );
    expect(document.querySelector("p.content-area__small-n-line")).toBeNull();
  });

  // ---- T2i: override badge renders when override differs from consensus_type ----
  it("T2i: override badge renders when consensus_type_override differs from consensus_type", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={makeFoodDomain({ overrideSet: true })}
      />
    );
    const badge = document.querySelector("span.content-area__override-badge");
    expect(badge).not.toBeNull();
    expect(badge!.textContent).toBe("WEAK_CONSENSUS");
  });

  // ---- T2j: override badge absent when override matches consensus_type ----
  it("T2j: override badge absent when consensus_type_override matches consensus_type", () => {
    // Domain where override == consensus_type (no visible divergence to disclose)
    const domain = makeFoodDomain({ overrideSet: true });
    // Force both to the same value
    (domain as Record<string, unknown>).consensus_type_override = "STRONG_CONSENSUS";
    render(
      <ContentArea
        {...BASE_PROPS}
        domain={domain}
      />
    );
    expect(document.querySelector("span.content-area__override-badge")).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// T2 (em-dash guard): no U+2014 in any of the five binding strings
// ---------------------------------------------------------------------------

describe("PROMOTE-FOOD-V02/V03 T2: em-dash absence across binding strings (CLAUDE.md hard rule)", () => {
  const EM_DASH = "—";

  it("F3-R3-A contains no em-dash", () => {
    expect(F3_R3_A).not.toContain(EM_DASH);
  });

  it("F3-R3-C (CI_DISCLOSURE_TEXT_V02) contains no em-dash", () => {
    expect(CI_DISCLOSURE_TEXT_V02).not.toContain(EM_DASH);
  });

  it("F3-V3-C (CI_DISCLOSURE_TEXT_V03) contains no em-dash", () => {
    expect(CI_DISCLOSURE_TEXT_V03).not.toContain(EM_DASH);
  });

  it("F3-R3-D (SMALL_N_TEXT) contains no em-dash", () => {
    expect(SMALL_N_TEXT).not.toContain(EM_DASH);
  });

  it("F3-R3-E contains no em-dash", () => {
    expect(F3_R3_E).not.toContain(EM_DASH);
  });

  it("F3-V3-E contains no em-dash", () => {
    expect(F3_V3_E).not.toContain(EM_DASH);
  });

  it("FABLE_DISCLOSURE_FRAMING contains no em-dash", () => {
    expect(FABLE_DISCLOSURE_FRAMING).not.toContain(EM_DASH);
  });

  it("FABLE_DISCLOSURE_BOUND contains no em-dash", () => {
    expect(FABLE_DISCLOSURE_BOUND).not.toContain(EM_DASH);
  });
});

// ---------------------------------------------------------------------------
// T3: Heatmap maverick-drop disclosure assertion
// ---------------------------------------------------------------------------

describe("PROMOTE-FOOD-V02 T3: heatmap maverick-drop disclosure (DESIGN_SYSTEM.md §23.3)", () => {
  it("T3a: renders one exclusion caption when one model is absent from mds_coordinates", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        activeVizTab="similarity"
        domain={makeFoodDomain({ excludedModel: "meta-llama/llama-4-maverick" })}
      />
    );
    const captions = document.querySelectorAll("p.heatmap-exclusion-caption");
    expect(captions.length).toBe(1);
  });

  it("T3b: exclusion caption text names the excluded model (displayModel strip)", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        activeVizTab="similarity"
        domain={makeFoodDomain({ excludedModel: "meta-llama/llama-4-maverick" })}
      />
    );
    const caption = document.querySelector("p.heatmap-exclusion-caption");
    expect(caption).not.toBeNull();
    // displayModel("meta-llama/llama-4-maverick") strips to "llama-4-maverick"
    expect(caption!.textContent).toContain("llama-4-maverick");
    expect(caption!.textContent).toContain(
      "is not shown in the similarity matrix because it has no single-pass collection records for this domain."
    );
  });

  it("T3c: exclusion caption aria-label carries the full model_id", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        activeVizTab="similarity"
        domain={makeFoodDomain({ excludedModel: "meta-llama/llama-4-maverick" })}
      />
    );
    const caption = document.querySelector("p.heatmap-exclusion-caption");
    expect(caption).not.toBeNull();
    expect(caption!.getAttribute("aria-label")).toContain("meta-llama/llama-4-maverick");
    expect(caption!.getAttribute("aria-label")).toContain(
      "is not shown because it has no single-pass collection records for this domain."
    );
  });

  it("T3d: no exclusion captions when all models appear in mds_coordinates", () => {
    render(
      <ContentArea
        {...BASE_PROPS}
        activeVizTab="similarity"
        domain={makeFoodDomain({ excludedModel: null })}
      />
    );
    const captions = document.querySelectorAll("p.heatmap-exclusion-caption");
    expect(captions.length).toBe(0);
  });

  it("T3e: exclusion captions absent on non-heatmap tabs", () => {
    // captions are inside the similarity tab; should not appear on mds-plot
    render(
      <ContentArea
        {...BASE_PROPS}
        activeVizTab="mds-plot"
        domain={makeFoodDomain({ excludedModel: "meta-llama/llama-4-maverick" })}
      />
    );
    const captions = document.querySelectorAll("p.heatmap-exclusion-caption");
    expect(captions.length).toBe(0);
  });

  it("T3f: multiple excluded models produce one caption each", () => {
    const domain = makeFoodDomain({ excludedModel: null });
    // Manually add two excluded models
    (domain as Record<string, unknown>).models = [
      ...((domain as Record<string, unknown>).models as PublishedModel[]),
      makeModel("excluded-a"),
      makeModel("excluded-b"),
    ];
    render(
      <ContentArea
        {...BASE_PROPS}
        activeVizTab="similarity"
        domain={domain}
      />
    );
    const captions = document.querySelectorAll("p.heatmap-exclusion-caption");
    expect(captions.length).toBe(2);
  });
});

// ---------------------------------------------------------------------------
// T4: FableDisclosureNote byte-identity coverage (batch A, DESIGN_SYSTEM.md §19.20)
// ---------------------------------------------------------------------------

describe("Batch A T4: FableDisclosureNote constant byte-identity (DESIGN_SYSTEM.md §19.20)", () => {
  /** BA-FABLE-FRAMING (binding, CDA SME ruling E). */
  const BA_FABLE_FRAMING =
    "The claude-fable-5 counts shown on this panel are a product of the" +
    " mechanism described immediately below.";

  /** Fable-5 bound string (binding, 2026-07-10 (d), CDA SME ruling E). */
  const FABLE_BOUND =
    "The provider's deployment-side output filter returned empty content" +
    " (stop_reason=refusal) for 22 of 23 free-list elicitation attempts on" +
    " claude-fable-5 in batch A. Under identical prompts collected the same hour," +
    " claude-opus-4-8 and claude-sonnet-5 completed the same elicitations with zero" +
    " refusals. The pattern is a property of claude-fable-5's deployment configuration," +
    " not of its training corpus, and does not license any claim about" +
    " claude-fable-5's categorical structure for family or holidays.";

  it("T4a: FABLE_DISCLOSURE_FRAMING is byte-identical to BA-FABLE-FRAMING bound string", () => {
    expect(FABLE_DISCLOSURE_FRAMING).toBe(BA_FABLE_FRAMING);
  });

  it("T4b: FABLE_DISCLOSURE_BOUND is byte-identical to 2026-07-10 (d) bound string", () => {
    expect(FABLE_DISCLOSURE_BOUND).toBe(FABLE_BOUND);
  });
});

// ---------------------------------------------------------------------------
// T5: BA-QA-FN methodology section coverage (batch A, DESIGN_SYSTEM.md §6.1)
// ---------------------------------------------------------------------------

describe("Batch A T5: BA-QA-FN methodology section (DESIGN_SYSTEM.md §6.1)", () => {
  it("T5a: MethodologyPage renders Informant-class QA calibration section heading", () => {
    render(<MethodologyPage />);
    const heading = document.getElementById("informant-class-qa-calibration-heading");
    expect(heading).not.toBeNull();
    expect(heading!.textContent).toBe("Informant-class QA calibration");
  });

  it("T5b: BA-QA-FN paragraph contains 'reasoning-model informants' and 'dense-tokenizer informants'", () => {
    const { container } = render(<MethodologyPage />);
    const text = container.textContent ?? "";
    expect(text).toMatch(/reasoning-model informants/i);
    expect(text).toMatch(/dense-tokenizer informants/i);
  });

  it("T5c: BA-QA-FN paragraph contains 'approved slate' cross-reference sentence", () => {
    const { container } = render(<MethodologyPage />);
    const text = container.textContent ?? "";
    expect(text).toContain("QA answers whether a record is fit for analysis");
    expect(text).toContain("the approved slate, curated separately, answers which models the published basis includes");
  });
});
