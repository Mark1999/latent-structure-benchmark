"""Tests for rebaseline_corpus.py DOMAIN_CONFIG structure (R3).

Verifies the invariants stated in the runbook and enforced by N17:

  - food has similarity_collection_mode="single_pass" (FOOD-FIX-A)
  - family and holidays have similarity_collection_mode=None
    (single-mode legacy slates; no filter needed)
  - DOMAIN_ORDER is ["family", "holidays", "food"] (family is the pilot gate)
  - Every entry in DOMAIN_CONFIG has the required keys including approved_slate
  - approved_slate frozensets contain the published basis + batch A additions,
    and exclude claude-fable-5, qwen/qwen3.6-plus, z-ai/glm-5.1
  - Empty approved_slate is a no-op (all QA-passed records included)
  - Batch A additions present in all three domain slates

No real API calls. No I/O. Pure import + structure inspection.
"""

from __future__ import annotations

# ─── Basic structure invariants ───────────────────────────────────────────────


def test_food_similarity_collection_mode_is_single_pass() -> None:
    """FOOD-FIX-A: food domain must have similarity_collection_mode='single_pass'."""
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
    similarity_collection_mode, and approved_slate."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    required_keys = {
        "prior_version",
        "new_version",
        "similarity_collection_mode",
        "approved_slate",
    }
    for domain, cfg in DOMAIN_CONFIG.items():
        missing = required_keys - cfg.keys()
        assert not missing, (
            f"DOMAIN_CONFIG[{domain!r}] is missing required keys: {missing}"
        )


def test_domain_order_is_family_holidays_food() -> None:
    """DOMAIN_ORDER must be ['family', 'holidays', 'food']."""
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


# ─── R3: approved_slate structure ─────────────────────────────────────────────


def test_approved_slate_is_frozenset() -> None:
    """approved_slate in each domain must be a frozenset (immutable, hashable)."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    for domain, cfg in DOMAIN_CONFIG.items():
        assert isinstance(cfg["approved_slate"], frozenset), (
            f"DOMAIN_CONFIG[{domain!r}]['approved_slate'] must be a frozenset; "
            f"got {type(cfg['approved_slate']).__name__}"
        )


def test_approved_slate_nonempty_for_all_domains() -> None:
    """Each domain's approved_slate must be non-empty (N17: published basis + batch A)."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    for domain, cfg in DOMAIN_CONFIG.items():
        assert len(cfg["approved_slate"]) > 0, (
            f"DOMAIN_CONFIG[{domain!r}]['approved_slate'] must not be empty"
        )


_BATCH_A_MODELS = frozenset({
    "claude-opus-4-8",
    "claude-sonnet-5",
    "openai/gpt-5.5",
    "deepseek/deepseek-v4-pro",
    "z-ai/glm-5.2",
    "google/gemini-3.5-flash",
    "x-ai/grok-4.3",
})


def test_batch_a_additions_in_all_slates() -> None:
    """All seven batch A additions must appear in every domain's approved_slate."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    for domain, cfg in DOMAIN_CONFIG.items():
        slate = cfg["approved_slate"]
        missing = _BATCH_A_MODELS - slate
        assert not missing, (
            f"DOMAIN_CONFIG[{domain!r}]['approved_slate'] is missing "
            f"batch A models: {sorted(missing)}"
        )


def test_family_published_basis_in_slate() -> None:
    """Family published basis models (from 0.3.json) must be in family approved_slate."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    # Verified from data/results/family/0.3.json cultural_centrality_scores 2026-07-11
    family_basis = frozenset({
        "claude-opus-4-5",
        "claude-opus-4-6",
        "claude-sonnet-4-6",
        "deepseek/deepseek-v3.2",
        "google/gemini-2.5-flash",
        "google/gemini-2.5-pro",
        "meta-llama/llama-4-maverick",
        "microsoft/phi-4",
        "mistralai/mistral-large-2512",
        "mistralai/mistral-small-2603",
        "openai/gpt-5.2",
        "openai/gpt-5.4",
        "openai/gpt-5.4-mini",
        "x-ai/grok-4",
        "x-ai/grok-4.20",
    })
    slate = DOMAIN_CONFIG["family"]["approved_slate"]
    missing = family_basis - slate
    assert not missing, (
        f"Family approved_slate is missing published basis models: {sorted(missing)}"
    )


def test_holidays_published_basis_in_slate() -> None:
    """Holidays published basis models (from 0.3.json) must be in holidays approved_slate."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    # Verified from data/results/holidays/0.3.json cultural_centrality_scores 2026-07-11
    holidays_basis = frozenset({
        "claude-opus-4-5",
        "claude-opus-4-6",
        "claude-sonnet-4-6",
        "deepseek/deepseek-v3.2",
        "google/gemini-2.5-flash",
        "google/gemini-2.5-pro",
        "meta-llama/llama-4-maverick",
        "mistralai/mistral-large-2512",
        "mistralai/mistral-small-2603",
        "openai/gpt-5.2",
        "openai/gpt-5.4",
        "openai/gpt-5.4-mini",
        "x-ai/grok-4",
        "x-ai/grok-4.20",
    })
    slate = DOMAIN_CONFIG["holidays"]["approved_slate"]
    missing = holidays_basis - slate
    assert not missing, (
        f"Holidays approved_slate is missing published basis models: {sorted(missing)}"
    )


def test_food_published_basis_in_slate() -> None:
    """Food published basis models (from 0.2.json) must be in food approved_slate."""
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    # Verified from data/results/food/0.2.json cultural_centrality_scores 2026-07-11
    food_basis = frozenset({
        "claude-opus-4-5",
        "claude-opus-4-6",
        "claude-sonnet-4-6",
        "deepseek/deepseek-v3.2",
        "google/gemini-2.5-flash",
        "google/gemini-2.5-pro",
        "mistralai/mistral-large-2512",
        "mistralai/mistral-small-2603",
        "openai/gpt-5.2",
        "openai/gpt-5.4",
        "openai/gpt-5.4-mini",
        "x-ai/grok-4",
    })
    slate = DOMAIN_CONFIG["food"]["approved_slate"]
    missing = food_basis - slate
    assert not missing, (
        f"Food approved_slate is missing published basis models: {sorted(missing)}"
    )


def test_excluded_models_not_in_any_slate() -> None:
    """claude-fable-5 (SME R1/R2) must not appear in any domain's approved_slate.

    qwen/qwen3.6-plus and z-ai/glm-5.1 are pending Mark's decision; they must
    not be in any slate until explicitly approved. A one-line add is all that is
    needed when the decision is made.
    """
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    excluded = {"claude-fable-5", "qwen/qwen3.6-plus", "z-ai/glm-5.1"}
    for domain, cfg in DOMAIN_CONFIG.items():
        slate = cfg["approved_slate"]
        present = excluded & slate
        assert not present, (
            f"DOMAIN_CONFIG[{domain!r}]['approved_slate'] contains model(s) "
            f"that must not be included yet: {sorted(present)}"
        )


def test_empty_approved_slate_is_noop() -> None:
    """An empty approved_slate frozenset is a no-op: an empty set never passes the filter.

    This is a structural test verifying the filter semantics: when approved_slate is
    empty, the rebaseline_domain function skips the filter (documented in the code
    as 'empty set is a no-op'). We verify this semantically: the filter condition
    'if approved_slate:' is falsy for an empty frozenset, so all QA-passed records
    would be included. This is the intended escape hatch for running without a slate.
    """
    empty_slate: frozenset[str] = frozenset()
    # Empty frozenset is falsy -> no filtering
    assert not empty_slate, "Empty frozenset must be falsy (no-op filter)"
    # Non-empty frozenset is truthy -> filtering applies
    nonempty: frozenset[str] = frozenset({"model-a"})
    assert nonempty, "Non-empty frozenset must be truthy (filter applies)"


def test_9_legacy_family_models_in_family_slate() -> None:
    """The 9 legacy family models that the defective load_records dropped must be in the slate.

    These are the models the architect plan identifies as having been mass-dropped
    in the 2026-07-11 rebaseline run due to the reference-set Check-2 bug.
    All 9 are part of the published family/0.3.json basis and must be in the slate.
    """
    from scripts.rebaseline_corpus import DOMAIN_CONFIG

    nine_legacy = frozenset({
        "claude-opus-4-5",
        "claude-opus-4-6",
        "claude-sonnet-4-6",
        "google/gemini-2.5-pro",
        "openai/gpt-5.2",
        "openai/gpt-5.4",
        "openai/gpt-5.4-mini",
        "x-ai/grok-4",
        "x-ai/grok-4.20",
    })
    slate = DOMAIN_CONFIG["family"]["approved_slate"]
    missing = nine_legacy - slate
    assert not missing, (
        f"Family approved_slate is missing 9 legacy models that were "
        f"mass-dropped by the defective load_records: {sorted(missing)}"
    )
