# Pinned: Collection records page review (Mark, 2026-06-10)

**Status:** pinned for a future task cycle, not yet dispatched. CDA-SME-bound copy work plus a possible new data surface. Capture of Mark's verbatim concerns so the framing is not lost.

## Mark's questions

1. The page needs a better explanation of the **real-world impact** of both the collection failures and the follow-up interviews. Why should a visitor care that a model refused or returned something unparseable? What does a follow-up "why did you decline" interview tell a reader about the model's behavior under the protocol?
2. **Why are only "Collection failures" and "Follow-up interviews" listed?** The taxonomy reads as incomplete to a cold visitor.
3. **What about successful collection records?** The page is named "Collection records" but shows only the failure side. Mark expects to see the successful runs represented.
4. **Raw prompt and responses per run, per attempt.** Visibility into the actual elicitation exchange for each record, including retries/attempts.

## Context for the future Architect

- Item 4 overlaps audit gap G7 (per-finding provenance surface: provider_request_id and SHA256 exist per record but are not linked from any chart or page). A raw-exchange browser would close G7 and item 4 together.
- Item 3 is a data-volume question: successful records live in the open data bundle (HF/Zenodo/B2), not in per-record JSON on the site today. Surfacing them needs a publish-layer decision (per-domain success summaries vs full record browser) and likely new publish artifacts.
- Items 1-2 are copy and framing: the existing framing_note is CDA-SME-approved but evidently does not land the "failures are findings" significance for a general reader. Any rewrite is CDA-SME-bound and should use Mark's voice.
- Related binding context: failures-are-findings directive, ARCHITECTURE.md §1.5 framing, the "Collection records" tab label ruling (9a-T1, chosen over "Failures" to avoid reading as the models failing).
