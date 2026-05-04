"""Unit tests for apps/ops_dashboard/lib/qa_interpreter.py (OPS-T7).

All tests use synthetic qa_notes strings constructed in-memory.
No real API calls. No reads from data/raw/*.jsonl.

QI-T5 / QI-T6 / QI-T12 use the CDA SME option (iii) expected counts:
  QI-T5  "247348ms; 4779"  -> 2 codes [latency_exceeded, token_inconsistency_or_campaign_tag]
  QI-T6  "0; 71000ms; 171" -> 3 codes [freelist_too_low, latency_exceeded,
                                        token_inconsistency_or_campaign_tag]
  QI-T12 "4779"            -> 1 code  [freelist_too_low]

See docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md §Q1 (option iii).

Forbidden-vocabulary patterns follow CLAUDE.md §7 / ARCHITECTURE.md §1.5.4.
"""

from __future__ import annotations

import re

import pytest

from apps.ops_dashboard.lib.qa_interpreter import (  # noqa: E402
    _INTERPRETATION_TABLE,
    QaInterpretation,
    interpret_qa_notes,
)

# ── Forbidden vocabulary patterns (CLAUDE.md §7 / ARCHITECTURE.md §1.5.4) ────

_FORBIDDEN_PATTERNS: list[str] = [
    r"\bbelieves\b",
    r"\bModel X believes",
    r"\bModel X thinks of",
    r"\bHow models see the world\b",
    r"\bModel X'?s worldview\b",
    r"\bworldview\b",
    r"\bCultural bias\b",
    r"\bWhat the model understands\b",
    r"\bwithin-model consensus\b",
    r"\bwithin-model eigenratio\b",
    r"\bwithin-model CCM\b",
]


# ── QI-T1: empty string → 0 interpretations ──────────────────────────────────

class TestQIT1EmptyString:
    def test_empty_string_returns_empty_list(self) -> None:
        """QI-T1: empty qa_notes string returns []."""
        result = interpret_qa_notes("")
        assert result == []

    def test_whitespace_only_returns_empty_list(self) -> None:
        """QI-T1 variant: whitespace-only qa_notes returns []."""
        result = interpret_qa_notes("   ")
        assert result == []


# ── QI-T2: latency shorthand ─────────────────────────────────────────────────

class TestQIT2Latency:
    def test_latency_single(self) -> None:
        """QI-T2: '60124ms' -> 1 interpretation with code latency_exceeded."""
        result = interpret_qa_notes("60124ms")
        assert len(result) == 1
        assert result[0].code == "latency_exceeded"
        assert result[0].raw_segment == "60124ms"

    def test_latency_large_value(self) -> None:
        """QI-T2 variant: '247348ms' -> 1 interpretation with code latency_exceeded."""
        result = interpret_qa_notes("247348ms")
        assert len(result) == 1
        assert result[0].code == "latency_exceeded"


# ── QI-T3: label_count_mismatch shorthand ────────────────────────────────────

class TestQIT3LabelCountMismatch:
    def test_label_count_mismatch_single(self) -> None:
        """QI-T3: 'label_count_mismatch:20/9' -> 1 interpretation."""
        result = interpret_qa_notes("label_count_mismatch:20/9")
        assert len(result) == 1
        assert result[0].code == "label_count_mismatch"
        assert result[0].raw_segment == "label_count_mismatch:20/9"


# ── QI-T4: latency + label_count_mismatch ────────────────────────────────────

class TestQIT4MultipleDistinct:
    def test_latency_plus_label_count_mismatch(self) -> None:
        """QI-T4: '60124ms; label_count_mismatch:16/81' -> 2 interpretations."""
        result = interpret_qa_notes("60124ms; label_count_mismatch:16/81")
        assert len(result) == 2
        codes = [r.code for r in result]
        assert codes == ["latency_exceeded", "label_count_mismatch"]


# ── QI-T5: latency + trailing bare integer (SME option iii: ambiguous) ───────

class TestQIT5LatencyPlusCampaignTag:
    def test_latency_then_trailing_bare_int(self) -> None:
        """QI-T5: '247348ms; 4779' -> 2 interpretations per SME option (iii).

        Trailing bare integer after another shorthand -> token_inconsistency_or_campaign_tag.
        """
        result = interpret_qa_notes("247348ms; 4779")
        assert len(result) == 2
        codes = [r.code for r in result]
        assert codes == ["latency_exceeded", "token_inconsistency_or_campaign_tag"]

    def test_trailing_segment_contains_both_readings(self) -> None:
        """QI-T5: The ambiguous trailing segment's impact text must name both
        possible readings (token inconsistency and campaign-id tag)."""
        result = interpret_qa_notes("247348ms; 4779")
        ambiguous = result[1]
        assert "token" in ambiguous.impact.lower() or "heuristic" in ambiguous.impact.lower()
        assert "campaign" in ambiguous.impact.lower()


# ── QI-T6: bare int + latency + trailing bare int ────────────────────────────

class TestQIT6ZeroItemsLatencyCampaignTag:
    def test_three_segments_three_codes(self) -> None:
        """QI-T6: '0; 71000ms; 171' -> 3 interpretations per SME option (iii).

        '0' is the first segment and the only bare int before other shorthands
        -> freelist_too_low.
        '71000ms' -> latency_exceeded.
        '171' is a trailing bare int after other shorthands -> token_inconsistency_or_campaign_tag.
        """
        result = interpret_qa_notes("0; 71000ms; 171")
        assert len(result) == 3
        codes = [r.code for r in result]
        assert codes == [
            "freelist_too_low",
            "latency_exceeded",
            "token_inconsistency_or_campaign_tag",
        ]


# ── QI-T7: label_count_mismatch near-equal counts ────────────────────────────

class TestQIT7LabelCountNearEqual:
    def test_near_equal_mismatch(self) -> None:
        """QI-T7: 'label_count_mismatch:64/63' -> 1 interpretation."""
        result = interpret_qa_notes("label_count_mismatch:64/63")
        assert len(result) == 1
        assert result[0].code == "label_count_mismatch"


# ── QI-T8: empty_request_id ──────────────────────────────────────────────────

class TestQIT8EmptyRequestId:
    def test_empty_literal(self) -> None:
        """QI-T8: 'empty' -> 1 interpretation with code empty_request_id."""
        result = interpret_qa_notes("empty")
        assert len(result) == 1
        assert result[0].code == "empty_request_id"
        assert result[0].raw_segment == "empty"


# ── QI-T9: uniqueness_too_low ────────────────────────────────────────────────

class TestQIT9UniquenessTooLow:
    def test_percentage_segment(self) -> None:
        """QI-T9: '12.3%' -> 1 interpretation with code uniqueness_too_low."""
        result = interpret_qa_notes("12.3%")
        assert len(result) == 1
        assert result[0].code == "uniqueness_too_low"
        assert result[0].raw_segment == "12.3%"

    def test_integer_percentage(self) -> None:
        """QI-T9 variant: '8%' -> 1 interpretation with code uniqueness_too_low."""
        result = interpret_qa_notes("8%")
        assert len(result) == 1
        assert result[0].code == "uniqueness_too_low"


# ── QI-T10: matrix_non_binary ────────────────────────────────────────────────

class TestQIT10MatrixNonBinary:
    def test_found_integer(self) -> None:
        """QI-T10: 'found 2' -> 1 interpretation with code matrix_non_binary."""
        result = interpret_qa_notes("found 2")
        assert len(result) == 1
        assert result[0].code == "matrix_non_binary"
        assert result[0].raw_segment == "found 2"

    def test_found_negative(self) -> None:
        """QI-T10 variant: 'found -1' -> 1 interpretation with code matrix_non_binary."""
        result = interpret_qa_notes("found -1")
        assert len(result) == 1
        assert result[0].code == "matrix_non_binary"


# ── QI-T11: matrix_asymmetric ────────────────────────────────────────────────

class TestQIT11MatrixAsymmetric:
    def test_not_equal_pattern(self) -> None:
        """QI-T11: '0 != 1' -> 1 interpretation with code matrix_asymmetric."""
        result = interpret_qa_notes("0 != 1")
        assert len(result) == 1
        assert result[0].code == "matrix_asymmetric"
        assert result[0].raw_segment == "0 != 1"


# ── QI-T12: bare integer alone (SME option iii: freelist_too_low) ─────────────

class TestQIT12BareIntAlone:
    def test_bare_int_only_segment(self) -> None:
        """QI-T12: '4779' alone -> 1 interpretation with code freelist_too_low.

        Per SME option (iii): bare integer as the only segment -> freelist_too_low.
        """
        result = interpret_qa_notes("4779")
        assert len(result) == 1
        assert result[0].code == "freelist_too_low"

    def test_zero_only_segment(self) -> None:
        """QI-T12 variant: '0' alone -> freelist_too_low."""
        result = interpret_qa_notes("0")
        assert len(result) == 1
        assert result[0].code == "freelist_too_low"

    def test_seven_only_segment(self) -> None:
        """QI-T12 variant: '7' alone -> freelist_too_low."""
        result = interpret_qa_notes("7")
        assert len(result) == 1
        assert result[0].code == "freelist_too_low"


# ── QI-T13: unknown shorthand ────────────────────────────────────────────────

class TestQIT13UnknownShorthand:
    def test_unrecognised_segment(self) -> None:
        """QI-T13: unrecognised shorthand -> 1 interpretation with code 'unknown'."""
        result = interpret_qa_notes("some unknown shorthand xyz")
        assert len(result) == 1
        assert result[0].code == "unknown"
        assert result[0].raw_segment == "some unknown shorthand xyz"


# ── QI-T14: forbidden-vocabulary scan over all table strings ─────────────────

class TestQIT14ForbiddenVocabularyScan:
    """All why/impact strings in the interpretation table must pass the
    forbidden-vocabulary check (CLAUDE.md §7 / ARCHITECTURE.md §1.5.4)."""

    def _all_table_strings(self) -> list[str]:
        """Collect all why and impact strings from _INTERPRETATION_TABLE."""
        strings: list[str] = []
        for _pattern, _code, why, impact in _INTERPRETATION_TABLE:
            strings.append(why)
            strings.append(impact)
        # Also collect from interpret_qa_notes output for all recognised codes
        test_inputs = [
            "60124ms",
            "label_count_mismatch:20/9",
            "12.3%",
            "found 2",
            "0 != 1",
            "empty",
            "0",          # freelist_too_low (only segment)
            "247348ms; 4779",  # includes token_inconsistency_or_campaign_tag
            "some unknown xyz",
        ]
        for qa_notes in test_inputs:
            for interp in interpret_qa_notes(qa_notes):
                strings.append(interp.why)
                strings.append(interp.impact)
        return strings

    @pytest.mark.parametrize("pattern", _FORBIDDEN_PATTERNS)
    def test_no_forbidden_vocabulary_in_table(self, pattern: str) -> None:
        """No forbidden-vocabulary pattern appears in any why/impact string."""
        rx = re.compile(pattern, re.IGNORECASE)
        for s in self._all_table_strings():
            assert not rx.search(s), (
                f"Forbidden pattern {pattern!r} found in interpretation table "
                f"string: {s!r}"
            )


# ── QI-T15: determinism ──────────────────────────────────────────────────────

class TestQIT15Determinism:
    """Two calls on the same input must return equal lists."""

    @pytest.mark.parametrize("qa_notes", [
        "",
        "60124ms",
        "label_count_mismatch:20/9",
        "12.3%",
        "found 2",
        "0 != 1",
        "empty",
        "0",
        "247348ms; 4779",
        "0; 71000ms; 171",
        "4779",
        "some unknown xyz",
        "60124ms; label_count_mismatch:16/81",
    ])
    def test_deterministic(self, qa_notes: str) -> None:
        """interpret_qa_notes is deterministic across two calls."""
        first = interpret_qa_notes(qa_notes)
        second = interpret_qa_notes(qa_notes)
        assert len(first) == len(second), (
            f"Non-deterministic length: {len(first)} vs {len(second)} "
            f"for input {qa_notes!r}"
        )
        for a, b in zip(first, second, strict=True):
            assert a.code == b.code
            assert a.why == b.why
            assert a.impact == b.impact
            assert a.raw_segment == b.raw_segment


# ── Additional edge-case tests ────────────────────────────────────────────────

class TestAdditionalEdgeCases:
    def test_raw_segment_preserved_verbatim(self) -> None:
        """The raw_segment field must equal the original segment from qa_notes."""
        result = interpret_qa_notes("60124ms; label_count_mismatch:20/9")
        assert result[0].raw_segment == "60124ms"
        assert result[1].raw_segment == "label_count_mismatch:20/9"

    def test_qa_interpretation_is_dataclass(self) -> None:
        """QaInterpretation is a dataclass with the four required fields."""
        qi = QaInterpretation(
            code="test_code",
            why="test why",
            impact="test impact",
            raw_segment="test_raw",
        )
        assert qi.code == "test_code"
        assert qi.why == "test why"
        assert qi.impact == "test impact"
        assert qi.raw_segment == "test_raw"

    def test_multiple_semicolons_separated_correctly(self) -> None:
        """Multiple segments separated by '; ' are each classified independently."""
        result = interpret_qa_notes("empty; 12.3%; found 2")
        assert len(result) == 3
        assert result[0].code == "empty_request_id"
        assert result[1].code == "uniqueness_too_low"
        assert result[2].code == "matrix_non_binary"

    def test_campaign_tag_only_maps_to_freelist_too_low(self) -> None:
        """A bare integer alone (even a large one like '4779') maps to freelist_too_low.

        Per SME option (iii): only-segment bare integer -> freelist_too_low.
        This is the transitional heuristic; in practice the campaign-id tag only
        appears in a trailing position, so the only-segment case is almost always
        a genuine freelist_too_low.
        """
        result = interpret_qa_notes("171")
        assert len(result) == 1
        assert result[0].code == "freelist_too_low"


# ── QI-T16: verbatim SME binding-edit impact strings ─────────────────────────


class TestQIT16VerbatimSMEImpactStrings:
    """Assert that the three SME Q1 binding-edit impact strings appear verbatim
    in the output of interpret_qa_notes.

    The SME verdict (docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md §Q1)
    mandated specific replacement text for three rows:
    - freelist_too_low: "Operator should exclude or flag"
    - uniqueness_too_low: "independent elicitation across runs"
    - token_inconsistency_or_campaign_tag: "chars/4 heuristic"

    QI-T14 scans for *forbidden* vocabulary; this class asserts the *required*
    replacement text is present verbatim (not just substring-of-category).
    """

    def test_freelist_too_low_impact_operator_should_exclude(self) -> None:
        """QI-T16a: freelist_too_low impact must contain the SME Q1 binding text
        'Operator should exclude or flag this run when computing grouped salience'.

        Rationale (SME Q1): the original 'Excluded from grouped salience aggregates'
        overstates what qa_passed=False does; the corrected text makes clear the
        flag is operator-actionable advice, not automated filtering.
        """
        result = interpret_qa_notes("0")  # bare integer only-segment
        assert len(result) == 1
        assert result[0].code == "freelist_too_low"
        assert "Operator should exclude or flag this run" in result[0].impact, (
            "QI-T16a: SME Q1 binding text 'Operator should exclude or flag this run' "
            f"not found in freelist_too_low impact. Got: {result[0].impact!r}"
        )
        assert "does not currently filter on" in result[0].impact, (
            "QI-T16a: SME Q1 binding text 'does not currently filter on' "
            f"not found in freelist_too_low impact. Got: {result[0].impact!r}"
        )

    def test_uniqueness_too_low_impact_independent_elicitation(self) -> None:
        """QI-T16b: uniqueness_too_low impact must contain the SME Q1 binding text
        'independent elicitation across runs'.

        Rationale (SME Q1): 'informed elicitation' was §1.5-adjacent; the
        corrected phrase is statistically descriptive and clean.
        """
        result = interpret_qa_notes("12.3%")
        assert len(result) == 1
        assert result[0].code == "uniqueness_too_low"
        assert "independent elicitation across runs" in result[0].impact, (
            "QI-T16b: SME Q1 binding text 'independent elicitation across runs' "
            f"not found in uniqueness_too_low impact. Got: {result[0].impact!r}"
        )
        assert ">=2 runs" in result[0].impact, (
            "QI-T16b: SME Q1 binding text '>=2 runs' "
            f"not found in uniqueness_too_low impact. Got: {result[0].impact!r}"
        )

    def test_token_inconsistency_impact_chars4_heuristic(self) -> None:
        """QI-T16c: token_inconsistency_or_campaign_tag impact must contain the
        SME Q1 binding text 'chars/4 heuristic'.

        Rationale (SME Q1): the original gave equal weight to non-ASCII and
        provider-side anomaly; the corrected text is honest that the heuristic
        is the loose part, not the provider count.
        """
        result = interpret_qa_notes("247348ms; 4779")  # trailing bare int = ambiguous
        assert len(result) == 2
        ambiguous = result[1]
        assert ambiguous.code == "token_inconsistency_or_campaign_tag"
        assert "chars/4" in ambiguous.impact, (
            "QI-T16c: SME Q1 binding text 'chars/4' "
            f"not found in token_inconsistency_or_campaign_tag impact. "
            f"Got: {ambiguous.impact!r}"
        )
        assert "campaign" in ambiguous.impact.lower(), (
            "QI-T16c: 'campaign' not found in token_inconsistency_or_campaign_tag "
            f"impact. Got: {ambiguous.impact!r}"
        )

    def test_freelist_too_low_impact_no_automated_exclusion_claim(self) -> None:
        """QI-T16d (negative): the rejected 'Excluded from grouped salience aggregates'
        phrase must NOT appear in the freelist_too_low impact.

        Guards against future drift back to the pre-SME-edit wording that overstated
        what qa_passed=False does. SME Q1 explicitly replaced this phrase.
        """
        result = interpret_qa_notes("7")
        assert len(result) == 1
        assert result[0].code == "freelist_too_low"
        assert "Excluded from grouped salience aggregates" not in result[0].impact, (
            "QI-T16d: rejected pre-SME text 'Excluded from grouped salience "
            "aggregates' found in freelist_too_low impact. SME Q1 binding "
            "replaced this with operator-advisory language."
        )
