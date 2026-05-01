"""Static-text assertions on apps/ops_dashboard/app.py (OPS-T4).

These tests do NOT import or execute app.py as a Streamlit application.
They read it as a plain text file and assert that the CDA SME-mandated
copy strings are present verbatim.

Rationale: Streamlit apps cannot be unit-tested by importing (the
`st.*` calls run at import time against a missing server context).
Static-text grep is the only way to guard against accidental copy drift
without spinning up a live Streamlit server.

CDA SME notes verified here:
- Note 1: Section 2 verbatim-provenance header.
- Note 4: Section 3 model-attribution disclaimer.
- Note 5: Empty-freelist banner with exact SME-approved wording.

No real API calls. No reads from data/. All assertions are on the
source file at a known absolute path.

See docs/status/2026-05-01-ops-wireframes-cda-sme-verdict.md for the
binding SME note text. Coverage point #24.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_APP_PY = Path(__file__).resolve().parents[1] / "apps" / "ops_dashboard" / "app.py"


@pytest.fixture(scope="module")
def app_source() -> str:
    """Return the full source text of app.py."""
    return _APP_PY.read_text(encoding="utf-8")


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
