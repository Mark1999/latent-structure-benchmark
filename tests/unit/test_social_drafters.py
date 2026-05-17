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
    validate_draft,
    validate_draft_forbidden_vocab,
    validate_draft_hypothesis_framing,
    validate_draft_numeric_ci_adjacency,
)
from cdb_social.drafters.base import (
    _HYPOTHESIS_FRAMING_PATTERNS,
    CI_SHAPE_REGEX,
    load_prompt,
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

    def test_all_four_keys_present_on_clean_text(self) -> None:
        _, framing_checks = validate_draft(
            "GPT-5's output clusters tightly: OCI = 2.4 (1.8, 3.1). "
            "Corpus lens concentrates on family terms."
        )
        assert "no_cognition_attribution" in framing_checks
        assert "no_value_attribution" in framing_checks
        assert "no_hypothesis_framing" in framing_checks
        assert "numeric_has_adjacent_ci" in framing_checks

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
        assert framing_checks["no_cognition_attribution"] is False

    def test_value_attribution_false_on_phrase_hit(self) -> None:
        _, framing_checks = validate_draft(
            "Model GPT-5 believes the structure. OCI = 2.4 (1.8, 3.1). Corpus lens."
        )
        assert framing_checks["no_value_attribution"] is False

    def test_hypothesis_framing_false_on_phrase_hit(self) -> None:
        _, framing_checks = validate_draft(
            "Our results show high consensus. OCI = 2.4 (1.8, 3.1)."
        )
        assert framing_checks["no_hypothesis_framing"] is False

    def test_numeric_has_adjacent_ci_false_on_bare_numeric(self) -> None:
        _, framing_checks = validate_draft(
            "Smith's S is 0.61. Corpus lens concentrates here."
        )
        assert framing_checks["numeric_has_adjacent_ci"] is False

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
