# LSB Frontend Designer Brief — Appendix: Aesthetic context

**Document name:** `docs/FRONTEND_DESIGNER_BRIEF_APPENDIX.md`
**Version:** v0.2 (CDA SME advisory §1 polarity tag applied 2026-05-17; §3a and §4 deferred to Mark)
**Status:** Opinionated, not doctrinal. Treat everything here as a recommendation, not a binding constraint.
**Companion:** `docs/FRONTEND_DESIGNER_BRIEF.md` (the doctrinal brief — CDA SME approved at v0.2)

---

## 0. What this file is, and what authority it has

The companion `FRONTEND_DESIGNER_BRIEF.md` is the doctrinal layer: methodology framing, forbidden vocabulary, accessibility floor, R10 binding, codebase map. Every word of it has been reviewed for methodology correctness by the CDA SME agent. It tells you what you *cannot* do.

This appendix is the taste layer. It tells you what I think you *should* do — based on having shipped the Phase 6 minimum-viable build and having absorbed the project's posture over many sessions. It is **not** binding. Mark may disagree with every word here; if he does, his word wins. The designer who comes after me may have better taste than I do; if they do, theirs wins.

The doctrinal brief was written for a future AI agent. This appendix is written more like a designer-to-designer handover note: opinions, concrete references, things I'd reach for first, things I'd avoid. Read it once, take what's useful, ignore the rest.

---

## 1. The reference set (study these first)

These publications get the article-with-explorer posture right. Spend an hour with each before sketching anything.

### Tier 1 — closest to LSB's posture

- **Our World in Data** ([ourworldindata.org](https://ourworldindata.org)).
  The North Star. Read three long-form pieces end to end — Hannah Ritchie's energy and climate pieces are especially good. Notice: dense typography, generous whitespace, every chart has a visible source line, every claim has an inline citation, the "embed this chart" affordance treats charts as primary objects. The chrome is almost invisible.
  Specifically study: the article header treatment, the lede-then-chart rhythm, the inline footnote affordance, the citation block at the foot of each article, the data table that always sits below each chart.

- **The Pudding** ([pudding.cool](https://pudding.cool)).
  Visual essays with serious data work. Read "How Bad is Your Spotify?" and "Where Should I Live?" for two different scrollytelling rhythms. They're more playful than LSB should be — borrow the typographic intent, not the playfulness. The Pudding's careful attention to sequencing (you read one thing at a time, the chart is in the same eye-line as the prose that explains it) is the thing to steal.

- **NYT Upshot / Graphics desk.**
  For gravitas-of-a-research-piece, look at almost anything by Kevin Quealy, Claire Cain Miller, Margot Sanger-Katz. The Upshot's posture — sober, declarative, careful about uncertainty — is exactly what LSB wants in copy and chrome.

### Tier 2 — pick selectively

- **Distill.pub** (archived 2021).
  ML explainability done well. They cared about interaction polish in a way most academic publishing doesn't. Their typography is dense and their charts are precise. Worth studying for the failure modes — Distill articles sometimes felt too dense for casual readers; LSB needs to land in between Distill and OWID.

- **FiveThirtyEight** (pre-Disney shutdown).
  The Nate Silver-era voice — methodologically transparent commentary. The forecasting articles are useful prior art for how to talk about uncertainty without making a reader's eyes glaze over.

- **Reuters Graphics.**
  Typographic restraint and sober color. Especially good for charts that need to read on small screens. Look at any of their long-form data pieces (e.g., COVID, migration).

- **The Economist / 1843.**
  For the typographic seriousness. Less directly relevant since they lean on photography for hero treatments and LSB doesn't have that affordance.

### Tier 3 — adjacent but useful

- **MIT Technology Review's long-form pieces** — for typographic gravitas in tech-adjacent content.
- **Quanta Magazine** — for science writing that doesn't condescend.
- **Stripe Press books** (the book aesthetic, not the SaaS product).

---

## 2. The anti-reference set (do not look at these for inspiration)

These are the wrong genre. Looking at them too long will pull LSB in a direction that breaks the posture.

- **SaaS landing pages of any kind** — Stripe, Linear, Notion, Vercel. LSB is not a product. There is nothing to sign up for.
- **Most LLM benchmark sites** — LMSYS Arena, OpenLLM Leaderboard, Artificial Analysis. They look like spreadsheets glued to a header. LSB explicitly is not that, and reading copy that says "the best model is X" trains the wrong instincts. (Mark's directive: "failures are findings" — that posture is incompatible with leaderboard framing.)
- **Anthropic, OpenAI, Google AI marketing pages** — aspirational, soft, brand-first. Wrong tone.
- **HuggingFace's Spaces / model cards UI** — too playful, too gamified, too crowded with widgets.
- **Material Design dashboards** — wrong language. The tile grid, FABs, snackbars, etc. signal "operations console" not "research piece."
- **Bloomberg terminal-style density.** Tempting because it signals "serious," but it's the wrong serious. LSB is a magazine article that contains data, not a data product that has prose.

---

## 3. Typography — concrete shortlist

The current build uses generic system serifs (`Georgia, Times, serif`) and the default sans stack. This is a defensible floor but the single biggest taste win is here. A real type pairing lifts the whole posture immediately.

### Body (serif)

| Family | License | Notes |
|---|---|---|
| **Source Serif 4** | OFL (free) | My recommended pick if budget is zero. Adobe-engineered, broad weight range, excellent on-screen rendering, OWID-adjacent feel. |
| **Charter** | OFL (free) | Workhorse alternative; web-safe; reads especially well on lower-DPI screens. A bit more "academic publishing" than Source Serif. |
| **Lyon Text** | Commercial Type, paid | What NYT uses for some long-form. Beautiful but expensive. |
| **Mercury Text** | Hoefler & Co., paid | NYT's primary body face. The reference standard for newspaper-on-web typography. |
| **GT Sectra** | Grilli Type, paid | Used widely in serious editorial design. Distinctive (those flared terminals); strong personality. |

### UI / chart axes / captions (sans)

| Family | License | Notes |
|---|---|---|
| **Inter** | OFL (free) | Workhorse pick. Ubiquitous, well-engineered, paired with almost any serif. Safe and good. |
| **GT America** | Grilli Type, paid | Pairs cleanly with Sectra. More distinctive than Inter. |
| **Söhne** | Klim Type Foundry, paid | What NYT graphics use. Excellent for chart contexts. |
| **National 2** | Klim Type Foundry, paid | Slightly warmer than Söhne; broader weight range. |

### Pairings I'd reach for first

1. **Source Serif 4 body + Inter UI** — zero-budget, immediate gravitas lift, no licensing friction. This is the pragmatic default.
2. **GT Sectra body + GT America UI** — if Mark has budget, the most "OWID-grown-up" pairing.
3. **Lyon Text body + Söhne UI** — NYT-adjacent.

### Avoid

- **Roboto** — signals "Material Design product," wrong genre.
- **Open Sans** — generic, doesn't carry gravitas.
- **Helvetica / Arial** — too cold for this work; LSB is not Swiss-style.
- **Comic / display faces of any kind** — obviously.

### Numerals

Use **tabular (monospaced) figures** in every chart context. Confidence intervals shifting horizontally because of proportional figures is a small but persistent irritation. Most of the recommended faces have tabular figure variants — turn them on.

---

## 4. Color posture

The current Phase 6 palette is functional but reads as "data viz default."

### What I'd change

- **Background.** Move from pure white (`#ffffff`) to a warm off-white. OWID uses something like `#F8F4EC`; NYT pieces use slight cream tints. This single change makes the page read as "publication," not as "app." Caveat: every chart palette must be re-verified for contrast against the new background — keep the WCAG AA floor binding.

- **Body text.** Move from `#2c3e50` (cool slate) to a warm dark gray like `#1F1B16` or `#2A2520`. The cool tint reads "tech blog"; warm reads "editorial."

- **Model qualitative palette.** The current 11-hue palette is colorblind-safe but the blues are over-saturated. A muted version (lower saturation, more matched perceptual lightness) reads as more serious without losing distinguishability. Reference: Color Brewer 2.0 "Set 3" or "Dark 2" palettes; OWID's own qualitative palette.

- **Heatmap sequential.** Current 5-stop scale (`#eaf0f8` → `#1a3a5c`) is OK but the highest stop reads as "navy"; the lowest stop reads as "ice." Consider a slightly warmer ramp — e.g., starting from off-white at the bottom and approaching a deep teal or oxblood at the top, depending on what the rest of the chrome looks like.

- **Accent colors.** Reserve a single bold accent for the primary call (`--color-info` currently navy `#3360a9`). Don't add a second equally-bold accent; the page gets noisy fast. For "warning" / "no bootstrap interval available" states, use a muted ochre rather than a saturated yellow — yellow reads as alarm.

### What I wouldn't change

- The fact that color is used to *encode data*, not to decorate. Phase 6 got this right. Don't add brand colors to chrome that don't carry information.
- The `--color-text-caption` (`#6c757d`, 4.60:1) is doing real work for 12px regular weight text. Don't lose it.
- The model-7 through model-11 hues were picked carefully to maintain hue-distance after the 11-model slate landed. If you re-tune the palette, preserve the distinguishability constraint (rough rule of thumb: any two adjacent series must be distinguishable at full saturation in monochrome).

---

## 5. Page architecture

The current Phase 6 architecture is correct in shape — domain picker → article header → lede → explorer → failures section. Where I'd push:

### Article column

- **Width: 600–720px** of body text. Current build uses 780px which is workable but a touch wide for comfortable reading rhythm.
- **Charts may break out** to wider widths with horizontal rules or a slight indent. OWID does this well — the prose column is narrow, the charts are wider, the boundary is signaled by typography.
- **Margins should feel generous.** White space is currency. The page should not feel "filled."

### Chrome

- **One header bar.** No sidebar. No breadcrumbs. No persistent toolbar. The chrome's job is to identify the publication, not to scaffold navigation.
- **No sticky header** on desktop unless it's *extremely* minimal. (The current build doesn't have one — keep it that way.)
- **No footer "sitemap."** A single small footer with: citation suggestion, link to open data bundle, link to GitHub, Mark's contact. Maybe a one-line "About" link. That's it.

### The lede strip

- **Headline ≠ marketing.** Headlines describe what was measured, not what the reader should feel. "Across N models, food vocabulary is organized around a shared categorical structure" is the right register. "Stunning convergence in food vocabulary across leading AI models" is not.
- **The CI in parentheses is a feature, not clutter.** It signals to the reader (and especially to a journalist) that the number has uncertainty. The current `KeyFinding.tsx` does this; preserve it.
- **Pull-quote treatment** is appropriate for the lede if you want to give it visual weight — large serif, generous leading, indent. NYT Upshot uses this occasionally.

### The "explore the data" affordance

- The current `DataExplorer` is a tabbed widget below the lede. It works.
- OWID's equivalent is more explicit — usually a section heading like "Explore the data" or a downward-pointing visual cue.
- I'd consider: instead of a tab bar, a sequential reading rhythm — "First, the map (MDS). Now, term-by-term (Free List). Now, pairwise similarity (Heatmap)." Each section gets its own subheading. The reader scrolls through them rather than tab-switching. This is more Pudding than OWID, and it might be wrong for LSB — judgment call.

### The failures-as-findings section

- **Treat it visually like a Limitations section in a paper, not a defect log.** Sober part of the page, located after the explorer, before the citation block.
- **Don't add warning iconography.** No yellow triangles, no red banners. These are findings, not errors. The §1.5 binding talks about *attributing intent* — visual semantics that say "warning" or "problem" come close to that boundary.
- **Decline-interview follow-ups should read like quoted material in a science article.** Block-quoted, attributed by model and version. Not chat-style bubbles. Not screenshots.
- **Refusal rate could be a small inline chart per model per domain** if the data supports it, BUT — check with CDA SME first. Quantifying refusals as a rate invites comparisons ("Model X refuses more than Model Y") that may need methodological framing.

---

## 6. Tone of voice

This is the easiest place to sound wrong. A few concrete rules I'd apply:

### Dos

- **First-person plural** ("we measure," "we ran the protocol," "we report"). It's neutral and avoids both passive voice and a fictitious "the LSB team."
- **Past tense for the protocol; present tense for the data** ("We ran 12 models through the free-list protocol. The data show...").
- **"Data show," not "data shows."** Plural agreement. Yes, English has shifted; in this audience it still matters.
- **Active voice when you can; declarative when you can't.**
- **State the number, then the CI, then the interpretation.** "Smith's S is 0.61 (95% CI [0.48, 0.79]), indicating strong consensus."

### Don'ts

- **No "stunning," "remarkable," "shocking," "surprising."** Flat reporting language. Let the numbers do the work.
- **No exclamation points anywhere in body copy.** Reserve them for accessibility (e.g., screen-reader interjections if absolutely needed).
- **No "AI" as a free-floating noun** ("What does AI think about families?" — wrong on multiple levels, including the §1.5 binding). Use "models," "language models," or specific model names.
- **No second-person addressing the reader** in article body ("You might be wondering..."). Keep the article voice authorial, not conversational. Second-person is fine in UI affordances ("Choose a domain") and in tooltips.
- **No claims about "what the model knows" or "what the model has learned."** §1.5 territory — see the forbidden vocabulary table.

### Worked example

> The "Wrong" example below uses §1.5.4 forbidden terms in order to demonstrate the failure mode (same documented exception class as the §3.1 forbidden-vocabulary table in the doctrinal brief: naming forbidden terms in order to forbid them).

**Wrong** *[do not write copy like this — forbidden vocabulary used here only to demonstrate the failure mode]***:**
> "It's shocking how differently AI models think about families! GPT-5 sees family as fundamentally Western, while Claude views it through a more globalist lens."

**Right:**
> "GPT-5 and Claude produce different categorical structures when given the same family domain prompt. GPT-5's free-list responses concentrate on terms from English-language nuclear-family vocabulary; Claude's responses include a wider set of extended-family and culturally-marked terms. Smith's S for the cross-model consensus is 0.41 (95% CI [0.28, 0.55]) — moderate, not strong."

The second is twice as long and contains five times as much information. It also can't get LSB sued or embarrassed.

---

## 7. Designer-trap list

Things designers reflexively reach for that don't belong here. Save yourself the round trip.

1. **Micro-animations on chart hover.** The math is the point. A subtle highlight on the hovered series is fine; a 200ms eased transition with a tooltip that floats in from below is not.
2. **A dark mode.** Tempting, but: every chart palette must be retuned for the new background (the sequential ramp doesn't work on dark; the qualitative palette needs re-tested for contrast); the open data bundle's static chart exports also need a dark version; the cost is high and the audience benefit is real but secondary. **Don't add it unless Mark explicitly asks.**
3. **Social-share buttons inline with article copy.** If they belong anywhere, it's a small unobtrusive bar at the very bottom.
4. **Newsletter signup CTAs.** LSB is a research website, not a publication trying to grow a list.
5. **Login / account UI.** Doesn't exist; not coming. Don't design the page assuming it will.
6. **A landing page with a hero image.** No marketing photography. No abstract gradient backgrounds. The article is the hero.
7. **An animated loading state.** The page is statically served; everything is in the bundle within the first paint. If you're tempted to add a skeleton screen, the answer is probably "the bundle is too big."
8. **Cookies banner / consent UI.** No tracking, no cookies. (Verify with `SECURITY_AND_HARDENING.md` §8 before committing to this in copy.)
9. **A "what's new" / changelog page.** The Git history is the changelog. If we want a public-facing one later, that's a Phase 8 decision.
10. **Tooltips that say "click to learn more."** Tooltips explain; they don't link out. If the user needs more, the methodology page is the place — but the link goes inline in body copy, not inside a tooltip.

---

## 8. Notes on each §10 open question (in the doctrinal brief)

My opinions on the eight open questions in `FRONTEND_DESIGNER_BRIEF.md` §10. Marked as opinion. The designer is free to disagree.

1. **Methodology page architecture.** I'd lean single long-scroll with section anchors in a left-rail TOC (visible on desktop, collapsed on mobile). Methodology is read end-to-end by researchers; chunking it into routes makes it feel app-like. Mark's call.

2. **Lede strip visual treatment.** Pull-quote treatment. Large serif (~28px), 1.4 line-height, ~16px-equivalent left indent, no quote marks. Sits in its own block above the data explorer.

3. **Article entry point.** Skip the index page for now. At three domains it's clutter. Revisit at six domains. Default landing should be the first domain (or the most recently-collected one).

4. **The "explore the data" affordance.** Yes, worth the pixels. A small horizontal rule + the words "Explore the data" + a downward visual cue. Then the explorer below.

5. **Type system.** Source Serif 4 body + Inter UI is my recommended default. Upgradable to Sectra+America if Mark wants to spend.

6. **Data viz polish.** Three quick wins I'd reach for:
   - MDS plot: replace numeric model labels with model name labels positioned to avoid ellipse overlap (right now models are labeled inside their ellipses, which is information-poor).
   - Heatmap: re-tune the sequential ramp; add row/column model names with truncation discipline; consider grouping models by family (Claude, GPT, Gemini, etc.) in the default ordering rather than alphabetical.
   - Free-list compare: the current bar chart per term is dense; consider a small-multiples view where each model gets its own column with a sparkline of top-10 terms.

7. **Failures-as-findings.** Limitations-section-style placement, after the explorer. Block-quoted decline-interview text, attributed by model+version. A small refusal-rate visualization is appropriate IF cleared by CDA SME first.

8. **Mobile experience.** The current hamburger + bottom drawer work. The mobile-first refresh I'd reach for: type-scale tightening (everything is currently sized for desktop and reads as too large on mobile); chart-aspect-ratio handling (right now charts get small fast); maybe a "swipe between viz tabs" gesture if it can be done accessibly.

---

## 9. The methodology page (when Mark writes it)

This is Mark's territory, but a few notes on the *shape* you might build for him to fill in:

- **Numbered subsections.** § 1 Protocol, § 2 Sample (models + domains), § 3 Statistics, § 4 Uncertainty quantification, § 5 Limitations, § 6 Reproducibility, § 7 Citation.
- **Inline math where needed but not gratuitous.** KaTeX or MathJax; not screenshots of LaTeX.
- **One canonical citation block at the bottom.** DOI (when assigned), BibTeX, suggested human-readable citation.
- **Link out to:** `docs/SME_REVIEW.md`, the open data bundle on Backblaze B2 / Zenodo (when published), the GitHub repo.
- **Tone:** less reader-friendly than the article shell; more authoritative. Methods sections of papers are not warm; they're precise. That's fine.
- **No FAQ format.** The methodology page is not "Frequently Asked Questions." It's a methods section. The structure is logical, not interrogative.

---

## 10. Things I deliberately don't have an opinion on

Mark or you should decide:

- **Whether to use a CSS framework** (Tailwind, vanilla CSS, CSS-in-JS, Panda CSS, etc.). Phase 6 shipped on vanilla CSS with custom properties; that works. Switching frameworks is a substantial change with no methodology consequence — entirely a productivity / aesthetic call.
- **Whether to add a small `<canvas>` or `<webgl>` chart for any view.** The current charts are hand-rolled SVG. SVG hits a wall around ~5,000 elements; we're not there yet. Switching to canvas is a tradeoff between accessibility (SVG wins) and performance (canvas wins).
- **The site's name treatment on the header.** Right now it just says "Latent Structure Benchmark" / "LSB" — no logo. Whether to commission a wordmark, a stylized lockup, or stay text-only is your call.
- **Whether the homepage has a hero quote / pull-quote from someone.** I'd lean no; Mark may want yes.
- **Whether to add a "papers using LSB" sidebar at some point.** Phase 9+ concern; not your problem today.

---

## 11. A note on iterating with Mark

Mark works in Cursor over SSH and reviews via inspection commands more than via Claude-mediated summaries (see `feedback_inspection.md`). When you ship something visual:

- **Build it; deploy to a staging URL or local dev URL; send him the URL.** He'll look at it directly.
- **Don't summarize what you built.** He reads the diff.
- **If you want feedback on a specific tradeoff, name the tradeoff and ask.** Don't ask "does this look good?" — ask "I went with X over Y because Z; the Y alternative would have given us [tradeoff]. Want me to switch?"
- **Ship in small commits.** Don't bundle. He reviews per-commit.
- **He'll override the agent pipeline if he wants to.** When he does, treat it as a binding decision and update memory accordingly.

---

## 12. Final note

The Phase 6 build is yours to keep, replace, or rewrite. Everything in `apps/dashboard/src/` is documented (file paths in `DESIGN_SYSTEM.md` §11), tested (1557 vitest cases), and stable (cleanly deployed). If you want to start from scratch in a different framework, the data contract in `docs/DATA_DICTIONARY.md` and the test suite as a behavioral spec are sufficient anchors. If you want to evolve in place, the existing component tree is reasonable scaffolding.

Mark cares about this project. The design system can carry that care or it can fight it. Make it carry it.

Good luck.

— *the Claude that orchestrated Phase 6, 2026-05-17*

---

*End of `FRONTEND_DESIGNER_BRIEF_APPENDIX.md` v0.2. Opinions are not doctrine; the companion `FRONTEND_DESIGNER_BRIEF.md` is doctrine.*
