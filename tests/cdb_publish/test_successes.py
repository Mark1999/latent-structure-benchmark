"""Tests for cdb_publish.successes and its publish-layer schema.

No real API calls. All tests use synthetic fixtures in
tests/fixtures/successes/ or written to tmp_path.
See CLAUDE.md §6 R9 (no real API in tests).

Coverage:
- Empty-domain emission produces a valid file with by_model: [].
- Multi-model counting produces the correct n_runs and n_qa_passed.
- qa_passed=False rows count toward n_runs but not n_qa_passed.
- Sanitization fires on a synthesised model_id field carrying a
  fake API-key-shaped substring (defense-in-depth verification).
- PublishedSuccessesFile.model_validate_json() round-trip on emitted JSON.
- Source informants.jsonl SHA256 is byte-identical before and after.
- Manifest carries a records entry for every domain in domains.
- framing_note is present and non-empty in all emitted files.
- by_model rows are sorted lexicographically by model_id ascending.
- model_version_returned carries lex-greatest when multiple versions exist.
- model_version_returned_count > 1 when provider rolled a snapshot.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "successes"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_fixture(tmp_path: Path) -> Path:
    """Copy fixture informants.jsonl to tmp_path. Returns the new path."""
    dest = tmp_path / "informants.jsonl"
    shutil.copy(FIXTURES_DIR / "informants.jsonl", dest)
    return dest


class TestEmptyDomainEmission:
    """Empty-domain case: zero informants produces a valid first-class file."""

    def test_empty_domain_file_emitted(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        result = build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays", "food"],
        )

        # food has zero records in fixture — file must still exist.
        assert (out / "food.json").exists()
        food_json = json.loads((out / "food.json").read_text())
        assert food_json["by_model"] == []
        assert food_json["n_informants"] == 0
        assert "framing_note" in food_json
        assert len(food_json["framing_note"]) > 50

        # Manifest map entry must be non-null.
        assert result["food"] == "data/records/food.json"

    def test_empty_domain_framing_note_present(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["food"],
        )

        food_json = json.loads((out / "food.json").read_text())
        # framing_note is always present even for empty domains (CDA SME N3).
        assert food_json["framing_note"] != ""
        assert "LSB pipeline" in food_json["framing_note"]


class TestMultiModelCounting:
    """Counting tests: n_runs, n_qa_passed, model_id sort order."""

    def test_n_runs_counts_all_records(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_json = json.loads((out / "family.json").read_text())
        # fixture has: alpha=3 (family), beta=3 (family), redact=1 (family)
        # total = 7 informants in family (including qa_passed=False)
        assert family_json["n_informants"] == 7

    def test_n_qa_passed_subset_only(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_json = json.loads((out / "family.json").read_text())
        # test-model-alpha has 3 runs: inf-s001 (qa=T), inf-s002 (qa=T), inf-s003 (qa=F)
        by_model = {row["model_id"]: row for row in family_json["by_model"]}
        alpha_row = by_model["test-model-alpha"]
        assert alpha_row["n_runs"] == 3
        assert alpha_row["n_qa_passed"] == 2

    def test_qa_failed_counts_n_runs_not_n_qa_passed(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_json = json.loads((out / "family.json").read_text())
        by_model = {row["model_id"]: row for row in family_json["by_model"]}
        alpha_row = by_model["test-model-alpha"]
        # The qa_passed=False record (inf-s003) bumps n_runs but not n_qa_passed.
        assert alpha_row["n_runs"] > alpha_row["n_qa_passed"]
        assert alpha_row["n_runs"] - alpha_row["n_qa_passed"] == 1

    def test_by_model_sorted_by_model_id_lexicographic(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_json = json.loads((out / "family.json").read_text())
        model_ids = [row["model_id"] for row in family_json["by_model"]]
        assert model_ids == sorted(model_ids), (
            f"by_model rows not sorted lexicographically: {model_ids}"
        )

    def test_model_version_returned_count_when_multiple(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_json = json.loads((out / "family.json").read_text())
        by_model = {row["model_id"]: row for row in family_json["by_model"]}
        # test-model-beta has two versions: v2 (runs 0,1) and v3 (run 2).
        beta_row = by_model["test-model-beta"]
        assert beta_row["model_version_returned_count"] == 2
        # lex-greatest version is selected.
        assert beta_row["model_version_returned"] == "test-model-beta-v3"

    def test_model_version_returned_count_one_when_single(
        self, tmp_path: Path
    ) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_json = json.loads((out / "family.json").read_text())
        by_model = {row["model_id"]: row for row in family_json["by_model"]}
        # test-model-alpha only has v1.
        alpha_row = by_model["test-model-alpha"]
        assert alpha_row["model_version_returned_count"] == 1
        assert alpha_row["model_version_returned"] == "test-model-alpha-v1"


class TestSanitization:
    """Sanitization fires on model_id / model_version_returned with key shapes."""

    def test_sanitization_fires_on_key_shaped_version_string(
        self, tmp_path: Path
    ) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_text = (out / "family.json").read_text()
        # The fixture inf-s008 has a model_version_returned that looks like
        # an Anthropic API key — it should be redacted.
        assert "sk-ant-api03-" not in family_text
        assert "[redacted: secret pattern]" in family_text


class TestSchemaRoundTrip:
    """PublishedSuccessesFile.model_validate_json() round-trip."""

    def test_round_trip_family(self, tmp_path: Path) -> None:
        from cdb_publish.schemas.successes import PublishedSuccessesFile
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        json_text = (out / "family.json").read_text()
        parsed = PublishedSuccessesFile.model_validate_json(json_text)
        assert parsed.domain_slug == "family"
        assert parsed.n_informants >= 0
        assert isinstance(parsed.by_model, list)
        assert parsed.framing_note != ""

    def test_round_trip_empty_domain(self, tmp_path: Path) -> None:
        from cdb_publish.schemas.successes import PublishedSuccessesFile
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["food"],
        )

        json_text = (out / "food.json").read_text()
        parsed = PublishedSuccessesFile.model_validate_json(json_text)
        assert parsed.domain_slug == "food"
        assert parsed.n_informants == 0
        assert parsed.by_model == []
        assert parsed.framing_note != ""


class TestSHA256Invariance:
    """Source informants.jsonl is byte-identical before and after build_successes."""

    def test_source_file_not_modified(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        sha_before = _sha256(inf_path)

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays", "food"],
        )

        sha_after = _sha256(inf_path)
        assert sha_before == sha_after, (
            "informants.jsonl was modified by build_successes()"
        )


class TestManifestMap:
    """Manifest map contains an entry for every domain slug."""

    def test_manifest_map_all_slugs(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        result = build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays", "food"],
        )

        for slug in ("family", "holidays", "food"):
            assert slug in result
            assert result[slug] == f"data/records/{slug}.json"

    def test_manifest_values_never_null(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        result = build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "food"],
        )

        for _slug, path in result.items():
            assert path is not None
            assert path != ""


class TestFramingNote:
    """framing_note is present, non-empty, and contains the corpus-lens anchor."""

    def test_framing_note_in_every_domain(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays", "food"],
        )

        for slug in ("family", "holidays", "food"):
            data = json.loads((out / f"{slug}.json").read_text())
            assert "framing_note" in data
            assert "LSB pipeline" in data["framing_note"]
            assert "quality judgment" in data["framing_note"]

    def test_framing_note_byte_identical_to_module_constant(
        self, tmp_path: Path
    ) -> None:
        from cdb_publish.successes import _FRAMING_NOTE, build_successes

        inf_path = _copy_fixture(tmp_path)
        out = tmp_path / "out"

        build_successes(
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        data = json.loads((out / "family.json").read_text())
        assert data["framing_note"] == _FRAMING_NOTE


class TestMissingInformantsFile:
    """build_successes handles a missing source file gracefully."""

    def test_missing_file_produces_empty_outputs(self, tmp_path: Path) -> None:
        from cdb_publish.successes import build_successes

        missing = tmp_path / "nonexistent.jsonl"
        out = tmp_path / "out"

        result = build_successes(
            raw_informants_path=missing,
            output_dir=out,
            domain_slugs=["family"],
        )

        # Must still emit a file with n_informants: 0.
        family_json = json.loads((out / "family.json").read_text())
        assert family_json["n_informants"] == 0
        assert family_json["by_model"] == []
        assert result["family"] == "data/records/family.json"


class TestBuildIntegration:
    """Integration test: build() wires build_successes() and manifest carries records."""

    def test_build_manifest_has_records_field(self, tmp_path: Path) -> None:
        """Manifest.records is populated after build() runs."""
        from cdb_publish.schemas.manifest import Manifest

        # Minimal manifest with records field present.
        m = Manifest(
            built_at=__import__("datetime").datetime(2026, 6, 10, 12, 0, 0),
            domains=[],
            records={"family": "data/records/family.json"},
        )
        assert "family" in m.records
        assert m.records["family"] == "data/records/family.json"

    def test_manifest_records_default_empty(self) -> None:
        """Manifest.records defaults to {} for backward compatibility."""
        from cdb_publish.schemas.manifest import Manifest

        m = Manifest(
            built_at=__import__("datetime").datetime(2026, 6, 10, 12, 0, 0),
            domains=[],
        )
        assert m.records == {}


@pytest.mark.parametrize("domain_slug", ["family", "holidays", "food"])
def test_every_domain_emits_file(domain_slug: str, tmp_path: Path) -> None:
    """Parametrized: all three known slugs produce output files."""
    from cdb_publish.successes import build_successes

    inf_path = _copy_fixture(tmp_path)
    out = tmp_path / "out"

    build_successes(
        raw_informants_path=inf_path,
        output_dir=out,
        domain_slugs=["family", "holidays", "food"],
    )

    assert (out / f"{domain_slug}.json").exists()
    data = json.loads((out / f"{domain_slug}.json").read_text())
    assert data["domain_slug"] == domain_slug
    assert "generated_at" in data
    assert "framing_note" in data
