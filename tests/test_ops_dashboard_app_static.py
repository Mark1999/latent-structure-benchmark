"""Static-text assertions on apps/ops_dashboard/app.py (OPS-T4 / OPS-T5).

These tests do NOT import or execute app.py as a Streamlit application.
They read it as a plain text file and assert that the CDA SME-mandated
copy strings are present verbatim.

Rationale: Streamlit apps cannot be unit-tested by importing (the
`st.*` calls run at import time against a missing server context).
Static-text grep is the only way to guard against accidental copy drift
without spinning up a live Streamlit server.

CDA SME notes verified here:
- Note 1 (OPS-T4): Section 2 verbatim-provenance header.
- Note 4 (OPS-T4): Section 3 model-attribution disclaimer.
- Note 5 (OPS-T4): Empty-freelist banner with exact SME-approved wording.
- Q1 (OPS-T5): Section 4 disclaimer wording.
- Q2 (OPS-T5): "Extended-thinking output (verbatim)" subheader inside expanders.
- Q3 (OPS-T5): Empty-thinking placeholder text.
- Q4 (OPS-T5): Section 4 title "### Raw transcripts".

No real API calls. No reads from data/. All assertions are on the
source file at a known absolute path.

See docs/status/2026-05-01-ops-wireframes-cda-sme-verdict.md for OPS-T4
binding SME note text. Coverage point #24.
See docs/status/2026-05-02-OPS-T5-cda-sme-verdict.md for OPS-T5
binding SME note text.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_APP_PY = Path(__file__).resolve().parents[1] / "apps" / "ops_dashboard" / "app.py"
_DETAIL_PY = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "ops_dashboard"
    / "lib"
    / "detail.py"
)
_QA_INTERPRETER_PY = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "ops_dashboard"
    / "lib"
    / "qa_interpreter.py"
)


@pytest.fixture(scope="module")
def app_source() -> str:
    """Return the full source text of app.py."""
    return _APP_PY.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def detail_source() -> str:
    """Return the full source text of lib/detail.py."""
    return _DETAIL_PY.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def qa_interpreter_source() -> str:
    """Return the full source text of lib/qa_interpreter.py."""
    return _QA_INTERPRETER_PY.read_text(encoding="utf-8")


class TestSMEMandatedCopy:
    """Verify that the exact SME-required strings are present in app.py.

    Each test is independent; a missing string is a FAIL for that note.
    """

    def test_empty_freelist_banner_exact_wording(self, app_source: str) -> None:
        """Note 5: empty-freelist banner must contain the SME-mandated text:
        '0 items elicited. The pile-sort prompt for this informant was
        constructed with 0 items of input — see Section 2.'

        The SME explicitly rejected 'upstream empty-input propagation' framing
        (Q5 FAIL in verdict) and mandated this strictly factual replacement.

        The string is split across two source lines in app.py (Python implicit
        string concatenation), so we test each fragment independently rather
        than the joined runtime string.
        """
        fragment_1 = "0 items elicited. The pile-sort prompt for this informant was"
        fragment_2 = "constructed with 0 items of input"
        fragment_3 = "see Section 2."
        for frag in (fragment_1, fragment_2, fragment_3):
            assert frag in app_source, (
                f"SME-mandated empty-freelist banner (Note 5): fragment not found "
                f"in app.py.\nMissing fragment:\n  {frag!r}"
            )

    def test_empty_freelist_banner_no_propagation_claim(
        self, app_source: str
    ) -> None:
        """Note 5 (negative): the rejected 'upstream empty-input propagation'
        wording must NOT appear in the empty-freelist banner context.

        The SME ruled this overclaims (Q5 FAIL).  Guard against future drift.
        """
        assert "upstream empty-input propagation" not in app_source, (
            "Rejected SME wording 'upstream empty-input propagation' found in "
            "app.py.  The SME ruled this overclaims (Note 5 FAIL in OPS-T4 "
            "verdict).  Remove it."
        )

    def test_section2_verbatim_provenance_header(self, app_source: str) -> None:
        """Note 1: Section 2 must carry a verbatim-provenance header.

        The SME required one unobtrusive line clarifying that pile labels and
        member ordering are the model's own verbatim output.
        """
        required = (
            "Pile labels and member ordering are the model’s own output, verbatim."
        )
        # Also accept the ASCII apostrophe variant in case the editor normalised it
        required_ascii = (
            "Pile labels and member ordering are the model's own output, verbatim."
        )
        assert required in app_source or required_ascii in app_source, (
            f"SME-mandated Section 2 verbatim-provenance header (Note 1) not found "
            f"in app.py.\nExpected (unicode or ascii apostrophe):\n  {required_ascii!r}"
        )

    def test_section3_model_attribution_disclaimer(self, app_source: str) -> None:
        """Note 4: Section 3 must carry a model-attribution disclaimer above the
        verbatim refusal text.

        The SME required a static one-time caption at the top of Section 3 so
        the dashboard is not read as endorsing the model’s framing.  The actual
        text in app.py is:
        ‘*The verbatim text below contains the model’s stated attributions.
         Any claims about reality are the model’s attributions, not facts.*’
        """
        # Two core phrases from the SME Note 4 disclaimer
        required_phrase_1 = "stated attributions"
        required_phrase_2 = "attributions, not facts"
        assert required_phrase_1 in app_source, (
            f"SME-mandated Section 3 disclaimer (Note 4) missing phrase "
            f"{required_phrase_1!r} in app.py."
        )
        assert required_phrase_2 in app_source, (
            f"SME-mandated Section 3 disclaimer (Note 4) missing phrase "
            f"{required_phrase_2!r} in app.py."
        )


class TestOPST5MandatedCopy:
    """Verify OPS-T5 CDA SME-required strings are present in app.py / detail.py.

    Disclaimer, placeholder, section title, and subheader are literals in
    app.py and are checked against app_source.  Expander labels are defined
    as step_label literals in lib/detail.py (app.py renders them via
    _step.step_label at runtime) and are checked against detail_source.

    Each test maps to a specific SME verdict item.
    See docs/status/2026-05-02-OPS-T5-cda-sme-verdict.md.
    """

    def test_section4_title(self, app_source: str) -> None:
        """Q4: Section 4 title must be ‘### Raw transcripts’."""
        required = "### Raw transcripts"
        assert required in app_source, (
            f"OPS-T5 Q4: Section 4 title {required!r} not found in app.py."
        )

    def test_section4_disclaimer_q1(self, app_source: str) -> None:
        """Q1: Section 4 disclaimer must contain the SME-approved wording
        (verified in fragments to tolerate line-wrap in source).

        Full approved text:
        ‘Verbatim model output below — prompts as sent, model output text as
        returned. Extended-thinking text is the model’s literal output, not a
        claim about internal reasoning.’
        """
        fragment_1 = "Verbatim model output below"
        fragment_2 = "Extended-thinking text is the model"  # avoid apostrophe encoding issues
        # "not a claim about internal reasoning" may be split across a Python
        # implicit string-concat line break — test each half separately.
        fragment_3a = "not a claim about"
        fragment_3b = "internal reasoning"
        for frag in (fragment_1, fragment_2, fragment_3a, fragment_3b):
            assert frag in app_source, (
                f"OPS-T5 Q1: Section 4 disclaimer fragment {frag!r} not found "
                f"in app.py."
            )

    def test_expander_label_step1(self, detail_source: str) -> None:
        """The Step 1 expander label must appear verbatim in lib/detail.py.

        The label is a literal string in TranscriptStep.step_label; app.py
        renders it via _step.step_label at runtime.
        """
        required = "Step 1 — Freelist transcript"
        assert required in detail_source, (
            f"OPS-T5: expander label {required!r} not found in lib/detail.py."
        )

    def test_expander_label_step2(self, detail_source: str) -> None:
        """The Step 2 expander label must appear verbatim in lib/detail.py."""
        required = "Step 2 — Pile-sort transcript"
        assert required in detail_source, (
            f"OPS-T5: expander label {required!r} not found in lib/detail.py."
        )

    def test_expander_label_step3(self, detail_source: str) -> None:
        """The Step 3 expander label must appear verbatim in lib/detail.py."""
        required = "Step 3 — Interview / pile-naming transcript"
        assert required in detail_source, (
            f"OPS-T5: expander label {required!r} not found in lib/detail.py."
        )

    def test_extended_thinking_subheader_q2(self, app_source: str) -> None:
        """Q2 (binding SME edit): subheader inside each expander must use
        ‘Extended-thinking output (verbatim)’, not ‘Thinking trace (verbatim)’.
        """
        required = "Extended-thinking output (verbatim)"
        rejected = "Thinking trace (verbatim)"
        assert required in app_source, (
            f"OPS-T5 Q2 binding edit: subheader {required!r} not found in "
            f"app.py. The SME overrode the Architect recommendation — use "
            f"’Extended-thinking output (verbatim)’."
        )
        # Confirm the rejected label is not used in Section 4 context
        # (it may still appear in Section 1’s OPS-T4 expander; count occurrences
        # to ensure it only appears once — in the OPS-T4 expander, not Section 4)
        section4_marker = "### Raw transcripts"
        if section4_marker in app_source:
            section4_text = app_source[app_source.index(section4_marker):]
            assert rejected not in section4_text, (
                f"OPS-T5 Q2: rejected label {rejected!r} found in Section 4 "
                f"of app.py. Must use ‘Extended-thinking output (verbatim)’."
            )

    def test_empty_thinking_placeholder_q3(self, app_source: str) -> None:
        """Q3: empty-thinking placeholder must appear verbatim in app.py."""
        required = "No extended-thinking output for this step."
        assert required in app_source, (
            f"OPS-T5 Q3: empty-thinking placeholder {required!r} not found "
            f"in app.py."
        )


class TestOPST6MandatedCopy:
    """Verify OPS-T6 CDA SME-required strings are present in app.py.

    Tests cover: QA badge text, qa_notes blocks, decline summary section
    title, decline summary gloss caption (with SME binding edits applied),
    no-declines wording, and the st.info → st.success framing change.

    Two SME binding edits applied (PASS-WITH-NOTES verdict Q3 and Q5):
    - Q3: column header `manual_classification` → `disposition`
    - Q5: gloss caption gains "Disposition and" prefix for the label group

    See docs/status/2026-05-06-OPS-T6-cda-sme-verdict.md.
    """

    def test_qa_badge_pass_text(self, app_source: str) -> None:
        """A1: QA PASS badge literal must appear in app.py."""
        required = ":green-background[**PASS**]"
        fallback = ":green[**PASS**]"
        assert required in app_source or fallback in app_source, (
            f"OPS-T6 A1: QA PASS badge not found in app.py. "
            f"Expected {required!r} (or fallback {fallback!r})."
        )

    def test_qa_badge_fail_text(self, app_source: str) -> None:
        """A1: QA FAIL badge literal must appear in app.py."""
        required = ":red-background[**FAIL**]"
        fallback = ":red[**FAIL**]"
        assert required in app_source or fallback in app_source, (
            f"OPS-T6 A1: QA FAIL badge not found in app.py. "
            f"Expected {required!r} (or fallback {fallback!r})."
        )

    def test_qa_caption_no_longer_carries_qa_passed(self, app_source: str) -> None:
        """A2: The f-string caption must NOT contain 'qa_passed:' as a
        displayed value (badge replaces it).

        The old caption was:
          f"... | qa_passed: {_rec.qa_passed}"
        The new caption omits this. We guard against the old literal string
        fragment which combines the label and template expression.
        """
        # The old caption carried the literal fragment below. If it reappears,
        # the badge has been reverted and the caption still carries qa_passed.
        rejected = "qa_passed: {_rec.qa_passed}"
        assert rejected not in app_source, (
            f"OPS-T6 A2 regression: {rejected!r} still present in app.py. "
            "The QA badge replaces it — remove 'qa_passed:' from the caption."
        )

    def test_qa_notes_block_present(self, app_source: str) -> None:
        """A3/A4: Both qa_notes block literals must appear in app.py."""
        fail_literal = "**QA notes:**"
        expander_literal = "QA notes (informational)"
        assert fail_literal in app_source, (
            f"OPS-T6 A3: FAIL-path qa_notes literal {fail_literal!r} not found "
            f"in app.py."
        )
        assert expander_literal in app_source, (
            f"OPS-T6 A4: PASS-with-notes expander label {expander_literal!r} not "
            f"found in app.py."
        )

    def test_decline_summary_section_title(self, app_source: str) -> None:
        """A7: '### Decline summary' section title must appear in app.py."""
        required = "### Decline summary"
        assert required in app_source, (
            f"OPS-T6 A7: section title {required!r} not found in app.py."
        )

    def test_decline_summary_caption_q5_wording(self, app_source: str) -> None:
        """A9 / SME binding edit Q5: gloss caption must contain the SME-approved
        wording naming both the disposition column and the safety-subtype labels.

        Full approved text (binding):
        'One row per decline event for this informant. Disposition and
        safety-subtype labels (k_frame / k_vocab) are defined in
        docs/DECLINE_INTERVIEW_PROTOCOL.md.'
        """
        fragment_1 = "One row per decline event for this informant."
        fragment_2 = "Disposition and safety-subtype labels (k_frame / k_vocab)"
        fragment_3 = "docs/DECLINE_INTERVIEW_PROTOCOL.md"
        for frag in (fragment_1, fragment_2, fragment_3):
            assert frag in app_source, (
                f"OPS-T6 Q5 binding edit: gloss caption fragment {frag!r} not "
                f"found in app.py."
            )

    def test_no_declines_success_wording(self, app_source: str) -> None:
        """A8: no-declines message text must appear in app.py."""
        required = "No decline events recorded for this informant."
        assert required in app_source, (
            f"OPS-T6 A8: no-declines wording {required!r} not found in app.py."
        )

    def test_no_declines_uses_st_success(self, app_source: str) -> None:
        """A8 / SME Q4 binding: st.success must be used for the no-declines
        message (not st.info).

        Checks that the literal st.success(...) with the no-declines message
        text appears in app.py.
        """
        required = 'st.success("No decline events recorded for this informant.")'
        assert required in app_source, (
            f"OPS-T6 A8: {required!r} not found in app.py. "
            "The no-declines message must use st.success (green), not st.info."
        )

    def test_no_declines_does_not_use_st_info(self, app_source: str) -> None:
        """A8 regression guard: the old st.info no-declines literal must NOT
        appear in app.py.

        The SME Q4 binding changes the primitive from st.info (blue/neutral)
        to st.success (green/positive) to reflect 'no declines' as a clearly
        positive run state.
        """
        rejected = 'st.info("*No decline events recorded for this informant.*")'
        assert rejected not in app_source, (
            f"OPS-T6 A8 regression: rejected literal {rejected!r} still present "
            f"in app.py. Replace with st.success (SME Q4 binding)."
        )

    def test_disposition_column_header_present(self, app_source: str) -> None:
        """A9 / SME binding edit Q3: column header must be 'disposition',
        not 'manual_classification'.

        The SME renamed the displayed column from 'manual_classification'
        (the process) to 'disposition' (the value).
        """
        required = '"disposition"'
        assert required in app_source, (
            f"OPS-T6 Q3 binding edit: column key {required!r} not found in "
            f"app.py. The SME renamed the column from 'manual_classification' "
            f"to 'disposition'."
        )

    def test_qa_notes_empty_string_guard_present(self, app_source: str) -> None:
        """A5: When qa_notes is the empty string (the schema default), no notes
        block renders at all.

        The guard 'if _rec.qa_notes:' must appear in app.py so that the
        empty-string default short-circuits both rendering branches (st.error
        and st.expander). This is a static assertion that the guard is not
        accidentally removed in a future edit.

        See OPS-T6 architect plan §3 step 3 and acceptance criterion A5.
        """
        required = "if _rec.qa_notes:"
        assert required in app_source, (
            f"OPS-T6 A5: guard {required!r} not found in app.py. "
            "Without this guard, a qa_notes='' record would render an empty "
            "notes block. The schema default is '' (empty string, not None)."
        )

    def test_no_declines_st_success_appears_twice(self, app_source: str) -> None:
        """A7/A8: st.success with the no-declines message must appear in BOTH
        the new summary block and the existing decline-events block.

        A8 requires the framing change in both locations. If either is missing,
        one block still uses st.info (blue/neutral) instead of st.success
        (green/positive), violating the CDA SME Q4 binding.

        See OPS-T6 architect plan §3 steps 4–5 and acceptance criterion A8.
        """
        needle = 'st.success("No decline events recorded for this informant.")'
        count = app_source.count(needle)
        assert count >= 2, (
            f"OPS-T6 A8: {needle!r} appears {count} time(s) in app.py; "
            "expected at least 2 (one in the summary block, one in the "
            "decline-events block). CDA SME Q4 binding requires st.success "
            "in both locations."
        )

    def test_decline_summary_column_order(self, app_source: str) -> None:
        """A9: The summary table columns must appear in the expected order:
        decline_interview_id, originating_step, outcome_class,
        disposition, safety_subtype.

        Python dicts preserve insertion order (3.7+). The table dict literal
        in app.py defines the column order. This test verifies that each
        column key appears at a lower string position than the next, enforcing
        the order specified in the architect plan §3 step 4 and A9.
        """
        keys_in_order = [
            '"decline_interview_id"',
            '"originating_step"',
            '"outcome_class"',
            '"disposition"',
            '"safety_subtype"',
        ]
        positions = [app_source.index(k) for k in keys_in_order if k in app_source]
        assert len(positions) == len(keys_in_order), (
            "OPS-T6 A9: one or more column keys not found in app.py: "
            f"{[k for k in keys_in_order if k not in app_source]}"
        )
        for i in range(len(positions) - 1):
            assert positions[i] < positions[i + 1], (
                f"OPS-T6 A9: column order violation — {keys_in_order[i]!r} "
                f"(pos {positions[i]}) does not precede "
                f"{keys_in_order[i+1]!r} (pos {positions[i+1]}) in app.py."
            )


class TestOPST7MandatedCopy:
    """Verify OPS-T7 CDA SME-required strings are present in app.py,
    lib/detail.py, and lib/qa_interpreter.py.

    AST-T1: decline banner verbatim template substring present in app.py.
    AST-T2: app.py imports interpret_qa_notes from lib.qa_interpreter.
    AST-T3: app.py imports pile_sort_item_count from lib.detail.
    AST-T4: both pile-sort caption branch strings present in app.py.
    AST-T5: forbidden-vocabulary regex scan over all three source files.

    See docs/status/2026-05-06-OPS-T7-cda-sme-verdict.md.
    """

    def test_ast_t1_decline_banner_template_substring(self, app_source: str) -> None:
        """AST-T1: The decline banner template must contain the CDA SME Q3
        binding verbatim text (fragment check).

        Binding verbatim (from verdict §Q3):
        "This run has N classified decline event(s). See Decline summary and
        Decline events sections below."

        The N is substituted at render time; test the static fragments.
        """
        # Test the key fragments that must be present regardless of N formatting
        fragment_2 = "classified decline event"
        fragment_3 = "Decline summary"
        fragment_4 = "Decline events"
        fragment_5 = "sections below"
        for frag in (fragment_2, fragment_3, fragment_4, fragment_5):
            assert frag in app_source, (
                f"OPS-T7 AST-T1: decline banner fragment {frag!r} not found "
                f"in app.py. CDA SME Q3 binding verbatim."
            )
        # Also check the key distinguishing phrase from the SME edit
        # ("has N classified" not "produced N")
        assert "classified decline event" in app_source, (
            "OPS-T7 AST-T1: 'classified decline event' not found in app.py. "
            "SME Q3 changed 'produced' to 'has ... classified'."
        )
        # Guard against the rejected 'produced' formulation
        assert "This run produced" not in app_source, (
            "OPS-T7 AST-T1: rejected phrase 'This run produced' found in app.py. "
            "SME Q3 binding requires 'This run has N classified decline event(s).'."
        )

    def test_ast_t2_import_interpret_qa_notes(self, app_source: str) -> None:
        """AST-T2: app.py must import interpret_qa_notes from lib.qa_interpreter."""
        assert "interpret_qa_notes" in app_source, (
            "OPS-T7 AST-T2: 'interpret_qa_notes' not found in app.py. "
            "app.py must import and call interpret_qa_notes from "
            "apps.ops_dashboard.lib.qa_interpreter."
        )
        assert "qa_interpreter" in app_source, (
            "OPS-T7 AST-T2: 'qa_interpreter' module reference not found in app.py."
        )

    def test_ast_t3_import_pile_sort_item_count(self, app_source: str) -> None:
        """AST-T3: app.py must import pile_sort_item_count from lib.detail."""
        assert "pile_sort_item_count" in app_source, (
            "OPS-T7 AST-T3: 'pile_sort_item_count' not found in app.py. "
            "app.py must import pile_sort_item_count from apps.ops_dashboard.lib.detail."
        )

    def test_ast_t4_pile_sort_caption_own_freelist_branch(
        self, app_source: str
    ) -> None:
        """AST-T4 (own_freelist branch): the own_freelist caption fragment must
        appear verbatim in app.py.

        CDA SME Q4 binding (own_freelist):
        "Items sorted: this informant's own Step 1 freelist (N items)."
        """
        # Use ASCII apostrophe in case editor normalised
        fragment = "Items sorted: this informant"
        fragment_2 = "own Step 1 freelist"
        for frag in (fragment, fragment_2):
            assert frag in app_source, (
                f"OPS-T7 AST-T4: own_freelist caption fragment {frag!r} not found "
                f"in app.py. CDA SME Q4 binding."
            )

    def test_ast_t4_pile_sort_caption_external_branch(
        self, app_source: str
    ) -> None:
        """AST-T4 (external branch): the external source caption fragment must
        appear verbatim in app.py.

        CDA SME Q4 binding (external):
        "Items sorted: items from `{item_source}` (N items). Not derived from
        this informant's own freelist — see `PileSortRecord.item_source` for
        source semantics."
        """
        fragment_1 = "Items sorted: items from"
        fragment_2 = "Not derived from this informant"
        fragment_3 = "PileSortRecord.item_source"
        for frag in (fragment_1, fragment_2, fragment_3):
            assert frag in app_source, (
                f"OPS-T7 AST-T4: external caption fragment {frag!r} not found "
                f"in app.py. CDA SME Q4 binding."
            )

    # Forbidden-vocabulary patterns (CLAUDE.md §7 / ARCHITECTURE.md §1.5.4)
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

    @pytest.mark.parametrize("pattern", _FORBIDDEN_PATTERNS)
    def test_ast_t5_forbidden_vocabulary_app_py(
        self, pattern: str, app_source: str
    ) -> None:
        """AST-T5: app.py must not contain any §7 forbidden-vocabulary pattern."""
        rx = re.compile(pattern, re.IGNORECASE)
        assert not rx.search(app_source), (
            f"OPS-T7 AST-T5: forbidden pattern {pattern!r} found in app.py."
        )

    @pytest.mark.parametrize("pattern", _FORBIDDEN_PATTERNS)
    def test_ast_t5_forbidden_vocabulary_qa_interpreter_py(
        self, pattern: str, qa_interpreter_source: str
    ) -> None:
        """AST-T5: lib/qa_interpreter.py must not contain any §7 forbidden pattern."""
        rx = re.compile(pattern, re.IGNORECASE)
        assert not rx.search(qa_interpreter_source), (
            f"OPS-T7 AST-T5: forbidden pattern {pattern!r} found in "
            f"lib/qa_interpreter.py."
        )

    @pytest.mark.parametrize("pattern", _FORBIDDEN_PATTERNS)
    def test_ast_t5_forbidden_vocabulary_detail_py(
        self, pattern: str, detail_source: str
    ) -> None:
        """AST-T5: lib/detail.py must not contain any §7 forbidden pattern."""
        rx = re.compile(pattern, re.IGNORECASE)
        assert not rx.search(detail_source), (
            f"OPS-T7 AST-T5: forbidden pattern {pattern!r} found in "
            f"lib/detail.py."
        )
