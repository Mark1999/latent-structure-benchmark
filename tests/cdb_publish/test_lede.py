"""Tests for cdb_publish.lede.generate_lede().

No real API calls. All tests use fixtures from data/results/ or
synthetic DomainResult objects. See CLAUDE.md §6 R9.

Test plan (12 tests):
  1. Real-corpus family (STRONG_CONSENSUS, all R1-a) → homogeneous pattern
  2. Real-corpus holidays (STRONG_CONSENSUS, 2 R1-b) → with_low_oci pattern
  3. Synthetic STRONG_CONSENSUS majority-R1-b → majority_low_oci pattern
  4. Synthetic WEAK_CONSENSUS → weak_consensus pattern
  5. Synthetic SUBCULTURAL → subcultural pattern
  6. Synthetic TURBULENT → turbulent pattern
  7. Synthetic CONTESTED → contested pattern
  8. Synthetic all-deterministic (all deterministic_output=True) → verbatim DS copy
  9. Synthetic DETERMINISTIC consensus_type → same verbatim DS copy
  10. Vocabulary discipline: no §1.5.4 / T9 / T14 forbidden phrases across all patterns
  11. Determinism: same fixture → byte-identical output on two calls
  12. No-LLM-imports: lede.py source text does not import forbidden libraries

See docs/status/2026-05-09-phase5-architect-plan.md §4 T2 and
CDA SME plan-level verdict Q1–Q5.
"""

from __future__ import annotations

import ast
from pathlib import Path

from cdb_core.schemas import DomainResult
from cdb_publish.lede import generate_lede

# ---------------------------------------------------------------------------
# Shared fixture-building helpers
# ---------------------------------------------------------------------------

_RESULTS_DIR = Path(__file__).parent.parent.parent / "data" / "results"

# Verbatim DESIGN_SYSTEM.md §3.3.5 item 6 all-deterministic copy.
# This is the binding string; the test asserts byte-identity against it.
_ALL_DETERMINISTIC_COPY = (
    "All selected models produced deterministic output on this domain"
    " — the same categorical structure on every run."
    " Cross-model comparison remains valid; see below."
    " Methodology page explains what deterministic output signals about"
    " model architecture."
)


def _model_ref(model_id: str = "test-model-a") -> dict:
    return {
        "provider": "anthropic",
        "model_id": model_id,
        "family": "test",
        "origin": "us",
        "open_weights": False,
        "collection_method": "anthropic_api",
        "quantization": None,
        "release_date": "2026-01-01",
        "version_label": model_id,
        "source_notes": "",
    }


def _free_list(model_id: str, domain_slug: str = "test-domain") -> dict:
    return {
        "run_id": f"run-{model_id}",
        "model": _model_ref(model_id),
        "domain_slug": domain_slug,
        "items": ["alpha", "beta"],
        "raw_order": ["alpha", "beta"],
    }


def _bootstrap_ellipse() -> dict:
    return {
        "center": [0.0, 0.0],
        "semi_major": 0.1,
        "semi_minor": 0.05,
        "rotation_rad": 0.0,
        "n_bootstrap": 100,
    }


def _within_model_result(
    model_id: str,
    oci: float = 10.0,
    deterministic_output: bool = False,
) -> dict:
    return {
        "model_id": model_id,
        "n_runs": 5,
        "oci": oci,
        "deterministic_output": deterministic_output,
    }


def _build_domain_result(
    *,
    domain_slug: str = "test-domain",
    consensus_type: str | None = "STRONG_CONSENSUS",
    consensus_score: float = 6.5,
    consensus_ci: tuple[float, float] = (4.0, 9.0),
    model_ids: list[str] | None = None,
    within_model_oci: dict[str, float] | None = None,
    deterministic_outputs: dict[str, bool] | None = None,
) -> DomainResult:
    """Build a minimal valid DomainResult for testing.

    Parameters
    ----------
    domain_slug : str
        The domain identifier.
    consensus_type : str | None
        One of the six ConsensusType schema literals, or None.
    consensus_score : float
        Smith's S value.
    consensus_ci : tuple[float, float]
        95% CI bounds.
    model_ids : list[str] | None
        Model identifiers. Defaults to ["model-a", "model-b"].
    within_model_oci : dict[str, float] | None
        OCI per model. Defaults to 10.0 for all models.
    deterministic_outputs : dict[str, bool] | None
        deterministic_output per model. Defaults to False for all.
    """
    if model_ids is None:
        model_ids = ["model-a", "model-b"]

    if within_model_oci is None:
        within_model_oci = {mid: 10.0 for mid in model_ids}

    if deterministic_outputs is None:
        deterministic_outputs = {mid: False for mid in model_ids}

    n = len(model_ids)
    models = [_model_ref(mid) for mid in model_ids]
    free_lists = {mid: _free_list(mid, domain_slug) for mid in model_ids}
    mds_coords = {mid: [float(i), 0.0] for i, mid in enumerate(model_ids)}
    mds_uncertainty = {mid: _bootstrap_ellipse() for mid in model_ids}
    sim_matrix = [[1.0 if i == j else 0.5 for j in range(n)] for i in range(n)]
    sim_ci = [
        [[0.4, 0.6] if i != j else [1.0, 1.0] for j in range(n)]
        for i in range(n)
    ]
    within_results = [
        _within_model_result(
            model_id=mid,
            oci=within_model_oci.get(mid, 10.0),
            deterministic_output=deterministic_outputs.get(mid, False),
        )
        for mid in model_ids
    ]

    raw = {
        "domain_slug": domain_slug,
        "analysis_version": "0.2",
        "models": models,
        "free_lists": free_lists,
        "mds_coordinates": mds_coords,
        "mds_uncertainty": mds_uncertainty,
        "similarity_matrix": sim_matrix,
        "similarity_ci": sim_ci,
        "consensus_score": consensus_score,
        "consensus_ci": list(consensus_ci),
        "consensus_type": consensus_type,
        "within_model_results": within_results,
        "generated_lede": "",
        "generated_at": "2026-05-09T00:00:00Z",
    }

    return DomainResult.model_validate(raw)


# ---------------------------------------------------------------------------
# Test 1 — Real corpus: family (STRONG_CONSENSUS, all R1-a)
# ---------------------------------------------------------------------------

def test_family_real_corpus_strong_consensus_homogeneous() -> None:
    """Family domain → strong_consensus_with_low_oci pattern.

    family/0.3.json: n=15, STRONG_CONSENSUS, 1 model R1-b (oci < 3.0).
    Expected substrings reflect the current 15-model corpus (analysis_version 0.3).
    T4's planned re-baseline will update these assertions again.

    NOTE: the test name retains "homogeneous" for git-blame continuity; the
    corpus now routes to the with_low_oci pattern due to 1 R1-b model.
    """
    # Current corpus uses analysis_version 0.3; 0.3.json is the latest.
    family_path = _RESULTS_DIR / "family" / "0.3.json"
    result = DomainResult.model_validate_json(family_path.read_text(encoding="utf-8"))

    lede = generate_lede(result)

    # n=15 models on the map (was 11; updated to current corpus — T4 will update again)
    assert "15 frontier models" in lede, (
        f"Expected '15 frontier models' in lede; got: {lede!r}"
    )
    # Smith's S = 0.8033... → "0.80" (was 0.71; updated to current corpus)
    assert "Smith's S = 0.80" in lede, (
        f"Expected 'Smith's S = 0.80' in lede; got: {lede!r}"
    )
    # CI [0.6406..., 0.9433...] → "[0.64, 0.94]" (was [0.50, 0.91]; updated)
    assert "[0.64, 0.94]" in lede, (
        f"Expected '[0.64, 0.94]' in lede; got: {lede!r}"
    )
    # Shared categorical structure language (present in both homogeneous and
    # with_low_oci patterns)
    assert "shared categorical structure" in lede, (
        f"Expected 'shared categorical structure' in lede; got: {lede!r}"
    )
    # 1 R1-b model present → with_low_oci pattern surfaces the count
    assert "1 of these 15 models produced low output concentration" in lede, (
        f"Expected R1-b count phrase in family lede; got: {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 2 — Real corpus: holidays (STRONG_CONSENSUS, 2 R1-b models)
# ---------------------------------------------------------------------------

def test_holidays_real_corpus_strong_consensus_with_low_oci() -> None:
    """Holidays domain → strong_consensus_with_low_oci pattern.

    holidays/0.2.json: n=9, STRONG_CONSENSUS.
    Two models have oci < 3.0 (mistral-small: 0.0, gpt-5.4-mini: 2.55).
    Per Q5 binding, the lede must surface the R1-b count.
    """
    holidays_path = _RESULTS_DIR / "holidays" / "0.2.json"
    result = DomainResult.model_validate_json(
        holidays_path.read_text(encoding="utf-8")
    )

    lede = generate_lede(result)

    # n=9 models on the map
    assert "9 frontier models" in lede, (
        f"Expected '9 frontier models' in lede; got: {lede!r}"
    )
    # Must surface the 2 R1-b models (Q5 binding)
    assert "2 of these 9 models produced low output concentration" in lede, (
        f"Expected R1-b count phrase in holidays lede; got: {lede!r}"
    )
    # Shared categorical structure language
    assert "shared categorical structure" in lede, (
        f"Expected 'shared categorical structure' in lede; got: {lede!r}"
    )
    # No confidence ellipse language per the pattern
    assert "confidence ellipse" in lede, (
        f"Expected 'confidence ellipse' reference in holidays lede; got: {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 3 — Synthetic STRONG_CONSENSUS, majority R1-b
# ---------------------------------------------------------------------------

def test_strong_consensus_majority_low_oci_pattern() -> None:
    """STRONG_CONSENSUS with >50% R1-b models → majority_low_oci pattern."""
    # 4 models, 3 with low OCI (majority)
    model_ids = ["m1", "m2", "m3", "m4"]
    oci_map = {"m1": 0.5, "m2": 1.0, "m3": 2.0, "m4": 20.0}  # 3/4 < 3.0

    result = _build_domain_result(
        domain_slug="test-domain",
        consensus_type="STRONG_CONSENSUS",
        consensus_score=5.5,
        consensus_ci=(3.0, 8.0),
        model_ids=model_ids,
        within_model_oci=oci_map,
    )

    lede = generate_lede(result)

    assert "majority" in lede, (
        f"Expected 'majority' in majority-low-OCI lede; got: {lede!r}"
    )
    assert "4 frontier models" in lede, (
        f"Expected '4 frontier models'; got: {lede!r}"
    )
    assert "OCI badges" in lede or "methodology page" in lede.lower(), (
        f"Expected methodology-page reference; got: {lede!r}"
    )
    # Must NOT use the minority phrasing
    assert "of these 4 models produced low output concentration" not in lede, (
        f"Unexpected minority phrasing in majority-low-OCI lede: {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 4 — Synthetic WEAK_CONSENSUS
# ---------------------------------------------------------------------------

def test_weak_consensus_pattern() -> None:
    """WEAK_CONSENSUS → weak_consensus pattern."""
    result = _build_domain_result(
        domain_slug="widgets",
        consensus_type="WEAK_CONSENSUS",
        consensus_score=3.8,
        consensus_ci=(2.0, 5.6),
    )

    lede = generate_lede(result)

    assert "partial categorical agreement" in lede, (
        f"Expected 'partial categorical agreement'; got: {lede!r}"
    )
    assert "Smith's S = 3.80" in lede, (
        f"Expected 'Smith's S = 3.80'; got: {lede!r}"
    )
    assert "[2.00, 5.60]" in lede, (
        f"Expected '[2.00, 5.60]'; got: {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 5 — Synthetic SUBCULTURAL
# ---------------------------------------------------------------------------

def test_subcultural_pattern() -> None:
    """SUBCULTURAL → subcultural pattern with negative-centrality language."""
    result = _build_domain_result(
        domain_slug="politics",
        consensus_type="SUBCULTURAL",
        consensus_score=3.2,
        consensus_ci=(1.5, 4.9),
    )

    lede = generate_lede(result)

    assert "multiple distinct categorical sub-structures" in lede, (
        f"Expected sub-structures language; got: {lede!r}"
    )
    assert "negative centrality" in lede, (
        f"Expected 'negative centrality'; got: {lede!r}"
    )
    assert "different region of cognitive space" in lede, (
        f"Expected locational language; got: {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 6 — Synthetic TURBULENT
# ---------------------------------------------------------------------------

def test_turbulent_pattern() -> None:
    """TURBULENT → turbulent pattern."""
    result = _build_domain_result(
        domain_slug="news",
        consensus_type="TURBULENT",
        consensus_score=2.1,
        consensus_ci=(0.5, 3.7),
    )

    lede = generate_lede(result)

    assert "does not organize around a shared categorical structure" in lede, (
        f"Expected turbulent language; got: {lede!r}"
    )
    assert "Smith's S = 2.10" in lede, (
        f"Expected 'Smith's S = 2.10'; got: {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 7 — Synthetic CONTESTED
# ---------------------------------------------------------------------------

def test_contested_pattern() -> None:
    """CONTESTED → contested pattern with active divergence language."""
    result = _build_domain_result(
        domain_slug="ethics",
        consensus_type="CONTESTED",
        consensus_score=1.8,
        consensus_ci=(0.2, 3.4),
    )

    lede = generate_lede(result)

    assert "active categorical divergence" in lede, (
        f"Expected 'active categorical divergence'; got: {lede!r}"
    )
    assert "negative centrality on one or more models" in lede, (
        f"Expected negative centrality language; got: {lede!r}"
    )
    assert "diverges from the rest" in lede, (
        f"Expected 'diverges from the rest'; got: {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 8 — Synthetic all-deterministic (all deterministic_output=True)
# ---------------------------------------------------------------------------

def test_all_deterministic_verbatim_copy() -> None:
    """All-deterministic fixture → byte-identical to DESIGN_SYSTEM.md §3.3.5 item 6.

    Acceptance criterion (c): the all-deterministic case produces verbatim
    the DESIGN_SYSTEM.md §3.3.5 item 6 approved copy.
    """
    model_ids = ["det-model-a", "det-model-b", "det-model-c"]
    result = _build_domain_result(
        domain_slug="deterministic-domain",
        consensus_type="STRONG_CONSENSUS",
        consensus_score=12.0,
        model_ids=model_ids,
        deterministic_outputs={mid: True for mid in model_ids},
    )

    lede = generate_lede(result)

    assert lede == _ALL_DETERMINISTIC_COPY, (
        f"Expected verbatim all-deterministic copy.\n"
        f"Expected: {_ALL_DETERMINISTIC_COPY!r}\n"
        f"Got:      {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 9 — Synthetic DETERMINISTIC consensus_type fallback
# ---------------------------------------------------------------------------

def test_deterministic_consensus_type_verbatim_copy() -> None:
    """consensus_type='DETERMINISTIC' → same verbatim DS §3.3.5 item 6 copy.

    DETERMINISTIC is a valid ConsensusType schema literal and must
    produce the same all-deterministic lede copy as the all-R1-c case.
    """
    result = _build_domain_result(
        domain_slug="zero-temp-domain",
        consensus_type="DETERMINISTIC",
        consensus_score=0.0,
    )

    lede = generate_lede(result)

    assert lede == _ALL_DETERMINISTIC_COPY, (
        f"Expected verbatim all-deterministic copy for DETERMINISTIC type.\n"
        f"Expected: {_ALL_DETERMINISTIC_COPY!r}\n"
        f"Got:      {lede!r}"
    )


# ---------------------------------------------------------------------------
# Test 10 — Vocabulary discipline across all patterns
# ---------------------------------------------------------------------------

# §1.5.4 forbidden phrases + T9 verb list + T14 + B6 internal-state phrases
_FORBIDDEN_PHRASES: list[str] = [
    "believes",
    "thinks",
    "worldview",
    "the model understands",
    "the model recognizes",
    "the model recognises",
    "the model interprets",
    "the model perceives",
    "the model comprehends",
    "the model identifies",
    "publishable",
    "publication",
    "cultural bias",
    # T9 softer verbs applied to models (substring check; case-insensitive)
    "model recognizes",
    "model identifies",
    "model interprets",
    "model comprehends",
    "model perceives",
    # B6 internal-state phrases
    "the model decided",
    "the model chose",
    "the model preferred",
]


def _all_pattern_lede_outputs() -> list[tuple[str, str]]:
    """Return (pattern_name, lede_text) for every distinct pattern."""
    scenarios = [
        # Pattern 1: strong_consensus_homogeneous
        _build_domain_result(
            domain_slug="family",
            consensus_type="STRONG_CONSENSUS",
            consensus_score=7.1,
            consensus_ci=(5.0, 9.1),
            model_ids=[f"m{i}" for i in range(8)],
            within_model_oci={f"m{i}": 10.0 for i in range(8)},
        ),
        # Pattern 2: strong_consensus_with_low_oci (1 R1-b out of 5)
        _build_domain_result(
            domain_slug="holidays",
            consensus_type="STRONG_CONSENSUS",
            consensus_score=6.5,
            model_ids=["m0", "m1", "m2", "m3", "m4"],
            within_model_oci={"m0": 0.5, "m1": 10.0, "m2": 10.0, "m3": 10.0, "m4": 10.0},
        ),
        # Pattern 3: strong_consensus_majority_low_oci (3 R1-b out of 4)
        _build_domain_result(
            domain_slug="test",
            consensus_type="STRONG_CONSENSUS",
            consensus_score=5.5,
            model_ids=["m0", "m1", "m2", "m3"],
            within_model_oci={"m0": 0.5, "m1": 1.0, "m2": 2.0, "m3": 20.0},
        ),
        # Pattern 4: weak_consensus
        _build_domain_result(
            domain_slug="widgets",
            consensus_type="WEAK_CONSENSUS",
            consensus_score=3.8,
        ),
        # Pattern 5: subcultural
        _build_domain_result(
            domain_slug="politics",
            consensus_type="SUBCULTURAL",
            consensus_score=3.2,
        ),
        # Pattern 6: turbulent
        _build_domain_result(
            domain_slug="news",
            consensus_type="TURBULENT",
            consensus_score=2.1,
        ),
        # Pattern 7: contested
        _build_domain_result(
            domain_slug="ethics",
            consensus_type="CONTESTED",
            consensus_score=1.8,
        ),
        # Pattern 8: all_deterministic (all R1-c)
        _build_domain_result(
            domain_slug="det-domain",
            consensus_type="STRONG_CONSENSUS",
            consensus_score=12.0,
            model_ids=["d1", "d2"],
            deterministic_outputs={"d1": True, "d2": True},
        ),
        # Pattern 9: DETERMINISTIC consensus_type
        _build_domain_result(
            domain_slug="zero-temp",
            consensus_type="DETERMINISTIC",
            consensus_score=0.0,
        ),
    ]

    return [(generate_lede(r), r.domain_slug) for r in scenarios]


def test_vocabulary_discipline_across_all_patterns() -> None:
    """No §1.5.4 / T9 / T14 / B6 forbidden phrase in any generated lede.

    Acceptance criterion (b): output strings contain none of the §1.5.4
    forbidden phrases. Test asserts this directly via substring check.
    Case-insensitive matching.
    """
    outputs = _all_pattern_lede_outputs()

    violations: list[str] = []
    for lede, slug in outputs:
        lede_lower = lede.lower()
        for phrase in _FORBIDDEN_PHRASES:
            if phrase.lower() in lede_lower:
                violations.append(
                    f"Forbidden phrase {phrase!r} found in {slug!r} lede: {lede!r}"
                )

    assert not violations, "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 11 — Determinism
# ---------------------------------------------------------------------------

def test_generate_lede_is_deterministic() -> None:
    """Same DomainResult → byte-identical output on two calls.

    Acceptance criterion (a): generate_lede is deterministic.
    """
    family_path = _RESULTS_DIR / "family" / "0.2.json"
    result = DomainResult.model_validate_json(family_path.read_text(encoding="utf-8"))

    lede_a = generate_lede(result)
    lede_b = generate_lede(result)

    assert lede_a == lede_b, (
        "generate_lede is not deterministic: two calls on the same fixture "
        f"produced different output.\nFirst:  {lede_a!r}\nSecond: {lede_b!r}"
    )


# ---------------------------------------------------------------------------
# Test 12 — No LLM imports in lede.py
# ---------------------------------------------------------------------------

_FORBIDDEN_IMPORTS = [
    "anthropic",
    "openai",
    "google.generativeai",
    "huggingface_hub",
    "litellm",
    "langchain",
    "llama_index",
]

_LEDE_PY_PATH = (
    Path(__file__).parent.parent.parent
    / "packages"
    / "cdb_publish"
    / "cdb_publish"
    / "lede.py"
)


def test_no_llm_imports_in_lede_py() -> None:
    """lede.py must not import any LLM client library.

    Acceptance criterion (d): the lede generator does not import any LLM
    client library. Mirrors the cdb_analyze static-import check pattern.

    We parse the AST to catch both 'import X' and 'from X import Y' forms.
    """
    source = _LEDE_PY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in _FORBIDDEN_IMPORTS:
                    if alias.name == forbidden or alias.name.startswith(f"{forbidden}."):
                        violations.append(
                            f"Line {node.lineno}: 'import {alias.name}' "
                            f"(matches forbidden library '{forbidden}')"
                        )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for forbidden in _FORBIDDEN_IMPORTS:
                if module == forbidden or module.startswith(f"{forbidden}."):
                    violations.append(
                        f"Line {node.lineno}: 'from {module} import ...' "
                        f"(matches forbidden library '{forbidden}')"
                    )

    assert not violations, (
        "LLM client library imports found in lede.py:\n"
        + "\n".join(violations)
    )


# ---------------------------------------------------------------------------
# Gap-fill Test 13 — WEAK_CONSENSUS with R1-b models (no sub-branch)
# ---------------------------------------------------------------------------

def test_weak_consensus_with_r1b_models_no_subbranch() -> None:
    """WEAK_CONSENSUS + R1-b models → still routes to weak_consensus pattern.

    Gap: _select_pattern does not sub-branch WEAK_CONSENSUS on n_low_oci.
    This regression guard confirms R1-b presence does not change the
    pattern selection or cause a crash for WEAK_CONSENSUS inputs.
    """
    model_ids = ["m0", "m1", "m2", "m3", "m4"]
    # Two R1-b models (oci < 3.0)
    oci_map = {"m0": 0.5, "m1": 2.0, "m2": 10.0, "m3": 10.0, "m4": 10.0}

    result = _build_domain_result(
        domain_slug="gadgets",
        consensus_type="WEAK_CONSENSUS",
        consensus_score=4.2,
        consensus_ci=(2.5, 5.9),
        model_ids=model_ids,
        within_model_oci=oci_map,
    )

    lede = generate_lede(result)

    # Pattern selection must be weak_consensus regardless of R1-b presence
    assert "partial categorical agreement" in lede, (
        f"Expected weak_consensus pattern with 'partial categorical agreement';"
        f" got: {lede!r}"
    )
    assert "Smith's S = 4.20" in lede, (
        f"Expected 'Smith's S = 4.20'; got: {lede!r}"
    )
    assert "[2.50, 5.90]" in lede, (
        f"Expected '[2.50, 5.90]'; got: {lede!r}"
    )
    # Must NOT surface the R1-b count phrase (no sub-branch for WEAK_CONSENSUS)
    assert "low output concentration" not in lede, (
        f"Unexpected 'low output concentration' in WEAK_CONSENSUS lede: {lede!r}"
    )


# ---------------------------------------------------------------------------
# Gap-fill Test 14 — n_low_oci=1 (singular) formatting in with_low_oci pattern
# ---------------------------------------------------------------------------

def test_strong_consensus_with_low_oci_singular_count() -> None:
    """STRONG_CONSENSUS, n_low_oci=1 → correct singular count in lede.

    Gap: tests 2 and 10 only exercise n_low_oci=2 (holidays fixture) and
    a 1-R1b scenario used only for vocabulary checks.  No test explicitly
    asserts that '1 of these N models produced low output concentration'
    appears verbatim when exactly one model is R1-b.
    """
    model_ids = ["m0", "m1", "m2", "m3", "m4"]
    # Exactly one R1-b model (oci < 3.0)
    oci_map = {"m0": 1.5, "m1": 10.0, "m2": 10.0, "m3": 10.0, "m4": 10.0}

    result = _build_domain_result(
        domain_slug="cuisine",
        consensus_type="STRONG_CONSENSUS",
        consensus_score=6.1,
        consensus_ci=(4.2, 8.0),
        model_ids=model_ids,
        within_model_oci=oci_map,
    )

    lede = generate_lede(result)

    # n_low_oci=1, n=5 → "1 of these 5 models produced low output concentration"
    assert "1 of these 5 models produced low output concentration" in lede, (
        f"Expected singular '1 of these 5 models produced low output"
        f" concentration'; got: {lede!r}"
    )
    assert "5 frontier models" in lede, (
        f"Expected '5 frontier models'; got: {lede!r}"
    )
    assert "Smith's S = 6.10" in lede, (
        f"Expected 'Smith's S = 6.10'; got: {lede!r}"
    )
    assert "[4.20, 8.00]" in lede, (
        f"Expected '[4.20, 8.00]'; got: {lede!r}"
    )
    assert "confidence ellipse" in lede, (
        f"Expected 'confidence ellipse' in with_low_oci lede; got: {lede!r}"
    )
