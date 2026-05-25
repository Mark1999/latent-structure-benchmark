# Frontend Redesign Brainstorm — 2026-05-25

**Status:** Brainstorming. No code changes yet. Mark is building a PowerPoint mockup.

---

## The problem

The current dashboard leans too heavily toward the academic side — both in writing and in visual style. It's difficult to read. The typography is flat (Lato for everything, no hierarchy). The visualizations were MVP functional, not polished. Now that Phase 9a added 6 new viz types (Term Map, Cluster Tree, Pile Structure, Centrality, plus the original MDS/Heatmap/Free Lists), the dashboard needs a design pass that makes it readable and engaging for a broader audience.

---

## Decision 1: Typography — Sans-Serif Only

Mark ruled out serif fonts (they read as "academic journal"). Three sans-serif combos were previewed at `docs/type-specimen-preview.html`:

| Combo | Display | Body | Mono | Character |
|---|---|---|---|---|
| **A** | Plus Jakarta Sans | Source Sans 3 | IBM Plex Mono | Bold geometric display + crisp UI body. Two-font hierarchy. |
| **B** | DM Sans (unified) | DM Sans | IBM Plex Mono | Single font for everything. Clean, warm geometric. Simplest stack. |
| **C** | Instrument Sans | General Sans | IBM Plex Mono | Narrow/compact display + wider body. Confident, space-efficient. |

All three replace Lato (body) and JetBrains Mono (data). IBM Plex Mono is narrower than JetBrains — better for dense numeric data in tooltips and tables.

**Decision needed:** Pick one combo. Preview is at `localhost:8888/type-specimen-preview.html` (run `python3 -m http.server 8888 --directory docs` to serve it).

---

## Decision 2: Slicer Model — Editorial, Not Universal

### The insight

We don't have to be everything to everyone. The raw data is available (HuggingFace, Zenodo, CC0 license). Anyone who wants to slice the data differently can download the open bundle and do it themselves. The dashboard is a **curated magazine**, not an exhaustive pivot-table explorer.

### The slicer hierarchy

Two natural comparison modes emerged:

**Mode 1 — Within-Provider:** "How do OpenAI's models differ from each other?"
- Pick a provider, see all their models side-by-side
- Shows internal consistency — does the flagship organize terms the same way the small model does?

**Mode 2 — Cross-Provider by Tier:** "How do the flagships compare to each other?"
- Pick a tier, compare across providers
- Shows the competitive landscape at each size class

### The data hierarchy

```
Provider (slicer 1 — who made it)
  └── Anthropic
        ├── claude-opus-4-6      [flagship]
        ├── claude-opus-4-5      [flagship]
        └── claude-sonnet-4-6    [mid]
  └── OpenAI
        ├── gpt-5.4              [flagship]
        └── gpt-5.4-mini         [small]
  └── Meta
        └── llama-4-maverick     [open, mid]
  └── Google
        └── gemini-2.5-pro       [flagship]
  └── xAI
        └── grok-4               [flagship]
  └── Mistral
        ├── mistral-large-2512   [flagship]
        └── mistral-small-2603   [small]
  └── DeepSeek
        └── deepseek-v3.2        [open, flagship]
  └── Microsoft
        └── phi-4                [open, small]
```

### Proposed slicers (Power BI style)

| Slicer | Type | Values |
|---|---|---|
| **Domain** | Page-level nav (stays as-is) | Family, Holidays, Food |
| **Provider** | Multi-select checkboxes | Anthropic, OpenAI, Meta, Google, xAI, Mistral, DeepSeek, Microsoft |
| **Tier** | Filter chips | Flagship, Mid, Small |
| **Open weights** | Toggle | Yes / No / All |

The two comparison modes emerge from how you use the slicers:
- **Within-provider:** select one provider, all tiers → see that provider's lineup
- **Cross-provider at tier:** select all providers, one tier → see flagships head-to-head

### Schema implication

`model_tier` (flagship / mid / small) is not in the schema today. It's implicit in the model names but would need to be added as a field on `ModelRef` or as a display-layer mapping. This is a small change.

---

## Decision 4: Forward-Looking Comparison Dimensions (2026-05-25)

Mark is thinking ahead to two axes that don't exist in the data yet but should shape the slicer design:

### Timeline behavior (refined 2026-05-25, with ghost comparison)

The timeline at the bottom is NOT a multi-lane view of all providers. It shows **one family at a time**, driven by whatever provider/family the user has selected or is focused on in the left panel. If you expand Anthropic → Claude in the slicer, the timeline shows the Claude version history. If you switch to OpenAI → GPT, the timeline updates to show the GPT version history. It's a detail view, not an overview.

**Ghost comparison (2026-05-25):** When viewing one family's timeline, the user can optionally see a "ghost" of another family's releases overlaid at reduced opacity (20-30%). This allows temporal comparison — "GPT-5.2 came out before Claude opus-4-5" — without cluttering the primary view. The ghost is the previously-viewed family (automatic) or explicitly toggled via a compare icon next to each provider in the left panel.

Ghost rendering:
- Dots: 25% opacity, smaller (10px vs 16px), provider's color
- Connector: dashed, 15% opacity
- Labels: 30% opacity, slightly smaller font
- No click interaction on ghost dots (they're for reference only)
- Only one ghost at a time

### Axis 1 — Version drift within a lineage

Claude Opus 4.5 → 4.6 → 4.7. Same provider, same family, different training cut. Does the categorical structure shift between versions? The schema already supports this (`model_version_returned`, `release_date`). Requires multiple collection campaigns over time (Phase 5+ plan). The slicer implication: a "version timeline" view within a provider/family, not just a static snapshot.

### Axis 2 — Architecture class comparison

LLM vs. world model vs. neurosymbolic vs. whatever comes next. The CDA protocol is architecture-agnostic — it gives any system a free-list prompt, gets a response, measures the structure. A neurosymbolic system that produces a pile sort is just another informant. The methodology doesn't care what's inside the box.

This implies a future top-level slicer dimension: `architecture_class` (transformer-LLM / world-model / neurosymbolic / hybrid). For now all models are LLMs, so this level is invisible. It becomes visible the day we collect from a non-LLM system.

### The full future hierarchy

```
Architecture Class (LLM / World Model / Neurosymbolic)  ← future, collapsed for v1
  └── Provider (Anthropic / OpenAI / Meta / ...)
        └── Family (Claude / GPT / Llama / ...)
              └── Version (timestamped snapshots over time)
```

### Design implication

Design the slicer layout with an expandable top level, even if it's collapsed for v1. The cost of this is zero (it's just a data structure that has room for one more level). The cost of NOT doing it is a redesign when the first non-LLM system enters the benchmark.

---

## Decision 3: Dashboard Posture

**The dashboard is a magazine that uses research methods, not a research tool that has a website.**

This is the same framing as ARCHITECTURE.md §1 ("LSB is a website that uses research methods, not a research project that has a website") applied specifically to the dashboard. It means:

- **Pick the 3-4 most interesting views** and make them excellent, rather than building 12 mediocre ones
- **Write editorial introductions** that guide the reader, not just display data
- **The open data bundle is the escape valve** — anyone who wants different cuts can build them
- **Fewer controls, more storytelling** — the slicers are opinionated, not exhaustive
- **Visual polish matters** — this is the thing people see, not the methodology page

### What this means for Phase 9a views

The 8-tab VizSwitcher (MDS Plot | Term Map | Cluster Tree | Free Lists | Similarity | Centrality | Pile Structure | Drift) may be too many tabs. Not all views are equally interesting to a general audience. Consider:

- **Keep prominent:** Term Map, Pile Structure, Centrality (these tell the most accessible stories)
- **Keep but de-emphasize:** MDS Plot, Similarity Heatmap (more technical)
- **Consider folding:** Cluster Tree could be a sub-view of Term Map (show/hide dendrogram)
- **Defer:** Free Lists (already visible), Drift (no longitudinal data yet)

This is a design decision, not a code decision. Mark to decide.

---

## Decision 5: Page Layout — No-Scroll Landing + Tab Architecture (2026-05-25)

### The landing page principle

**Everything above the fold. No scrolling to understand what this is.** The landing page is the MDS plot + slicers. Once someone understands the gist of the project (a one-time thing), they just want to start slicing. The home page is the entry point to exploration, not an essay to read.

### Layout: landing page

```
┌─────────────────────────────────────────────────────┐
│  [Site name / logo]                    [Nav tabs →]  │
│                                                      │
│  ┌──────────┐  ┌────────────────────────────────┐   │
│  │ Slicers  │  │                                │   │
│  │          │  │         MDS Plot                │   │
│  │ Provider │  │    (the hero visual)            │   │
│  │ □ Anthr. │  │                                │   │
│  │ □ OpenAI │  │    Stress = 0.12               │   │
│  │ □ Meta   │  │                                │   │
│  │ ...      │  └────────────────────────────────┘   │
│  │          │  ┌─ Viz tabs ─────────────────────┐   │
│  │ Tier     │  │ MDS | Terms | Tree | Piles | … │   │
│  │ ○ Flag.  │  └────────────────────────────────┘   │
│  │ ○ Mid    │                                        │
│  │ ○ Small  │  One-line lede with Smith's S + CI     │
│  │          │                                        │
│  │ Open wt. │                                        │
│  │ [toggle] │                                        │
│  └──────────┘                                        │
└─────────────────────────────────────────────────────┘
```

### Nav tabs (top-level, not viz tabs)

Two tiers of navigation:

**Top-level nav (site sections):**
- **Explore** — the dashboard itself (landing page, slicers, viz tabs)
- **Methodology** — how LSB works, protocol details, limitations
- **Data** — links to open bundle, HuggingFace, Zenodo, citation info

These are the site's main sections. "Explore" is the default/home.

**Viz tabs (within Explore):**
- MDS Plot (default — hero visual)
- Term Map
- Cluster Tree
- Pile Structure
- Centrality
- Similarity
- Free Lists

These switch the visualization within the explore view. The slicers persist across tab switches.

### Tooltips: opt-in educational layer

A global **"Show tooltips" toggle** (probably in the nav bar or as a small ? icon). When enabled:

- Rolling over technical terms, chart elements, or measures shows a pithy plain-English explanation
- Examples:
  - **Stress = 0.12** → "How well the 2D map preserves the original distances. Lower is better. Below 0.15 is a good fit."
  - **Smith's S = 0.81** → "How much models agree on the structure of this domain. 1.0 = perfect agreement, 0.0 = no shared pattern."
  - **95% CI [0.65–0.95]** → "If we repeated this with different model samples, 95% of the time the score would fall in this range."
  - **Bootstrap support 58%** → "This grouping appeared in 58% of resampled analyses. Below 70% = treat with caution."
  - **Cultural centrality** → "How typical this model's categorical structure is compared to the group. Not a quality score."

When tooltips are off, the UI is clean — just data and labels. Power users turn them off after their first visit. New visitors turn them on.

This is a much better approach than trying to write explanatory paragraphs everywhere. The explanation is available exactly where you need it, exactly when you need it, and invisible otherwise.

---

## Decision 6: Prototype Feedback — Live Notes (2026-05-25)

Mark reviewed `docs/slicer-prototype.html` and gave the following feedback:

### Domain selector: move to left panel as dropdown, not pills in nav

**Problem:** Domain pills (Family / Holidays / Food) are in the upper-right nav bar. But domains will grow over time — many more domains, possibly with categories and subcategories (e.g., "Medical" → various tests/domains underneath). Pills in the nav bar don't scale.

**Fix:** Domain selection moves to the left slicer panel, at the top, as a dropdown menu. This is the first thing you pick — it determines everything below it. The dropdown should support hierarchical categories in the future:
```
Domain (dropdown)
  ├── Family
  ├── Holidays  
  ├── Food
  └── Medical (future category)
        ├── Symptom recognition
        ├── Treatment terminology
        └── ...
```

### Nav tabs: move Explore / Methodology / Data to upper-right

**Fix:** The three site sections (Explore, Methodology, Data) move to the upper-right corner of the nav bar where the domain pills were. This is more conventional placement for site navigation.

### Tier slicer: rethink

**Problem:** "All / Flagship / Mid / Small" assumes every provider divides models into these tiers. Not all do. Some providers have one model. Some have a different internal hierarchy. The tier taxonomy may not be universal.

**Open question:** Is "tier" even the right cross-cutting dimension? Alternatives:
- **Parameter count range** (>100B / 10-100B / <10B) — more objective but not always public
- **Provider's own positioning** (top-tier / mid-tier / lightweight) — but naming varies
- **Just remove the tier slicer** and let people use the provider tree to select what they want

Mark to decide. If tier stays, it needs to be flexible enough to handle providers that don't follow the flagship/mid/small pattern.

### Timeline: model releases, not collection dates

**Problem:** The timeline at the bottom shows when LSB collected the data (Apr 22, May 05, May 08). Nobody cares when we collected it. What's interesting is the **model release timeline** — when each version of a model was released.

**Fix:** The timeline becomes a model version slider:
```
GPT-1 ──── GPT-2 ──── GPT-3 ──── GPT-3.5 ──── GPT-4 ──── GPT-5.4
                                                              ▲
                                                         [current]
```

This enables the version-drift view: "How did OpenAI's categorical structure change from GPT-4 to GPT-5?" The slider scrubs through time and the visualization updates to show the selected model version at that point.

**Implication:** This requires `release_date` (which we have) and ideally a lineage field connecting model versions within a family (GPT-5.4 is the successor to GPT-4, etc.). The lineage isn't in the schema today.

### Provider/model tree: approved

**What works:** The left panel with expandable provider groups (chevrons → family label → individual model checkboxes with dates and badges). Mark approved this layout. Keep it.

---

## Open items

## Decision 7: Term Map Interaction Design (2026-05-25)

### The approach (synthesized from research + Mark's feedback)

**Default view:** Colored semi-transparent convex hulls around each cluster, with cluster name as prominent callout. Individual terms shown as small dots, no term labels. This reads clean at a glance.

**Hover a cluster hull:** The terms within that cluster "explode" outward from their centroid (fisheye/force-repulsion animation), spreading just enough to read individual term labels. Terms spring back on mouse-out. This is the cluster explosion pattern (Furnas 1986).

**Hover a single dot (at any zoom):** Tooltip with term name, cluster, coordinates.

**Cluster callouts:** Large, prominent labels positioned at the hull boundary or in nearby whitespace. These are the primary readable elements at the default zoom. Styled like the coffee MDS reference — large bold text in cluster color.

**Term Map is the hero tab** — shows first when someone lands on the page.

### Research findings (from agent)

Best approaches for 100 items / 19 clusters on web SVG:
1. **Convex hulls + cluster labels** as default — reduces 100 labels to 19
2. **D3 force-directed label nudging** when showing individual labels (only 5-8 per cluster)
3. **Fisheye/cluster explosion on hover** — spreads clustered dots to resolve label collisions
4. **OWID pattern** — unlabeled dots at rest, labels on hover
5. **Avoid**: ANTHROPAC-style stamp-all-labels (unreadable at 30+), full callout lines at 100 items

### Prototype status (2026-05-25)

The hover-explode interaction is working in `docs/slicer-prototype.html`. Tested with real family domain data (100 terms, 19 clusters). Key findings:
- Convex hulls with cluster labels work well as the default overview
- Hover-explode successfully spreads dense clusters (e.g., 6 "Immediate Family" terms) into readable positions with labels
- Non-hovered clusters fade to ~15% opacity, providing strong visual focus
- Terms animate back to original positions on mouse-out (0.2s ease)

### Chart sizing strategy (2026-05-25)

Don't fight the viewport height. Instead:
1. **Zoom:** D3-zoom (scroll wheel / pinch). Chart renders at whatever size the viewport gives it; zoom handles the rest.
2. **Semantic zoom:** As user zooms in, term labels progressively appear when there's enough pixel space. At default zoom, only cluster hull labels show.
3. **Fisheye burst:** Hover a cluster or dense area → dots spread and labels appear, even without zooming.
4. **First-visit tooltip:** "Scroll to zoom, hover clusters to explore" — dismissable.

This eliminates the "cramming 100 labels into a viewport" problem entirely.

### Polish needed (future iteration)
- D3-zoom integration (scroll wheel / pinch)
- Semantic zoom: labels appear/disappear based on zoom level
- Cluster labels collide in dense areas — need label collision avoidance for the 19 labels themselves
- Hover should trigger on dots too, not just hull paths
- Cluster label aggregation is imperfect (CDA SME A2 advisory) — e.g., "Cousin Relationships" label on the grandparent cluster
- Explosion strength (25px) could be adaptive based on cluster density
- First-visit tooltip for zoom hint

### Not using
- Flavor wheel / radial layout (Mark dropped this)
- Full callout leader lines at 100 items (too noisy)
- Semantic zoom (loses spatial context)

---

## Open items

- [ ] Mark to pick a type combo (A, B, or C)
- [ ] Mark to finish PowerPoint mockup of slicer layout
- [ ] Add `model_tier` field to schema or display-layer mapping
- [ ] Mark to decide which views are "magazine front page" vs. "deep dive"
- [ ] Mark to write new introductory copy (he mentioned this at session start)
- [ ] §1.5 amendment needed if the site intro reads warmer than §1.5 currently allows

---

## Reference

- Type specimen preview: `docs/type-specimen-preview.html`
- Phase 9a kickoff: `docs/status/2026-05-24-phase9a-viz-gap-kickoff.md`
- Current design system: `DESIGN_SYSTEM.md` v0.5.2
- Frontend designer briefs: `docs/FRONTEND_DESIGNER_BRIEF.md` + `_APPENDIX.md`
- Phase 9 planning notes: `docs/PHASE_9_PLANNING_NOTES.md`

---

*End of brainstorm. Resume with: "Let's pick up the frontend redesign" or "I have the PowerPoint mockup."*
