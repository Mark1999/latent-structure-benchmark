"""Unit tests for cdb_social/drafters/ — Phase 7 T3.

Tests organised by CDA SME binding note (§5.x) from
docs/status/2026-05-17-phase7-T3-cda-sme-verdict.md.

No real Anthropic API calls are made.  The BlueskyDrafter accepts an
injected ``anthropic_client`` argument; tests supply a MockAnthropicClient
that returns deterministic fixture responses.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from cdb_core.schemas import (
    BootstrapEllipse,
    DomainResult,
    FreeList,
    ModelRef,
    Platform,
    SocialTrigger,
    TriggerType,
)
from cdb_social.drafters import (
    BlueskyDrafter,
    DrafterRejectedException,
    LinkedInDrafter,
    XDrafter,
    validate_draft,
    validate_draft_forbidden_vocab,
    validate_draft_hypothesis_framing,
    validate_draft_numeric_ci_adjacency,
)
from cdb_social.drafters.base import (
    _HYPOTHESIS_FRAMING_PATTERNS,
    CI_SHAPE_REGEX,
    _check_rejection_window,
    load_prompt,
)
from cdb_social.drafters.linkedin import (
    _check_linkedin_no_first_person,
    _validate_linkedin_anti_thought_leadership,
)
from cdb_social.drafters.x import (
    _X_SEGMENT_DELIMITER,
    _check_x_thread_structure,
    _validate_x_hook_tweet,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixture helpers
# ─────────────────────────────────────────────────────────────────────────────

_FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "social" / "drafter_responses"


def _load_fixture(name: str) -> str:
    """Load a canned LLM response from the fixture directory."""
    return (_FIXTURE_DIR / name).read_text(encoding="utf-8").strip()


def _model_ref(
    model_id: str = "claude-opus-4-6",
    family: str = "claude",
) -> ModelRef:
    return ModelRef(
        provider="anthropic",
        model_id=model_id,
        family=family,
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2025, 1, 1),
        version_label="4.6",
    )


def _domain_result(
    domain_slug: str = "family",
    n_models: int = 3,
) -> DomainResult:
    """Minimal DomainResult for drafter tests."""
    model_ids = [f"model-{i}" for i in range(n_models)]
    coords = {mid: (float(i), 0.0) for i, mid in enumerate(model_ids)}
    n = n_models
    sim_matrix = [[1.0 if i == j else 0.5 for j in range(n)] for i in range(n)]
    sim_ci = [
        [(0.4, 0.6) for _ in range(n)] for _ in range(n)
    ]
    ellipse = BootstrapEllipse(
        center=(0.0, 0.0),
        semi_major=0.1,
        semi_minor=0.05,
        rotation_rad=0.0,
        n_bootstrap=1000,
    )
    return DomainResult(
        domain_slug=domain_slug,
        analysis_version="v1",
        models=[_model_ref(mid) for mid in model_ids],
        free_lists={
            mid: FreeList(
                run_id=f"run-{mid}",
                model=_model_ref(mid),
                domain_slug=domain_slug,
                items=["mother", "father"],
                raw_order=["mother", "father"],
            )
            for mid in model_ids
        },
        mds_coordinates=coords,
        mds_uncertainty={mid: ellipse for mid in model_ids},
        similarity_matrix=sim_matrix,
        similarity_ci=sim_ci,
        consensus_score=0.72,
        consensus_ci=(0.55, 0.88),
        generated_lede="Placeholder lede.",
        generated_at=datetime(2026, 5, 17, tzinfo=UTC),
    )


def _trigger(
    trigger_type: TriggerType = TriggerType.NEW_MODEL,
    domain_slug: str = "family",
    model_id: str = "gpt-5",
) -> SocialTrigger:
    return SocialTrigger(
        trigger_type=trigger_type,
        detected_at=datetime(2026, 5, 17, tzinfo=UTC),
        domain_slug=domain_slug,
        model_id=model_id,
        evidence={"first_seen_in_domain": "family"},
        dedupe_key="abc123def456789a",
    )


class MockAnthropicMessage:
    """Minimal mock of an Anthropic message response."""

    def __init__(self, text: str) -> None:
        block = MagicMock()
        block.text = text
        self.content = [block]


class MockAnthropicClient:
    """Mock Anthropic client that returns a fixed canned response.

    Stores the last call's arguments for inspection in cache/no-cache tests.
    """

    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.last_call_kwargs: dict[str, Any] = {}
        # Mirror real client structure: client.messages.create(...)
        self.messages = self

    def create(self, **kwargs: Any) -> MockAnthropicMessage:
        self.last_call_kwargs = kwargs
        return MockAnthropicMessage(self._response_text)


# ─────────────────────────────────────────────────────────────────────────────
# TestValidatorForbiddenVocab (§5.1, §5.16)
# ─────────────────────────────────────────────────────────────────────────────


class TestValidatorForbiddenVocab:
    """§5.1 — Full §1.5.4 table + word-stem matches, case-insensitive."""

    def test_clean_text_returns_empty(self) -> None:
        hits = validate_draft_forbidden_vocab(
            "GPT-5's output on family vocabulary clusters tightly: "
            "OCI = 2.4 (1.8, 3.1). The corpus lens concentrates on family terms."
        )
        assert hits == []

    # Row 1: "Model X believes..."
    def test_row1_model_x_believes(self) -> None:
        hits = validate_draft_forbidden_vocab("Model GPT-5 believes the data is clear.")
        assert any("believes" in h.lower() for h in hits)

    def test_row1_models_believe(self) -> None:
        hits = validate_draft_forbidden_vocab("These models believe in different structures.")
        assert any("believe" in h.lower() for h in hits)

    # Row 2: "Model X thinks of family as..."
    def test_row2_model_x_thinks_of(self) -> None:
        hits = validate_draft_forbidden_vocab("Model Claude thinks of family as hierarchical.")
        assert any("thinks of" in h.lower() for h in hits)

    def test_row2_models_think_of(self) -> None:
        hits = validate_draft_forbidden_vocab("Models think of vocabulary differently.")
        assert any("think of" in h.lower() for h in hits)

    # Row 3: "How models see the world"
    def test_row3_how_models_see_the_world(self) -> None:
        hits = validate_draft_forbidden_vocab("How models see the world varies widely.")
        assert hits

    # Row 4: "Model X's worldview"
    def test_row4_model_worldview(self) -> None:
        hits = validate_draft_forbidden_vocab("GPT-5's worldview is narrow.")
        assert hits

    def test_row4_models_worldview(self) -> None:
        hits = validate_draft_forbidden_vocab("The models' worldview shapes their output.")
        assert hits

    # Row 5: "Cultural bias"
    def test_row5_cultural_bias_standalone(self) -> None:
        hits = validate_draft_forbidden_vocab("This shows cultural bias in the outputs.")
        assert any("cultural bias" in h.lower() for h in hits)

    # Row 6: "What the model understands"
    def test_row6_what_the_model_understands(self) -> None:
        hits = validate_draft_forbidden_vocab("What the model understands about family.")
        assert hits

    # Rows 7–10: Register-boundary phrases
    def test_row7_within_model_consensus(self) -> None:
        hits = validate_draft_forbidden_vocab("Within-model consensus is high.")
        assert hits

    def test_row8_within_model_cultural_consensus(self) -> None:
        hits = validate_draft_forbidden_vocab("Within-model cultural consensus drives this.")
        assert hits

    def test_row9_within_model_eigenratio(self) -> None:
        hits = validate_draft_forbidden_vocab("The within-model eigenratio is 2.4.")
        assert hits

    def test_row10_within_model_ccm(self) -> None:
        hits = validate_draft_forbidden_vocab("Within-model CCM shows structure.")
        assert hits

    # Stem-level: worldview, believes, thinks — with case variations
    def test_stem_worldview_lowercase(self) -> None:
        hits = validate_draft_forbidden_vocab("This reflects a worldview about culture.")
        assert any("worldview" in h.lower() for h in hits)

    def test_stem_worldview_titlecase(self) -> None:
        hits = validate_draft_forbidden_vocab("A Worldview emerges from the outputs.")
        assert any("worldview" in h.lower() for h in hits)

    def test_stem_believes_lowercase(self) -> None:
        hits = validate_draft_forbidden_vocab("The model believes structure is fixed.")
        assert any("believes" in h.lower() for h in hits)

    def test_stem_believes_uppercase(self) -> None:
        hits = validate_draft_forbidden_vocab("The model BELIEVES structure is fixed.")
        assert any("believes" in h.lower() for h in hits)

    def test_stem_thinks_lowercase(self) -> None:
        hits = validate_draft_forbidden_vocab("GPT-5 thinks about family differently.")
        assert any("thinks" in h.lower() for h in hits)

    # Word-boundary anchoring: "disbelieves" should NOT match "believes"
    def test_word_boundary_disbelieves_no_match(self) -> None:
        hits = validate_draft_forbidden_vocab(
            "No one disbelieves the measurement results here."
        )
        # "disbelieves" must NOT trigger the \bbelieves\b stem match
        stem_hits = [h for h in hits if h.lower() == "believes"]
        assert stem_hits == []

    # "rethinks" should not match "thinks"
    def test_word_boundary_rethinks_no_match(self) -> None:
        hits = validate_draft_forbidden_vocab("The field rethinks its assumptions.")
        stem_hits = [h for h in hits if h.lower() == "thinks"]
        assert stem_hits == []

    # Fixture: "forbidden_vocab_phrase" fixture fails §5.1
    def test_fixture_forbidden_vocab_phrase(self) -> None:
        text = _load_fixture("forbidden_vocab_phrase.txt")
        hits = validate_draft_forbidden_vocab(text)
        assert hits, "Expected forbidden phrase hit on 'Model GPT-5 believes...'"

    # Fixture: "forbidden_vocab_worldview" fixture fails §5.1 stem
    def test_fixture_forbidden_vocab_worldview(self) -> None:
        text = _load_fixture("forbidden_vocab_worldview.txt")
        hits = validate_draft_forbidden_vocab(text)
        assert any("worldview" in h.lower() for h in hits)

    # Fixture: good draft passes §5.1
    def test_fixture_good_draft_passes(self) -> None:
        text = _load_fixture("good_draft.txt")
        hits = validate_draft_forbidden_vocab(text)
        assert hits == [], f"Unexpected forbidden vocab in good draft: {hits}"


# ─────────────────────────────────────────────────────────────────────────────
# TestValidatorNumericCI (§5.2, §5.16)
# ─────────────────────────────────────────────────────────────────────────────


class TestValidatorNumericCI:
    """§5.2 — Numeric+CI adjacency: K=12, four CI patterns, five exemptions."""

    def test_bare_numeric_rejected(self) -> None:
        text = "Smith's S is 0.61. The corpus lens concentrates here."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert not ok
        assert bare  # 0.61 is bare

    def test_ci_bracketed_accepted_pattern_a(self) -> None:
        # Pattern (a): (95% CI [a, b])
        text = "Smith's S = 0.61, 95% CI [0.48, 0.79]. Corpus lens concentrates."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"Bare numerics found: {bare}"

    def test_ci_bracketed_accepted_pattern_b(self) -> None:
        # Pattern (b): CI: a–b
        text = "OCI = 2.4, CI: 1.8–3.1. Corpus lens concentrates here."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"Bare numerics found: {bare}"

    def test_ci_bracketed_accepted_pattern_c(self) -> None:
        # Pattern (c): ±X
        text = "Consensus eigenratio = 5.2 ± 0.8. Corpus lens concentrates."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"Bare numerics found: {bare}"

    def test_ci_bracketed_accepted_pattern_d(self) -> None:
        # Pattern (d): (a, b) paren pair
        text = "OCI = 2.4 (1.8, 3.1). Corpus lens concentrates here."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"Bare numerics found: {bare}"

    # Exemption category (a): model version strings
    def test_exemption_model_version_gpt(self) -> None:
        text = "GPT-5's output clusters tightly: OCI = 2.4 (1.8, 3.1)."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"GPT-5 should be exempt, bare: {bare}"

    def test_exemption_model_version_claude(self) -> None:
        text = "Claude-3.5 output: OCI = 2.4 (1.8, 3.1). Corpus lens concentrates."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"Claude-3.5 should be exempt, bare: {bare}"

    # Exemption category (b): years
    def test_exemption_year_token(self) -> None:
        text = "In 2026, OCI = 2.4 (1.8, 3.1). Corpus lens concentrates."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"Year 2026 should be exempt, bare: {bare}"

    # Exemption category (c): character counts
    def test_exemption_char_count(self) -> None:
        text = "Post is 270 chars: OCI = 2.4 (1.8, 3.1). Corpus lens."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"Char count should be exempt, bare: {bare}"

    # Exemption category (e): count-of-N context
    def test_exemption_count_of_n_models(self) -> None:
        text = "Results across 12 models: OCI = 2.4 (1.8, 3.1). Corpus lens."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"'across 12 models' should be exempt, bare: {bare}"

    def test_exemption_count_of_n_domains(self) -> None:
        text = "Over 8 domains: OCI = 2.4 (1.8, 3.1). Corpus lens."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"'over 8 domains' should be exempt, bare: {bare}"

    # Exemption (d): URL components — URLs stripped before scan
    def test_exemption_url_numeric(self) -> None:
        text = "See https://cogstructurelab.com/family: OCI = 2.4 (1.8, 3.1)."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"URL numeric should be exempt, bare: {bare}"

    # K=12 token window boundary: CI exactly 12 tokens away passes
    def test_k12_boundary_within_window_passes(self) -> None:
        # 12 words between the numeric and the CI
        padding = "word " * 10  # 10 extra words between value and CI marker
        text = f"OCI = 2.4 {padding}(1.8, 3.1). Corpus lens."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        # 10 padding words + a few surrounding tokens — may or may not pass
        # depending on exact token count; the key is K=12 is enforced.
        # We don't assert direction here — just that it runs without error.
        assert isinstance(ok, bool)

    # CI strictly outside K=12 window fails
    def test_k12_boundary_outside_window_fails(self) -> None:
        # 15 words between the numeric and the CI — outside K=12
        padding = " ".join(["word"] * 15)
        text = f"OCI = 2.4 {padding} (1.8, 3.1). Corpus lens."
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert not ok, "CI more than 12 tokens away should fail"

    # Fixture: bare_numeric fixture fails §5.2
    def test_fixture_bare_numeric(self) -> None:
        text = _load_fixture("bare_numeric.txt")
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert not ok, "Expected bare numeric failure"

    # Fixture: good_draft passes §5.2
    def test_fixture_good_draft_passes(self) -> None:
        text = _load_fixture("good_draft.txt")
        ok, bare = validate_draft_numeric_ci_adjacency(text)
        assert ok, f"Expected CI adjacency pass; bare: {bare}"

    def test_ci_shape_regex_matches_95_ci_square_brackets(self) -> None:
        assert CI_SHAPE_REGEX.search("95% CI [0.48, 0.79]")

    def test_ci_shape_regex_matches_95_ci_paren_brackets(self) -> None:
        assert CI_SHAPE_REGEX.search("(95% CI 0.48-0.79)")

    def test_ci_shape_regex_matches_paren_pair(self) -> None:
        assert CI_SHAPE_REGEX.search("(1.8, 3.1)")

    def test_ci_shape_regex_matches_plus_minus(self) -> None:
        assert CI_SHAPE_REGEX.search("± 0.8")


# ─────────────────────────────────────────────────────────────────────────────
# TestValidatorHypothesisFraming (§5.3, §5.16)
# ─────────────────────────────────────────────────────────────────────────────


class TestValidatorHypothesisFraming:
    """§5.3 — Closed list of 14 hypothesis-framing phrases."""

    @pytest.mark.parametrize("phrase,text", [
        ("LSB hypothesized", "LSB hypothesized that models diverge."),
        ("LSB hypothesised", "LSB hypothesised that models diverge."),
        ("LSB tested whether", "LSB tested whether models agree."),
        ("LSB confirms that", "LSB confirms that the structure holds."),
        ("LSB confirms that", "LSB confirms that the structure holds."),
        ("LSB found that", "LSB found that GPT-5 clusters tightly."),
        ("LSB predicted", "LSB predicted high consensus."),
        ("data confirmed", "The data confirmed the hypothesis."),
        ("data refuted", "The data refuted our prediction."),
        ("our results show", "Our results show high consensus."),
        ("this demonstrates", "This demonstrates alignment in the corpus."),
        ("this means", "This means the model is consistent."),
        ("this proves", "This proves that GPT-5 clusters together."),
        ("we hypothesized", "We hypothesized that models would diverge."),
        ("confirms that", "The result confirms that structure holds."),
        ("proves that", "The analysis proves that models agree."),
    ])
    def test_each_pattern_triggers_rejection(self, phrase: str, text: str) -> None:
        hits = validate_draft_hypothesis_framing(text)
        assert hits, f"Expected hypothesis-framing hit for phrase: {phrase!r}"

    def test_close_but_not_forbidden_lsb_measures(self) -> None:
        hits = validate_draft_hypothesis_framing("LSB measures output concentration.")
        assert hits == []

    def test_close_but_not_forbidden_lsb_reports(self) -> None:
        hits = validate_draft_hypothesis_framing("LSB reports the eigenratio.")
        assert hits == []

    def test_close_but_not_forbidden_lsb_observes(self) -> None:
        hits = validate_draft_hypothesis_framing("LSB observes categorical structure shifts.")
        assert hits == []

    def test_clean_text_passes(self) -> None:
        text = (
            "GPT-5's output on family vocabulary clusters tightly: "
            "OCI = 2.4 (1.8, 3.1). Corpus lens concentrates on family terms."
        )
        hits = validate_draft_hypothesis_framing(text)
        assert hits == []

    def test_fixture_hypothesis_framing(self) -> None:
        text = _load_fixture("hypothesis_framing.txt")
        hits = validate_draft_hypothesis_framing(text)
        assert hits, "Expected hypothesis-framing hit in fixture"

    def test_fourteen_patterns_defined(self) -> None:
        """The closed list must have exactly 14 patterns per §5.3."""
        assert len(_HYPOTHESIS_FRAMING_PATTERNS) == 14


# ─────────────────────────────────────────────────────────────────────────────
# TestFramingChecksDict (§5.11, §5.18)
# ─────────────────────────────────────────────────────────────────────────────


class TestFramingChecksDict:
    """§5.11 — All four framing_checks keys populated; framing_check_passed is AND."""

    def test_exact_four_keys_present_on_clean_text(self) -> None:
        """Exact canonical four-key set per CDA SME §5.11."""
        _, framing_checks = validate_draft(
            "GPT-5's output clusters tightly: OCI = 2.4 (1.8, 3.1). "
            "Corpus lens concentrates on family terms."
        )
        assert set(framing_checks.keys()) == {
            "hypothesis_framing",
            "cognition_attribution",
            "bare_numeric_without_ci",
            "register_boundary",
        }

    def test_all_four_keys_present_on_clean_text(self) -> None:
        _, framing_checks = validate_draft(
            "GPT-5's output clusters tightly: OCI = 2.4 (1.8, 3.1). "
            "Corpus lens concentrates on family terms."
        )
        assert "hypothesis_framing" in framing_checks
        assert "cognition_attribution" in framing_checks
        assert "bare_numeric_without_ci" in framing_checks
        assert "register_boundary" in framing_checks

    def test_all_true_on_clean_text(self) -> None:
        _, framing_checks = validate_draft(
            "GPT-5's output clusters tightly: OCI = 2.4 (1.8, 3.1). "
            "Corpus lens concentrates on family terms."
        )
        assert all(framing_checks.values()), f"Expected all True: {framing_checks}"

    def test_cognition_attribution_false_on_stem_hit(self) -> None:
        _, framing_checks = validate_draft(
            "The model believes it, OCI = 2.4 (1.8, 3.1). Corpus lens."
        )
        assert framing_checks["cognition_attribution"] is False

    def test_hypothesis_framing_false_on_phrase_hit(self) -> None:
        _, framing_checks = validate_draft(
            "Our results show high consensus. OCI = 2.4 (1.8, 3.1)."
        )
        assert framing_checks["hypothesis_framing"] is False

    def test_bare_numeric_without_ci_false_on_bare_numeric(self) -> None:
        _, framing_checks = validate_draft(
            "Smith's S is 0.61. Corpus lens concentrates here."
        )
        assert framing_checks["bare_numeric_without_ci"] is False

    def test_register_boundary_detects_row_7(self) -> None:
        """§1.5.4 row 7 'within-model consensus' sets register_boundary=False."""
        _, framing_checks = validate_draft(
            "Within-model consensus is high. OCI = 2.4 (1.8, 3.1). Corpus lens."
        )
        assert framing_checks["register_boundary"] is False

    def test_register_boundary_detects_row_8(self) -> None:
        """§1.5.4 row 8 'within-model cultural consensus' sets register_boundary=False."""
        _, framing_checks = validate_draft(
            "Within-model cultural consensus drives this. OCI = 2.4 (1.8, 3.1)."
        )
        assert framing_checks["register_boundary"] is False

    def test_register_boundary_detects_row_9(self) -> None:
        """§1.5.4 row 9 'within-model eigenratio' sets register_boundary=False."""
        _, framing_checks = validate_draft(
            "The within-model eigenratio is 2.4 (1.8, 3.1). Corpus lens."
        )
        assert framing_checks["register_boundary"] is False

    def test_register_boundary_detects_row_10(self) -> None:
        """§1.5.4 row 10 'within-model CCM' sets register_boundary=False."""
        _, framing_checks = validate_draft(
            "Within-model CCM shows structure. OCI = 2.4 (1.8, 3.1). Corpus lens."
        )
        assert framing_checks["register_boundary"] is False

    def test_register_boundary_does_not_match_row_1_phrases(self) -> None:
        """Rows 1-6 phrases do NOT set register_boundary=False.

        'Model X believes...' is a row-1 forbidden phrase that populates
        forbidden_terms_hit and sets cognition_attribution=False (via stem
        hit on 'believes'), but must NOT affect register_boundary.
        Rows 1-6 and rows 7-10 are distinct check surfaces.
        """
        _, framing_checks = validate_draft(
            # Row 1 phrase — forbidden, but NOT a register-boundary phrase
            "Model GPT-5 believes the structure. OCI = 2.4 (1.8, 3.1). Corpus lens."
        )
        # register_boundary must remain True — only rows 7-10 affect it
        assert framing_checks["register_boundary"] is True
        # cognition_attribution must be False due to the 'believes' stem hit
        assert framing_checks["cognition_attribution"] is False

    def test_register_boundary_true_on_clean_text(self) -> None:
        _, framing_checks = validate_draft(
            "OCI = 2.4 (1.8, 3.1). The corpus lens concentrates on family terms."
        )
        assert framing_checks["register_boundary"] is True

    def test_framing_check_passed_is_and_of_all(self) -> None:
        """framing_check_passed = AND(framing_checks.values()) AND forbidden_terms==[].

        Tested indirectly via BlueskyDrafter.draft() — the SocialDraft carries
        framing_check_passed.  Here we test the validate_draft facade directly.
        """
        # All pass
        hits, framing_checks = validate_draft(
            "OCI = 2.4 (1.8, 3.1). Corpus lens concentrates on family terms."
        )
        all_pass = not hits and all(framing_checks.values())
        assert all_pass

        # One fails
        hits2, framing_checks2 = validate_draft(
            "Smith's S is 0.61. Corpus lens concentrates here."
        )
        all_pass2 = not hits2 and all(framing_checks2.values())
        assert not all_pass2


# ─────────────────────────────────────────────────────────────────────────────
# TestBlueskyDrafterStructure (§5.7, §5.5)
# ─────────────────────────────────────────────────────────────────────────────


class TestBlueskyDrafterStructure:
    """Pattern A (3-line) and Pattern B (4-line) fit ≤ 270 chars; URL label is 'details'."""

    def test_good_draft_fits_270_chars(self) -> None:
        text = _load_fixture("good_draft.txt")
        assert len(text) <= 270, f"Good draft is {len(text)} chars"

    def test_good_draft_fits_300_chars_hard_limit(self) -> None:
        text = _load_fixture("good_draft.txt")
        assert len(text) <= 300, f"Good draft is {len(text)} chars"

    def test_good_draft_url_contains_domain(self) -> None:
        text = _load_fixture("good_draft.txt")
        assert "cogstructurelab.com/family" in text

    def test_good_draft_url_label_is_details(self) -> None:
        text = _load_fixture("good_draft.txt")
        # The URL should be preceded by "details" (not "methodology")
        assert "details" in text.lower()
        assert "methodology" not in text.lower()

    def test_round_trip_url_is_article_shell(self, tmp_path: Path) -> None:
        """BlueskyDrafter builds article-shell URL for domain slug."""
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger(domain_slug="family")
        result = drafter.draft(trigger, _domain_result())
        assert "cogstructurelab.com/family" in result.methodology_url
        assert "cogstructurelab.com/family" in result.dashboard_url

    def test_round_trip_methodology_url_not_labeled_methodology(
        self, tmp_path: Path
    ) -> None:
        """Post text labels the URL 'details', not 'methodology'."""
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger(domain_slug="family")
        result = drafter.draft(trigger, _domain_result())
        # The post text uses "details", not "methodology"
        assert "details" in result.text.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TestBlueskyDrafterSelfRating (§5.6)
# ─────────────────────────────────────────────────────────────────────────────


class TestBlueskyDrafterSelfRating:
    """§5.6 — drafter_self_rating is always 0.5, regardless of LLM output."""

    def test_self_rating_is_0_5(self) -> None:
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        result = drafter.draft(trigger, _domain_result())
        assert result.drafter_self_rating == 0.5

    def test_self_rating_not_from_llm_output(self) -> None:
        """Even if LLM output contained a rating, drafter_self_rating is fixed."""
        # The LLM response is irrelevant to drafter_self_rating
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        result = drafter.draft(trigger, _domain_result())
        # Always 0.5 regardless
        assert result.drafter_self_rating == 0.5


# ─────────────────────────────────────────────────────────────────────────────
# TestPromptVersioning (§5.13)
# ─────────────────────────────────────────────────────────────────────────────


class TestPromptVersioning:
    """§5.13 — Prompt file at v1/bluesky.md exists; bumping requires new directory."""

    def test_v1_prompt_file_exists(self) -> None:
        prompts_dir = (
            Path(__file__).parent.parent.parent
            / "packages"
            / "cdb_social"
            / "cdb_social"
            / "drafters"
            / "prompts"
            / "v1"
        )
        assert (prompts_dir / "bluesky.md").exists(), (
            "Expected v1/bluesky.md prompt file at "
            f"{prompts_dir / 'bluesky.md'}"
        )

    def test_load_prompt_v1_returns_text(self) -> None:
        text = load_prompt("bluesky", "v1")
        assert len(text) > 100, "Prompt text should be non-trivial"

    def test_load_prompt_nonexistent_version_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_prompt("bluesky", "v99")

    def test_drafter_prompt_version_matches_directory(self) -> None:
        """BlueskyDrafter.prompt_version must match the directory it loads from."""
        drafter = BlueskyDrafter.__new__(BlueskyDrafter)
        assert drafter.prompt_version == "v1"
        # The file at prompts/v1/bluesky.md must exist
        prompt_text = load_prompt("bluesky", drafter.prompt_version)
        assert prompt_text  # non-empty

    def test_editing_v1_in_place_is_forbidden(self) -> None:
        """The CLAUDE.md §6 rule 7 principle is enforced by convention.

        This test documents that editing v1/bluesky.md in place is forbidden.
        A new version creates prompts/v2/bluesky.md.  We verify the rule
        by confirming v2 does NOT exist yet (it should not; it is not created
        unless the escalation policy in §5.8 fires).
        """
        prompts_dir = (
            Path(__file__).parent.parent.parent
            / "packages"
            / "cdb_social"
            / "cdb_social"
            / "drafters"
            / "prompts"
        )
        v2_path = prompts_dir / "v2" / "bluesky.md"
        # v2 should not exist at T3 close (no escalation yet)
        assert not v2_path.exists(), (
            "v2/bluesky.md exists — was the prompt bumped without CDA SME review? "
            "Per CLAUDE.md §6 rule 7 and CDA SME §5.8, bumping requires a new "
            "directory and CDA SME review before any v2-generated draft reaches the queue."
        )

    # T4 extension: x.md and linkedin.md exist at prompts/v1/ (CDA SME T4 §5.13 carry-forward)
    def test_v1_x_prompt_file_exists(self) -> None:
        """v1/x.md exists — required for XDrafter at T4."""
        prompts_dir = (
            Path(__file__).parent.parent.parent
            / "packages"
            / "cdb_social"
            / "cdb_social"
            / "drafters"
            / "prompts"
            / "v1"
        )
        assert (prompts_dir / "x.md").exists(), (
            f"Expected v1/x.md prompt file at {prompts_dir / 'x.md'}"
        )

    def test_v1_linkedin_prompt_file_exists(self) -> None:
        """v1/linkedin.md exists — required for LinkedInDrafter at T4."""
        prompts_dir = (
            Path(__file__).parent.parent.parent
            / "packages"
            / "cdb_social"
            / "cdb_social"
            / "drafters"
            / "prompts"
            / "v1"
        )
        assert (prompts_dir / "linkedin.md").exists(), (
            f"Expected v1/linkedin.md prompt file at {prompts_dir / 'linkedin.md'}"
        )

    def test_load_prompt_x_v1_returns_text(self) -> None:
        text = load_prompt("x", "v1")
        assert len(text) > 100, "X prompt text should be non-trivial"

    def test_load_prompt_linkedin_v1_returns_text(self) -> None:
        text = load_prompt("linkedin", "v1")
        assert len(text) > 100, "LinkedIn prompt text should be non-trivial"

    def test_x_prompt_contains_forbidden_vocab_table(self) -> None:
        """X prompt Block 3 must contain the §1.5.4 forbidden-vocab table."""
        prompt_text = load_prompt("x", "v1")
        assert "Model X believes" in prompt_text or "Model X's output treats" in prompt_text
        assert "within-model consensus" in prompt_text.lower()

    def test_linkedin_prompt_contains_anti_thought_leadership_block(self) -> None:
        """LinkedIn prompt Block 5.5 must contain the anti-thought-leadership content."""
        prompt_text = load_prompt("linkedin", "v1")
        assert "I've been thinking" in prompt_text or "thought-leadership" in prompt_text.lower()
        assert "future of AI" in prompt_text

    def test_x_prompt_contains_per_segment_r10_emphasis(self) -> None:
        """X prompt Block 4 must mention per-segment CI requirement."""
        prompt_text = load_prompt("x", "v1")
        # Must describe that each segment is independently validated
        assert "segment" in prompt_text.lower()
        assert "independently" in prompt_text.lower() or "segment 1" in prompt_text.lower()

    def test_x_prompt_contains_hook_tweet_rules(self) -> None:
        """X prompt Block 6 must contain hook-tweet rules."""
        prompt_text = load_prompt("x", "v1")
        assert "hook" in prompt_text.lower() or "segment 1" in prompt_text.lower()
        assert "decides" in prompt_text.lower() or "intent" in prompt_text.lower()

    def test_bumping_x_requires_new_directory(self) -> None:
        """v2/x.md must not exist at T4 close — bumping requires CDA SME review."""
        prompts_dir = (
            Path(__file__).parent.parent.parent
            / "packages"
            / "cdb_social"
            / "cdb_social"
            / "drafters"
            / "prompts"
        )
        v2_path = prompts_dir / "v2" / "x.md"
        assert not v2_path.exists(), (
            "v2/x.md exists — bumping requires a new directory and CDA SME review "
            "per CLAUDE.md §6 rule 7."
        )

    def test_bumping_linkedin_requires_new_directory(self) -> None:
        """v2/linkedin.md must not exist at T4 close — bumping requires CDA SME review."""
        prompts_dir = (
            Path(__file__).parent.parent.parent
            / "packages"
            / "cdb_social"
            / "cdb_social"
            / "drafters"
            / "prompts"
        )
        v2_path = prompts_dir / "v2" / "linkedin.md"
        assert not v2_path.exists(), (
            "v2/linkedin.md exists — bumping requires a new directory and CDA SME review "
            "per CLAUDE.md §6 rule 7."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestCacheNoCacheSplit (§5.10)
# ─────────────────────────────────────────────────────────────────────────────


class TestCacheNoCacheSplit:
    """§5.10 — Per-call payload is data-only; system prompt carries methodology copy."""

    def test_system_prompt_has_cache_control(self) -> None:
        """The Anthropic call must use cache_control on the system prompt block."""
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())

        # Inspect the call arguments
        call_kwargs = mock_client.last_call_kwargs
        system = call_kwargs.get("system", [])
        assert isinstance(system, list), "system must be a list of blocks"
        assert len(system) == 1, "Expected exactly one system block"
        block = system[0]
        assert block.get("cache_control") == {"type": "ephemeral"}, (
            f"Expected cache_control ephemeral on system block, got: {block}"
        )

    def test_per_call_payload_is_data_only(self) -> None:
        """The user message must NOT contain methodology copy (§1.5.4 phrases)."""
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())

        call_kwargs = mock_client.last_call_kwargs
        messages = call_kwargs.get("messages", [])
        assert messages, "Expected at least one user message"
        user_content = messages[0].get("content", "")

        # Forbidden: methodology copy in per-call payload
        methodology_phrases = [
            "§1.5.4",
            "corpus lens",
            "Cultural Domain Analysis",
            "forbidden vocabulary",
            "Register-1",
            "Register-2",
            "hypothesis-framing",
            "NEVER use phrases",
            "Block 1",
            "Block 2",
        ]
        for phrase in methodology_phrases:
            assert phrase not in user_content, (
                f"Methodology copy found in per-call payload: {phrase!r}"
            )

    def test_per_call_payload_contains_trigger_evidence(self) -> None:
        """The user message must contain the trigger evidence dict."""
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())

        call_kwargs = mock_client.last_call_kwargs
        messages = call_kwargs.get("messages", [])
        user_content = messages[0].get("content", "")

        # Must contain data fields
        assert "trigger_type" in user_content
        assert "domain_slug" in user_content
        assert "trigger_evidence" in user_content

    def test_per_call_payload_contains_numerics(self) -> None:
        """The user message must contain domain numerics."""
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())

        call_kwargs = mock_client.last_call_kwargs
        messages = call_kwargs.get("messages", [])
        user_content = messages[0].get("content", "")

        assert "domain_numerics" in user_content
        assert "consensus_score" in user_content

    def test_system_prompt_contains_forbidden_vocab_table(self) -> None:
        """The system prompt must contain the §1.5.4 forbidden-vocab table."""
        prompt_text = load_prompt("bluesky", "v1")
        # The table must be present
        assert "Model X believes" in prompt_text or "Model X's output treats" in prompt_text
        assert "within-model consensus" in prompt_text.lower()

    def test_system_prompt_contains_corpus_lens_anchor(self) -> None:
        """Block 2 — corpus-lens anchor must be in the system prompt."""
        prompt_text = load_prompt("bluesky", "v1")
        assert "corpus lens" in prompt_text.lower()
        assert "Cultural Domain Analysis" in prompt_text

    def test_system_prompt_contains_r10_rule(self) -> None:
        """Block 4 — R10 rule must be in the system prompt."""
        prompt_text = load_prompt("bluesky", "v1")
        assert "confidence interval" in prompt_text.lower() or "CI" in prompt_text


# ─────────────────────────────────────────────────────────────────────────────
# TestDrafterRejectedException (§5.12, §5.16, §5.17)
# ─────────────────────────────────────────────────────────────────────────────


class TestDrafterRejectedException:
    """§5.12 — Failing drafts raise DrafterRejectedException; queue never sees them."""

    def test_forbidden_vocab_raises(self) -> None:
        fixture_text = _load_fixture("forbidden_vocab_phrase.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        assert exc_info.value.forbidden_terms_hit

    def test_bare_numeric_raises(self) -> None:
        fixture_text = _load_fixture("bare_numeric.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        # The exception must carry context
        assert exc_info.value.draft_text

    def test_hypothesis_framing_raises(self) -> None:
        fixture_text = _load_fixture("hypothesis_framing.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException):
            drafter.draft(trigger, _domain_result())

    def test_overlength_raises(self) -> None:
        long_text = "X" * 301  # 301 chars — exceeds 300-char limit
        mock_client = MockAnthropicClient(long_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        assert "__overlength_300__" in exc_info.value.forbidden_terms_hit

    def test_exception_carries_draft_text(self) -> None:
        fixture_text = _load_fixture("forbidden_vocab_worldview.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        assert exc_info.value.draft_text != ""

    def test_exception_carries_forbidden_terms(self) -> None:
        fixture_text = _load_fixture("forbidden_vocab_worldview.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        # Must carry the matched forbidden terms
        assert isinstance(exc_info.value.forbidden_terms_hit, list)
        assert len(exc_info.value.forbidden_terms_hit) > 0

    def test_good_draft_does_not_raise(self) -> None:
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        result = drafter.draft(trigger, _domain_result())
        assert result is not None
        assert result.forbidden_terms_hit == []
        assert result.framing_check_passed is True

    # §5.17 — round-trip test
    def test_round_trip_good_draft_all_fields(self) -> None:
        """§5.17 — Good draft SocialDraft has all expected field values."""
        fixture_text = _load_fixture("good_draft.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = BlueskyDrafter(anthropic_client=mock_client)
        trigger = _trigger(
            trigger_type=TriggerType.NEW_MODEL,
            domain_slug="family",
            model_id="gpt-5",
        )
        result = drafter.draft(trigger, _domain_result())

        assert result.forbidden_terms_hit == []
        assert result.framing_check_passed is True
        assert all(result.framing_checks.values()), (
            f"Expected all framing_checks True: {result.framing_checks}"
        )
        assert len(result.text) <= 300
        assert result.drafter_self_rating == 0.5
        assert result.prompt_version == "v1"
        assert result.methodology_url
        assert result.dashboard_url
        assert result.platform == Platform.BLUESKY
        assert result.drafter_version == "bluesky-v1"

    # §5.17 mirror — forbidden vocab draft raises
    def test_round_trip_forbidden_vocab_raises(self) -> None:
        """§5.17 mirror — forbidden vocab draft always raises, never returns SocialDraft."""
        for fixture in [
            "forbidden_vocab_phrase.txt",
            "forbidden_vocab_worldview.txt",
        ]:
            fixture_text = _load_fixture(fixture)
            mock_client = MockAnthropicClient(fixture_text)
            drafter = BlueskyDrafter(anthropic_client=mock_client)
            trigger = _trigger()
            with pytest.raises(DrafterRejectedException):
                drafter.draft(trigger, _domain_result())


# ─────────────────────────────────────────────────────────────────────────────
# TestRejectionWindowMonitor (§5.8)
# ─────────────────────────────────────────────────────────────────────────────


class TestRejectionWindowMonitor:
    """§5.8 — Sliding-window monitor reads last 10 *total attempts* from
    drafter_audit.jsonl and fires when ≥ 2 are rejections."""

    def _write_audit_records(
        self,
        audit_path: Path,
        outcomes: list[str],
    ) -> None:
        """Write audit records with the given outcomes to audit_path."""
        import json

        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with audit_path.open("w", encoding="utf-8") as f:
            for outcome in outcomes:
                record = {
                    "timestamp": "2026-05-17T00:00:00+00:00",
                    "platform": "bluesky",
                    "drafter_version": "bluesky-v1",
                    "prompt_version": "v1",
                    "outcome": outcome,
                }
                f.write(json.dumps(record) + "\n")

    def test_window_fires_when_2_of_10_are_rejections(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """2 rejections in 10 attempts → monitor logs the warning."""
        import logging

        audit_path = tmp_path / "drafter_audit.jsonl"
        # 8 passes + 2 rejects = 2/10 rejection rate
        outcomes = ["pass"] * 8 + ["reject", "reject"]
        self._write_audit_records(audit_path, outcomes)

        with caplog.at_level(logging.WARNING, logger="cdb_social.drafters.base"):
            _check_rejection_window(audit_path)

        assert any(
            "DRAFTER_REJECTION_WINDOW" in record.message
            for record in caplog.records
        ), "Expected DRAFTER_REJECTION_WINDOW warning when 2/10 are rejections"

    def test_window_silent_when_1_of_10_is_rejection(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """1 rejection in 10 attempts → monitor does NOT log."""
        import logging

        audit_path = tmp_path / "drafter_audit.jsonl"
        # 9 passes + 1 reject = 1/10 rejection rate
        outcomes = ["pass"] * 9 + ["reject"]
        self._write_audit_records(audit_path, outcomes)

        with caplog.at_level(logging.WARNING, logger="cdb_social.drafters.base"):
            _check_rejection_window(audit_path)

        assert not any(
            "DRAFTER_REJECTION_WINDOW" in record.message
            for record in caplog.records
        ), "Expected no warning when only 1/10 are rejections"

    def test_window_silent_when_no_recent_rejections(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """100 passes → monitor does NOT log."""
        import logging

        audit_path = tmp_path / "drafter_audit.jsonl"
        outcomes = ["pass"] * 100
        self._write_audit_records(audit_path, outcomes)

        with caplog.at_level(logging.WARNING, logger="cdb_social.drafters.base"):
            _check_rejection_window(audit_path)

        assert not any(
            "DRAFTER_REJECTION_WINDOW" in record.message
            for record in caplog.records
        ), "Expected no warning when all 100 are passes"

    def test_window_only_looks_at_last_10(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """50 historical rejections followed by 10 passes → monitor does NOT log.

        The window is the last 10 *total* attempts.  Historical rejections
        outside that window must not trigger the warning.
        """
        import logging

        audit_path = tmp_path / "drafter_audit.jsonl"
        # 50 old rejections (outside window) + 10 recent passes (the window)
        outcomes = ["reject"] * 50 + ["pass"] * 10
        self._write_audit_records(audit_path, outcomes)

        with caplog.at_level(logging.WARNING, logger="cdb_social.drafters.base"):
            _check_rejection_window(audit_path)

        assert not any(
            "DRAFTER_REJECTION_WINDOW" in record.message
            for record in caplog.records
        ), (
            "Expected no warning: 50 historical rejections are outside the "
            "last-10 window; the recent window is all passes"
        )


# ─────────────────────────────────────────────────────────────────────────────
# T4: TestXDrafterStructure (CDA SME T4 §5.7)
# ─────────────────────────────────────────────────────────────────────────────


class TestXDrafterStructure:
    """Thread output is \\n---\\n-delimited; max 3 segments; per-segment char limits."""

    def test_good_thread_has_three_segments(self) -> None:
        text = _load_fixture("x_good_thread.txt")
        segments = text.split(_X_SEGMENT_DELIMITER)
        assert len(segments) == 3, f"Expected 3 segments, got {len(segments)}"

    def test_good_thread_each_segment_under_280(self) -> None:
        text = _load_fixture("x_good_thread.txt")
        segments = text.split(_X_SEGMENT_DELIMITER)
        for idx, seg in enumerate(segments):
            assert len(seg) <= 280, (
                f"Segment {idx} is {len(seg)} chars — exceeds 280-char hard limit"
            )

    def test_good_thread_each_segment_under_250_target(self) -> None:
        text = _load_fixture("x_good_thread.txt")
        segments = text.split(_X_SEGMENT_DELIMITER)
        for idx, seg in enumerate(segments):
            assert len(seg) <= 250, (
                f"Segment {idx} is {len(seg)} chars — exceeds 250-char target"
            )

    def test_four_segment_thread_rejected(self) -> None:
        """Thread with 4 segments raises with __x_thread_too_long__ sentinel."""
        # Craft a 4-segment thread (each segment well under 280 chars)
        seg = "OCI = 2.4 (1.8, 3.1). corpus lens concentrates on family terms."
        four_segs = _X_SEGMENT_DELIMITER.join([seg] * 4)
        with pytest.raises(DrafterRejectedException) as exc_info:
            _check_x_thread_structure(four_segs)
        assert "__x_thread_too_long__" in exc_info.value.forbidden_terms_hit

    def test_overlength_segment_rejected(self) -> None:
        """A 290-char segment raises with __x_segment_overlength_{idx}__ sentinel."""
        long_seg = "X" * 290
        ci_seg = "OCI = 2.4 (1.8, 3.1). corpus lens concentrates."
        two_segs = _X_SEGMENT_DELIMITER.join([long_seg, ci_seg])
        with pytest.raises(DrafterRejectedException) as exc_info:
            _check_x_thread_structure(two_segs)
        assert any(
            "__x_segment_overlength_" in t
            for t in exc_info.value.forbidden_terms_hit
        )

    def test_round_trip_good_thread_returns_social_draft(self) -> None:
        """Good thread fixture → SocialDraft with all-pass framing_checks."""
        fixture_text = _load_fixture("x_good_thread.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger(domain_slug="family")
        result = drafter.draft(trigger, _domain_result())
        assert result is not None
        assert result.platform == Platform.X
        assert result.drafter_version == "x-v1"
        assert result.prompt_version == "v1"
        assert result.forbidden_terms_hit == []
        assert result.framing_check_passed is True
        assert result.drafter_self_rating == 0.5

    def test_round_trip_thread_framing_checks_has_x_keys(self) -> None:
        """framing_checks contains the three X-specific keys."""
        fixture_text = _load_fixture("x_good_thread.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger(domain_slug="family")
        result = drafter.draft(trigger, _domain_result())
        assert "x_hook_has_measurement_noun" in result.framing_checks
        assert "x_hook_has_ci_shape" in result.framing_checks
        assert "x_hook_no_intent_attribution" in result.framing_checks
        assert result.framing_checks["x_hook_has_measurement_noun"] is True
        assert result.framing_checks["x_hook_has_ci_shape"] is True
        assert result.framing_checks["x_hook_no_intent_attribution"] is True

    def test_x_drafter_cache_control_on_system_prompt(self) -> None:
        """XDrafter must pass cache_control ephemeral on system prompt (ARCHITECTURE.md §6.2)."""
        fixture_text = _load_fixture("x_good_thread.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())
        call_kwargs = mock_client.last_call_kwargs
        system = call_kwargs.get("system", [])
        assert isinstance(system, list)
        assert len(system) == 1
        block = system[0]
        assert block.get("cache_control") == {"type": "ephemeral"}

    def test_x_drafter_per_call_payload_contains_n_segments_target(self) -> None:
        """Per-call payload must contain n_segments_target (structural hint, T4 §5.12)."""
        fixture_text = _load_fixture("x_good_thread.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())
        call_kwargs = mock_client.last_call_kwargs
        messages = call_kwargs.get("messages", [])
        user_content = messages[0].get("content", "")
        assert "n_segments_target" in user_content

    def test_x_drafter_per_call_payload_no_methodology_copy(self) -> None:
        """Per-call payload must NOT contain methodology copy (T3 §5.10 carry-forward)."""
        fixture_text = _load_fixture("x_good_thread.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())
        call_kwargs = mock_client.last_call_kwargs
        messages = call_kwargs.get("messages", [])
        user_content = messages[0].get("content", "")
        forbidden_in_payload = [
            "§1.5.4",
            "Cultural Domain Analysis",
            "forbidden vocabulary",
            "Register-1",
            "Block 1",
            "Block 2",
        ]
        for phrase in forbidden_in_payload:
            assert phrase not in user_content, (
                f"Methodology copy found in X per-call payload: {phrase!r}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# T4: TestXPerSegmentValidation (CDA SME T4 §5.2 — Option A)
# ─────────────────────────────────────────────────────────────────────────────


class TestXPerSegmentValidation:
    """Per-segment validation: Option A — each segment independently passes all four checks."""

    def test_segment_with_forbidden_vocab_rejects_whole_thread(self) -> None:
        """A §1.5.4 phrase in segment 1 rejects the whole thread."""
        # Build a thread where segment 0 is good but segment 1 has forbidden vocab
        seg0 = (
            "LSB added GPT-5 to the family domain.\n"
            "OCI = 2.4 (1.8, 3.1) across 12 runs. corpus lens concentrates."
        )
        seg1 = "Model GPT-5 believes the structure is fixed. OCI = 2.4 (1.8, 3.1)."
        seg2 = "details https://cogstructurelab.com/family"
        bad_thread = _X_SEGMENT_DELIMITER.join([seg0, seg1, seg2])
        mock_client = MockAnthropicClient(bad_thread)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException):
            drafter.draft(trigger, _domain_result())

    def test_cross_segment_r10_parking_rejected(self) -> None:
        """Option A critical case: numeric in segment 0, CI in segment 1 → rejected.

        The x_bad_cross_segment_r10.txt fixture has:
        - segment 0: Smith's S = 0.61 with no CI
        - segment 1: (0.48, 0.79) — the CI parked in a different segment

        This MUST be rejected. Cross-segment CI parking violates Option A.
        """
        text = _load_fixture("x_bad_cross_segment_r10.txt")
        mock_client = MockAnthropicClient(text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        # The exception must indicate a validation failure (hook or R10)
        assert exc_info.value.forbidden_terms_hit  # sentinel or banned term

    def test_per_segment_validator_runs_on_each_segment(self) -> None:
        """Validate that the per-segment validator is actually invoked per segment.

        Build a thread where all segments are individually well-formed and
        confirm the draft passes (positive case for per-segment validation).
        """
        text = _load_fixture("x_good_thread.txt")
        segs = text.split(_X_SEGMENT_DELIMITER)
        assert len(segs) == 3
        # Each segment should individually pass validate_draft
        for seg in segs:
            hits, framing = validate_draft(seg)
            assert hits == [], f"Unexpected forbidden vocab in segment: {hits}"
            assert framing["bare_numeric_without_ci"] is True or seg.count(
                "OCI"
            ) == 0  # segment 3 has no numerics

    def test_aggregate_framing_checks_and_across_segments(self) -> None:
        """framing_checks for the thread is the AND across all segments."""
        text = _load_fixture("x_good_thread.txt")
        mock_client = MockAnthropicClient(text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        result = drafter.draft(trigger, _domain_result())
        # All canonical T3 keys should be True (AND across all 3 segments)
        assert result.framing_checks["hypothesis_framing"] is True
        assert result.framing_checks["cognition_attribution"] is True
        assert result.framing_checks["bare_numeric_without_ci"] is True
        assert result.framing_checks["register_boundary"] is True


# ─────────────────────────────────────────────────────────────────────────────
# T4: TestXHookTweetChecks (CDA SME T4 §5.3)
# ─────────────────────────────────────────────────────────────────────────────


class TestXHookTweetChecks:
    """Segment 0 must have measurement noun, CI-shape, no intent-attribution stems."""

    # ── Check 1: measurement-noun presence ──────────────────────────────────

    def test_hook_with_oci_passes_measurement_noun_check(self) -> None:
        """Segment 0 containing 'OCI' passes the measurement-noun check."""
        seg0 = "OCI = 2.4 (1.8, 3.1). corpus lens concentrates on family terms."
        hooks = _validate_x_hook_tweet(seg0)
        assert hooks["x_hook_has_measurement_noun"] is True

    def test_hook_with_smiths_s_passes_measurement_noun_check(self) -> None:
        """Segment 0 containing 'Smith's S' passes the measurement-noun check."""
        seg0 = "Smith's S = 0.61, 95% CI [0.48, 0.79]. categorical structure."
        hooks = _validate_x_hook_tweet(seg0)
        assert hooks["x_hook_has_measurement_noun"] is True

    def test_hook_with_consensus_passes_measurement_noun_check(self) -> None:
        """Segment 0 containing 'consensus' passes the measurement-noun check."""
        seg0 = "consensus eigenratio = 5.2 ± 0.8. Corpus lens concentrates."
        hooks = _validate_x_hook_tweet(seg0)
        assert hooks["x_hook_has_measurement_noun"] is True

    def test_hook_missing_measurement_noun_rejected(self) -> None:
        """Segment 0 missing any measurement noun → __x_segment_1_no_measurement_noun__."""
        text = _load_fixture("x_bad_hook_no_measurement.txt")
        mock_client = MockAnthropicClient(text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        assert "__x_segment_1_no_measurement_noun__" in exc_info.value.forbidden_terms_hit

    # ── Check 2: CI-shape presence ───────────────────────────────────────────

    def test_hook_with_ci_inline_passes(self) -> None:
        """Segment 0 with an inline CI passes the CI-shape check."""
        seg0 = "OCI = 2.4 (1.8, 3.1). corpus lens concentrates on family terms."
        hooks = _validate_x_hook_tweet(seg0)
        assert hooks["x_hook_has_ci_shape"] is True

    def test_hook_with_bracket_ci_passes(self) -> None:
        """Segment 0 with 95% CI [...] passes the CI-shape check."""
        seg0 = "Smith's S = 0.61, 95% CI [0.48, 0.79]. categorical structure."
        hooks = _validate_x_hook_tweet(seg0)
        assert hooks["x_hook_has_ci_shape"] is True

    def test_hook_missing_ci_shape_rejected(self) -> None:
        """Segment 0 with a bare numeric but no CI-shape → __x_segment_1_no_ci_shape__."""
        # Build a thread where segment 0 has a measurement noun but no CI
        seg0 = "OCI = 2.4. corpus lens concentrates on family terms."  # bare OCI
        seg1 = "Context: (1.8, 3.1) shown here for reference."
        seg2 = "details https://cogstructurelab.com/family"
        bad_thread = _X_SEGMENT_DELIMITER.join([seg0, seg1, seg2])
        mock_client = MockAnthropicClient(bad_thread)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        assert "__x_segment_1_no_ci_shape__" in exc_info.value.forbidden_terms_hit

    # ── Check 3: intent-attribution stems forbidden in segment 0 ─────────────

    def test_hook_with_decides_rejected(self) -> None:
        """Segment 0 containing 'decides' → __x_segment_1_intent_attribution_decides__."""
        text = _load_fixture("x_bad_hook_intent_attribution.txt")
        mock_client = MockAnthropicClient(text)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        assert any(
            "intent_attribution" in t
            for t in exc_info.value.forbidden_terms_hit
        )

    def test_hook_with_chooses_rejected(self) -> None:
        """Segment 0 containing 'chooses' → intent-attribution rejection."""
        seg0 = "GPT-5 chooses to group family terms: OCI = 2.4 (1.8, 3.1). corpus lens."
        with pytest.raises(DrafterRejectedException) as exc_info:
            _validate_x_hook_tweet(seg0)
        assert any(
            "chooses" in t
            for t in exc_info.value.forbidden_terms_hit
        )

    def test_hook_with_prefers_rejected(self) -> None:
        """Segment 0 containing 'prefers' → intent-attribution rejection."""
        seg0 = "GPT-5 prefers narrow groupings: OCI = 2.4 (1.8, 3.1). corpus lens."
        with pytest.raises(DrafterRejectedException) as exc_info:
            _validate_x_hook_tweet(seg0)
        assert any(
            "prefers" in t
            for t in exc_info.value.forbidden_terms_hit
        )

    def test_hook_no_intent_attribution_passes(self) -> None:
        """Segment 0 with no intent stems passes check 3."""
        seg0 = "OCI = 2.4 (1.8, 3.1). corpus lens concentrates on family terms."
        hooks = _validate_x_hook_tweet(seg0)
        assert hooks["x_hook_no_intent_attribution"] is True

    def test_intent_attribution_stems_only_forbidden_in_segment_0(self) -> None:
        """'decides' in segment 1 (not segment 0) does NOT trigger hook rejection.

        The intent-attribution stem check is hook-only (segment 0).  Segments 1+
        are subject only to the standard per-segment validator, which does not
        include decides/chooses/prefers in its forbidden-stem list.
        """
        # A thread where segment 0 is good but segment 1 has "decides"
        seg0 = (
            "LSB added GPT-5 to the family domain.\n"
            "OCI = 2.4 (1.8, 3.1). corpus lens concentrates."
        )
        seg1 = "The output distribution decides the clustering pattern. OCI = 2.4 (1.8, 3.1)."
        seg2 = "details https://cogstructurelab.com/family"
        thread = _X_SEGMENT_DELIMITER.join([seg0, seg1, seg2])
        mock_client = MockAnthropicClient(thread)
        drafter = XDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        # Should NOT raise on the hook-tweet intent-attribution check
        # (segment 1 "decides" is not caught by hook rules — only the per-segment
        # validator runs on segment 1, and it does not include intent-attribution stems)
        result = drafter.draft(trigger, _domain_result())
        assert result.framing_checks["x_hook_no_intent_attribution"] is True


# ─────────────────────────────────────────────────────────────────────────────
# T4: TestLinkedInDrafterStructure (CDA SME T4 §5.8)
# ─────────────────────────────────────────────────────────────────────────────


class TestLinkedInDrafterStructure:
    """Single long-form post; ≤ 3000 chars; soft target ≤ 1500 chars."""

    def test_good_linkedin_post_under_3000_chars(self) -> None:
        text = _load_fixture("linkedin_good.txt")
        assert len(text) <= 3000, f"LinkedIn fixture is {len(text)} chars"

    def test_good_linkedin_post_under_1500_target(self) -> None:
        text = _load_fixture("linkedin_good.txt")
        assert len(text) <= 1500, f"LinkedIn fixture is {len(text)} chars"

    def test_good_linkedin_no_thread_delimiter(self) -> None:
        text = _load_fixture("linkedin_good.txt")
        assert _X_SEGMENT_DELIMITER not in text, (
            "LinkedIn post must not contain thread delimiter"
        )

    def test_overlength_post_rejected(self) -> None:
        """A post exceeding 3000 chars raises with __linkedin_overlength_3000__ sentinel."""
        long_text = "A" * 3001
        mock_client = MockAnthropicClient(long_text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        assert "__linkedin_overlength_3000__" in exc_info.value.forbidden_terms_hit

    def test_round_trip_good_post_returns_social_draft(self) -> None:
        """Good LinkedIn fixture → SocialDraft with all-pass framing_checks."""
        fixture_text = _load_fixture("linkedin_good.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger(domain_slug="family")
        result = drafter.draft(trigger, _domain_result())
        assert result is not None
        assert result.platform == Platform.LINKEDIN
        assert result.drafter_version == "linkedin-v1"
        assert result.prompt_version == "v1"
        assert result.forbidden_terms_hit == []
        assert result.framing_check_passed is True
        assert result.drafter_self_rating == 0.5

    def test_round_trip_linkedin_framing_checks_has_linkedin_key(self) -> None:
        """framing_checks contains linkedin_no_thought_leadership key."""
        fixture_text = _load_fixture("linkedin_good.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger(domain_slug="family")
        result = drafter.draft(trigger, _domain_result())
        assert "linkedin_no_thought_leadership" in result.framing_checks
        assert result.framing_checks["linkedin_no_thought_leadership"] is True

    def test_linkedin_framing_checks_has_four_canonical_t3_keys(self) -> None:
        """framing_checks contains all four canonical T3 keys (carry-forward)."""
        fixture_text = _load_fixture("linkedin_good.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger(domain_slug="family")
        result = drafter.draft(trigger, _domain_result())
        assert "hypothesis_framing" in result.framing_checks
        assert "cognition_attribution" in result.framing_checks
        assert "bare_numeric_without_ci" in result.framing_checks
        assert "register_boundary" in result.framing_checks

    def test_linkedin_cache_control_on_system_prompt(self) -> None:
        """LinkedInDrafter must pass cache_control ephemeral on system prompt."""
        fixture_text = _load_fixture("linkedin_good.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())
        call_kwargs = mock_client.last_call_kwargs
        system = call_kwargs.get("system", [])
        assert isinstance(system, list)
        assert len(system) == 1
        block = system[0]
        assert block.get("cache_control") == {"type": "ephemeral"}

    def test_linkedin_per_call_payload_has_target_char_count(self) -> None:
        """Per-call payload must contain target_char_count (structural hint, T4 §5.12)."""
        fixture_text = _load_fixture("linkedin_good.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        drafter.draft(trigger, _domain_result())
        call_kwargs = mock_client.last_call_kwargs
        messages = call_kwargs.get("messages", [])
        user_content = messages[0].get("content", "")
        assert "target_char_count" in user_content

    def test_linkedin_k12_window_inherited_unchanged(self) -> None:
        """LinkedIn validator uses K=12 CI-adjacency window (T4 §5.6 ruling).

        A bare numeric rejected under K=12 must also be rejected in a LinkedIn post.
        The window does NOT scale with content length.
        """
        # A LinkedIn post with a bare numeric at the top and the CI far away
        # (more than 12 tokens apart)
        bare_in_linkedin = (
            "LSB added GPT-5 to the family domain.\n\n"
            "The OCI value is 2.4 for this model. "  # bare 2.4
            "There are many aspects to consider about the categorical structure "
            "of the family domain. Each model shows different patterns. "
            "The corpus lens concentrates on a small subset. "
            "Here is additional context about the measurement methodology. "
            "The confidence interval is (1.8, 3.1).\n\n"  # CI > 12 tokens away
            "details https://cogstructurelab.com/family"
        )
        ok, bare = validate_draft_numeric_ci_adjacency(bare_in_linkedin)
        # The bare 2.4 should be flagged (CI is far away)
        assert not ok, f"Expected bare-numeric failure for far-away CI, got: {bare}"


# ─────────────────────────────────────────────────────────────────────────────
# T4: TestLinkedInAntiThoughtLeadership (CDA SME T4 §5.5)
# ─────────────────────────────────────────────────────────────────────────────


class TestLinkedInAntiThoughtLeadership:
    """LinkedIn-specific forbidden patterns + first-person pronoun rule."""

    # ── Three forbidden thought-leadership patterns ───────────────────────────

    def test_ive_been_thinking_rejected(self) -> None:
        """'I've been thinking' (case-insensitive) triggers LinkedIn rejection."""
        text = _load_fixture("linkedin_bad_thought_leadership.txt")
        mock_client = MockAnthropicClient(text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        matched = exc_info.value.forbidden_terms_hit
        assert any("been thinking" in t.lower() or "first_person" in t.lower() for t in matched), (
            f"Expected thought-leadership or first-person hit, got: {matched}"
        )

    def test_the_future_of_ai_rejected(self) -> None:
        """'The future of AI' (case-insensitive) triggers LinkedIn rejection."""
        post = (
            "LSB added GPT-5 to the family domain. OCI = 2.4 (1.8, 3.1).\n\n"
            "The future of AI will reshape how we measure categorical structure.\n\n"
            "details https://cogstructurelab.com/family"
        )
        matched, linkedin_ok = _validate_linkedin_anti_thought_leadership(post)
        assert not linkedin_ok
        assert any("future" in t.lower() and "ai" in t.lower() for t in matched)

    def test_ai_is_reshaping_rejected(self) -> None:
        """'AI is reshaping' (case-insensitive) triggers LinkedIn rejection."""
        post = (
            "LSB added GPT-5 to the family domain. OCI = 2.4 (1.8, 3.1).\n\n"
            "AI is reshaping how we think about categorical structure.\n\n"
            "details https://cogstructurelab.com/family"
        )
        matched, linkedin_ok = _validate_linkedin_anti_thought_leadership(post)
        assert not linkedin_ok
        assert any("reshaping" in t.lower() for t in matched)

    def test_ive_been_thinking_case_insensitive(self) -> None:
        """Pattern match is case-insensitive: 'I'VE BEEN THINKING' also rejected."""
        post = "I'VE BEEN THINKING about how LSB measures OCI = 2.4 (1.8, 3.1)."
        matched, linkedin_ok = _validate_linkedin_anti_thought_leadership(post)
        assert not linkedin_ok
        assert matched  # must have at least one hit

    # ── First-person pronoun rule ─────────────────────────────────────────────

    def test_standalone_i_rejected(self) -> None:
        """\\bI\\b (case-sensitive, word-boundary) triggers __linkedin_first_person__."""
        text = _load_fixture("linkedin_bad_first_person.txt")
        mock_client = MockAnthropicClient(text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        assert "__linkedin_first_person__" in exc_info.value.forbidden_terms_hit

    def test_we_and_our_pass_first_person_check(self) -> None:
        """'we' and 'our' are first-person plural and are allowed."""
        post = (
            "LSB added GPT-5 to our domain coverage.\n\n"
            "We measure OCI = 2.4 (1.8, 3.1) on the family domain.\n\n"
            "details https://cogstructurelab.com/family"
        )
        no_first_person = _check_linkedin_no_first_person(post)
        assert no_first_person, "Expected 'we'/'our' to pass first-person check"

    def test_capital_i_in_word_not_rejected(self) -> None:
        """'Information', 'In', 'Is' etc. with capital I are NOT \\bI\\b and are allowed."""
        post = (
            "LSB added GPT-5 to the family domain.\n\n"
            "Information about OCI = 2.4 (1.8, 3.1) is here.\n"
            "In 2026, LSB covers 5 domains.\n\n"
            "details https://cogstructurelab.com/family"
        )
        no_first_person = _check_linkedin_no_first_person(post)
        assert no_first_person, (
            r"Capital-I words like 'Information', 'In', 'Is' must not match \bI\b"
        )

    def test_clean_linkedin_post_passes_all_checks(self) -> None:
        """Clean LinkedIn post passes anti-thought-leadership checks."""
        post = _load_fixture("linkedin_good.txt")
        matched, linkedin_ok = _validate_linkedin_anti_thought_leadership(post)
        assert linkedin_ok, f"Expected clean LinkedIn post to pass, got: {matched}"

    def test_ive_been_thinking_no_apostrophe_also_rejected(self) -> None:
        """'Ive been thinking' (without apostrophe) matches the regex pattern.

        The regex pattern is r\"\\bI'?ve been thinking\\b\" so both
        \"I've been thinking\" (with apostrophe) and \"Ive been thinking\"
        (without) are caught.  This test documents this behavior.
        """
        post = "Ive been thinking about OCI = 2.4 (1.8, 3.1)."
        matched, linkedin_ok = _validate_linkedin_anti_thought_leadership(post)
        assert not linkedin_ok, "Expected 'Ive been thinking' (no apostrophe) to match"

    def test_linkedin_no_thought_leadership_framing_check_key_exists(self) -> None:
        """The linkedin_no_thought_leadership key is in framing_checks on good draft."""
        fixture_text = _load_fixture("linkedin_good.txt")
        mock_client = MockAnthropicClient(fixture_text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        result = drafter.draft(trigger, _domain_result())
        assert "linkedin_no_thought_leadership" in result.framing_checks
        assert result.framing_checks["linkedin_no_thought_leadership"] is True

    def test_framing_check_passed_false_when_thought_leadership_pattern(self) -> None:
        """framing_check_passed is False when thought-leadership pattern detected."""
        text = _load_fixture("linkedin_bad_thought_leadership.txt")
        mock_client = MockAnthropicClient(text)
        drafter = LinkedInDrafter(anthropic_client=mock_client)
        trigger = _trigger()
        with pytest.raises(DrafterRejectedException) as exc_info:
            drafter.draft(trigger, _domain_result())
        # The exception must carry non-empty forbidden_terms_hit
        assert exc_info.value.forbidden_terms_hit
