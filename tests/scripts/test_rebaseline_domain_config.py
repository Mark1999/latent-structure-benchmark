"""Tests for rebaseline_corpus.py DOMAIN_CONFIG structure.

Verifies the invariants stated in the runbook
(docs/proposed/2026-06-08-new-model-incorporation-runbook.md Step 3):

  - food has similarity_collection_mode="single_pass" (FOOD-FIX-A)
  - family and holidays have similarity_collection_mode=None
    (single-mode legacy slates; no filter needed)
  - DOMAIN_ORDER is ["family", "holidays", "food"] (family is the pilot gate)
  - Every entry in DOMAIN_CONFIG has the required keys

No real API calls. No I/O. Pure import + structure inspection.
"""

from __future__ import annotations


def test_food_similarity_collection_mode_is_single_pass() -> None:
    """FOOD-FIX-A: food domain must have similarity_collection_mode='single_pass'.

    The runbook Step 3 addendum (and the rebaseline_corpus.py header comment)
    binds this value: any stray cross_model_consensus records are basis-excluded
    before the similarity matrix is computed.
    """
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    assert "food" in DOMAIN_CONFIG, "food must be a key in DOMAIN_CONFIG"
    assert DOMAIN_CONFIG["food"]["similarity_collection_mode"] == "single_pass", (
        "food similarity_collection_mode must be 'single_pass' (FOOD-FIX-A)"
    )


def test_family_similarity_collection_mode_is_none() -> None:
    """family is a single-mode legacy slate; no mode filter required."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    assert "family" in DOMAIN_CONFIG, "family must be a key in DOMAIN_CONFIG"
    assert DOMAIN_CONFIG["family"]["similarity_collection_mode"] is None, (
        "family similarity_collection_mode must be None (single-mode legacy slate)"
    )


def test_holidays_similarity_collection_mode_is_none() -> None:
    """holidays is a single-mode legacy slate; no mode filter required."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    assert "holidays" in DOMAIN_CONFIG, "holidays must be a key in DOMAIN_CONFIG"
    assert DOMAIN_CONFIG["holidays"]["similarity_collection_mode"] is None, (
        "holidays similarity_collection_mode must be None (single-mode legacy slate)"
    )


def test_domain_config_all_entries_have_required_keys() -> None:
    """Every DOMAIN_CONFIG entry must have prior_version, new_version,
    and similarity_collection_mode."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    required_keys = {"prior_version", "new_version", "similarity_collection_mode"}
    for domain, cfg in DOMAIN_CONFIG.items():
        missing = required_keys - cfg.keys()
        assert not missing, (
            f"DOMAIN_CONFIG[{domain!r}] is missing required keys: {missing}"
        )


def test_domain_order_is_family_holidays_food() -> None:
    """DOMAIN_ORDER must be ['family', 'holidays', 'food'].

    The runbook Step 3 pipeline processes domains in this fixed sequence
    (family is the pilot gate; a halt stops remaining domains).
    """
    from scripts.rebaseline_corpus import DOMAIN_ORDER

    assert DOMAIN_ORDER == ["family", "holidays", "food"], (
        f"DOMAIN_ORDER must be ['family', 'holidays', 'food']; got {DOMAIN_ORDER!r}"
    )


def test_domain_order_entries_all_in_domain_config() -> None:
    """Every domain in DOMAIN_ORDER must have a DOMAIN_CONFIG entry."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG, DOMAIN_ORDER

    for domain in DOMAIN_ORDER:
        assert domain in DOMAIN_CONFIG, (
            f"DOMAIN_ORDER lists {domain!r} but it has no DOMAIN_CONFIG entry"
        )
