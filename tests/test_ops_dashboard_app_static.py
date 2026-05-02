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


@pytest.fixture(scope="module")
def app_source() -> str:
    """Return the full source text of app.py."""
    return _APP_PY.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def detail_source() -> str:
    """Return the full source text of lib/detail.py."""
    return _DETAIL_PY.read_text(encoding="utf-8")


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
