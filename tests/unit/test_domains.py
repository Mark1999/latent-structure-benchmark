"""Tests for domain loader. See ARCHITECTURE.md §3.2."""

import pytest
from cdb_collect.domains import load_domain
from cdb_core import Domain


def test_load_family_domain():
    domain = load_domain("family")
    assert isinstance(domain, Domain)
    assert domain.slug == "family"
    assert domain.version == "v1"
    assert domain.display_name == "Family Terms"
    assert domain.prompt_seed == "type of family relationship or family member"
    assert domain.truncation_k == 25


def test_load_nonexistent_domain():
    with pytest.raises(FileNotFoundError, match="Domain definition not found"):
        load_domain("nonexistent_domain_xyz")


def test_domain_round_trip():
    domain = load_domain("family")
    json_str = domain.model_dump_json()
    restored = Domain.model_validate_json(json_str)
    assert restored == domain
