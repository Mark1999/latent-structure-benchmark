# Mark-approved impact copy for Collection records (CR-T1, CR-T2)

**Date:** 2026-06-10
**Status:** Approved verbatim by Mark ("Both strawmen are good, use them as written"). These are the authoritative strings for kickoff Tasks T1 and T2 (`docs/status/2026-06-10-collection-records-rework-kickoff.md`, D2 = a). CDA SME gates §1.5 compliance; if the SME requires any change to either string, the change goes back to Mark before shipping. Ship byte-identical otherwise.

## T1: IMPACT_PARAGRAPH_FAILURES (renders above the framing_note)

> Some sessions do not produce a usable answer. A model declines, or returns something our pipeline cannot parse, or the request fails on the provider's side. We keep all of it. Which prompts a model will not answer, and how it says no, is as much a part of its behavior as the answers it gives. Deleting these records would make every model look equally cooperative, and that would be misleading. So they are published here, verbatim.

## T2: IMPACT_PARAGRAPH_FOLLOWUPS (renders by the first follow-up interview record; UI/UX picks exact placement)

> When a model declines, we ask it one more question: why? Its answer is recorded here word for word. Read these with care. The explanation a model gives for refusing is itself just output, produced the same way as everything else it says. It may be consistent, it may be boilerplate, it may contradict what actually happened. That is exactly why we keep it: how a model accounts for its own refusal is one more observable behavior, not the inside story.
