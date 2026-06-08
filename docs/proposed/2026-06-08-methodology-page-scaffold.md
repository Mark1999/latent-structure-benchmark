# Methodology page, draft scaffold (for Mark's review and personal authoring)

**Status:** DRAFT for Mark. Per ARCHITECTURE §5.3 / DESIGN_SYSTEM §6.1, the methodology page is
Mark-authored, not Coder-generated. This is a starting draft in Mark's voice (per
the `WritingSample/` review, 2026-06-08) for him to cut, rewrite, and own. Nothing here ships
until Mark approves the prose and it passes the gates below.

**Scope:** fills the placeholder in `MethodologyPage.tsx` (the §6.1 sections 1 through 6). The two
sections already live on the page (**Data provenance** and **Cross-model term map and uncertainty**)
are verbatim CDA-SME copy and stay exactly as they are; this draft sits above them.

**Rails this draft already respects (so the SME pass is light):**
- Anchors the precise construct ("the latent categorical structure of a training corpus, refracted
  through training and alignment") and defines "corpus lens" on first use, per §1.5.1.
- Surfaces every §1.5.3 limitation (prompt sensitivity, English-only, corpus opacity, alignment
  confound, sampling variance, the informant metaphor is metaphor).
- No §1.5.4 / §7 forbidden vocabulary.
- No em dashes (per Mark's standing rule).

**Gates to ship (after Mark authors the final prose):** CDA SME (framing + vocab) → UI/UX (page
layout, the 30-second-journalist + reproduce-and-cite tests, WCAG) → Coder (replace the placeholder
`<section>` in `MethodologyPage.tsx`) → Reviewer → Tester.

**Voice notes used here (from `reference_mark_writing_voice`):** demystify first, plain-question
section headers that anticipate the reader, explain a category the way the "you reader, are a
segment" post does, use the "picture on the dresser" reasoning for the limits section (an observed
pattern is real and can still have a boring cause), be honest about limits in the text, close on
"do your own homework."

---

## 1. What is this, really?

The Latent Structure Benchmark takes a method that anthropologists use to study people and points
it at large language models instead.

The method is old and unglamorous. If you want to understand how a group of people carves up some
corner of life, say the world of family, or holidays, or food, you do not start with a theory. You
ask them to list the things in that world, and then you ask them to sort those things into piles
that go together. Do that with enough people and patterns fall out: which items everyone names
first, which things reliably get grouped together, where people agree and where they split. That is
Cultural Domain Analysis, and it has been around for decades.

We run that same protocol on language models, one prompt at a time, as if the model were a person we
were interviewing. It is not a person, and that "as if" is doing real work; more on that in section
4. What comes out is a map of how a given model sorts the everyday words in a domain.

We call the thing those maps show the **corpus lens**: the shape a model imposes on a domain,
inherited from the text it was trained on. Said more carefully, and this is the version we would
defend to a skeptical researcher, it is the latent categorical structure of a training corpus, as
refracted through the model's training and alignment. The short name is for headlines. The long name
is the honest one. They mean the same thing.

## 2. What does "corpus lens" actually mean?

Start with what a category even is, because the whole benchmark rests on it.

You, reader, sort the world into categories all day without noticing. A "vegetable" is a category. So
is "a holiday," "a relative," "a snack." We group things so we can think about them without drowning
in detail. A category lets you say a great deal in one short word. The catch is that the grouping is
a choice, and different sources make different choices. Whether a tomato files under "vegetable" or
"fruit" depends on whether you are cooking or doing botany.

A language model makes these choices too, not because anyone taught it a theory of vegetables, but
because it absorbed an enormous amount of text in which people had already done the sorting. The
corpus lens is the residue of all that sorting, after it has been pushed through the machine that
built the model. That machine has five stages, and it helps to name them:

- the **corpus**, the text the model was trained on,
- **training**, which compresses the patterns in that text into the model's weights,
- **alignment**, the later tuning that nudges the model toward being helpful and harmless,
- **decoding**, the settings that turn the model's internal probabilities into actual words,
- and the **output distribution**, the landscape of likely responses we finally get to sample.

When we run a free-list or a pile-sort, we are looking at the shadow that whole chain casts when we
shine our questions at it. We measure the shadow directly. Everything we say about the stages behind
it is an inference, not a measurement, and we try to be clear about which is which.

## 3. How does the measurement work? (there is no magic in it)

If this takes the mystery out of it, good. There is not much mystery to take.

We ask each model two kinds of question, many times over:

- A **free-list**: name the members of a category. "List the kinds of family members." We count which
  items show up, and how early, across all the runs. Items that come up often and early are
  *salient*; the statistic for that is Smith's S, and a high S just means "this is one of the first
  things that comes to mind in this domain."
- A **pile-sort**: here are the items, sort them into piles that belong together. We count how often
  any two items land in the same pile. Do that across runs and across models and you get a similarity
  structure: which things cluster, which sit apart.

From the pile-sort similarities we draw the map you see on the dashboard. Items that get grouped
together sit close; items that rarely co-occur sit far apart. That is multidimensional scaling, which
is a fancy name for a simple goal: put things on a 2D map so that distance on the map matches how
unalike they are.

Two things we insist on, because they are where this kind of work usually goes wrong:

First, we never show a point without showing how sure we are of it. Every position on the map carries
an uncertainty ellipse, drawn by resampling the data hundreds of times and watching how much the
answer wobbles. A tight ellipse means the structure is solid. A fat one means do not read too much
into the exact spot.

Second, when something fails, that is data, not garbage. A model that refuses a prompt, or returns an
empty list, gets recorded and shown, not quietly dropped. A refusal is itself a finding about the
machine.

## 4. What this does not measure (or, the picture on the dresser)

Here is the part to read twice.

When you see two models sort family words into the same piles, the words almost beg you to say that
the two models "see family the same way," that they share some value or attitude. Do not say it. Or
at least, know that you would be guessing, not reading the data.

A pattern can be perfectly real and still have a dull cause. Suppose you walked into my home and found
a single photograph on display in my bedroom, a young woman with a guitar, and nothing else on the
walls. You could infer a great deal: an old flame, a quiet heartbreak, a story. You would also be
wrong. The honest explanation is that I am a slob, a cleaner once tidied a toppled stack of prints,
and that one happened to land in a frame and stay there. The pattern was real. The meaning you
reached for was a projection. The only way to know the difference is to ask, and not just look.

The benchmark is in the same position, with one hard limit: there is no one to ask. So we hold the
line on what we will claim. We measure categorical structure in a model's output, refracted from the
text it learned on. We do not claim it as evidence of belief, preference, cognition, or inner
experience, because the model has none of those, and our method could not see them if it did. The
structure is the finding. The inner life is not on the table.

A few more limits, stated plainly because burying them would be the opposite of the point:

- **Wording matters.** Change the prompt and the output can shift. We hold the prompt fixed across
  models within a run, and we ran a formal study of how much paraphrasing moves the result. Whatever
  wobble is left shows up as the uncertainty you see on every chart.
- **English only, for now.** The benchmark runs in English. Anything it seems to say about another
  culture is really a statement about how English-language text represents that culture, which is not
  the same thing.
- **We cannot see the corpus.** The training data for most of these models is not public. We can show
  you the structure; we usually cannot trace it back to a particular source.
- **Training and tuning are tangled.** Pretraining, alignment, and system prompts all bend the output,
  and our method sees the sum, not the separate parts. For "how does this deployed product behave"
  that is fine. For "what was in the raw corpus" it is a real limit.
- **The interview is a metaphor.** Treating the model as an informant is a move we make to borrow a
  good method. It is not a claim that there is anybody home.

## 5. How do I read the charts?

Short version, so the dashboard is not a puzzle:

- **The model map (MDS).** Each labeled point is one model's position for the domain. Closer together
  means more alike in how they sorted the domain. The ring around each point is uncertainty; overlap
  means the difference may not be real.
- **The similarity heatmap.** Every cell is one model-pair, darker for more alike. Cells whose
  confidence interval crosses zero are drawn faint, because we are not sure they differ from chance.
- **The term map.** Here the points are the words themselves, placed by how often models grouped them
  together. This is where you see a domain's internal shape.
- **Consensus.** A single number for "how much do the models agree on this domain," with the usual
  uncertainty attached.

Every figure links back here, and every figure shows its uncertainty. If a claim on this site does
not come with a sense of how sure we are, treat that as a bug and tell us.

## 6. Do not take my word for it

This is one instrument, built and run by a small operation, and like any single source it has a point
of view and its blind spots. So we made it checkable.

The full open data bundle is public: every raw model response, the processed results, and the code
that turns one into the other. Given the bundle and an afternoon, you can rebuild the database from
the raw responses, rerun the analysis, and regenerate every figure on this site. The exact toolchain
versions and the code commit behind the current numbers are recorded in the data provenance, just
below. The release carries a citable DOI.

We would rather you check us than trust us. Do your own homework.

---

*(Sections 7 onward, Data provenance and Cross-model term map and uncertainty, are already live as
verbatim CDA-SME copy and are unchanged.)*

---

## Notes for the author (Mark)

- The "picture on the dresser" passage in section 4 is the load-bearing move and the one most likely
  to need your hand. It is drawn straight from your 2007 post. If you would rather not put a personal
  anecdote on the public page, the same point survives as the abstract version ("a real pattern can
  have a dull cause; the only fix is to ask, and here there is no one to ask"). Your call.
- Section 1's "method that is old and unglamorous" and section 3's "there is no magic in it" lean on
  your demystify habit. Keep or cut to taste.
- I kept the precise construct anchored in section 1 and defined "corpus lens" there on first use,
  which is the one hard requirement the CDA SME will check. If you reorder sections, keep that anchor
  ahead of any later use of "corpus lens."
- Every §1.5.3 limitation is present in section 4. The SME requires all of them on the page, so if you
  trim, move rather than delete.
- Length is a first pass. The 30-second-journalist test wants sections 1 and 4 to stand on their own;
  the reproduce-and-cite test wants sections 3 and 6 to be specific. UI/UX will weigh in on both.
