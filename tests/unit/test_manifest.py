"""Tests for SHA256 manifest computation."""

from cdb_collect.manifest import compute_manifest


def test_manifest_has_8_keys():
    m = compute_manifest(
        freelist_prompt="prompt1",
        freelist_response="response1",
        pilesort_prompt="",
        pilesort_response="",
        interview_prompt="",
        interview_response="",
        request_params={"model": "test"},
    )
    expected_keys = {
        "freelist_prompt", "freelist_response",
        "pilesort_prompt", "pilesort_response",
        "interview_prompt", "interview_response",
        "request_params", "informant_record_total",
    }
    assert set(m.keys()) == expected_keys


def test_manifest_values_are_hex_sha256():
    m = compute_manifest(
        freelist_prompt="test",
        freelist_response="test",
        pilesort_prompt="",
        pilesort_response="",
        interview_prompt="",
        interview_response="",
        request_params={},
    )
    for v in m.values():
        assert len(v) == 64
        assert all(c in "0123456789abcdef" for c in v)


def test_manifest_deterministic():
    kwargs = dict(
        freelist_prompt="hello",
        freelist_response="world",
        pilesort_prompt="",
        pilesort_response="",
        interview_prompt="",
        interview_response="",
        request_params={"key": "value"},
    )
    m1 = compute_manifest(**kwargs)
    m2 = compute_manifest(**kwargs)
    assert m1 == m2


def test_manifest_changes_with_input():
    m1 = compute_manifest(
        freelist_prompt="a",
        freelist_response="b",
        pilesort_prompt="",
        pilesort_response="",
        interview_prompt="",
        interview_response="",
        request_params={},
    )
    m2 = compute_manifest(
        freelist_prompt="c",
        freelist_response="d",
        pilesort_prompt="",
        pilesort_response="",
        interview_prompt="",
        interview_response="",
        request_params={},
    )
    assert m1["freelist_prompt"] != m2["freelist_prompt"]
    assert m1["informant_record_total"] != m2["informant_record_total"]
