"""Domain loader — reads YAML domain definitions. See ARCHITECTURE.md §3.2."""

from pathlib import Path

import yaml
from cdb_core import Domain

# Default location for domain definitions
_DOMAINS_DIR = Path(__file__).resolve().parents[4] / "data" / "domains"


def load_domain(slug: str, version: str = "v1") -> Domain:
    """Load a domain definition from its YAML file.

    Args:
        slug: Domain slug (e.g., "family").
        version: Domain version directory (default "v1").

    Returns:
        A validated Domain instance.

    Raises:
        FileNotFoundError: If the domain YAML file does not exist.
        ValueError: If the YAML content does not match the Domain schema.
    """
    path = _DOMAINS_DIR / version / f"{slug}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Domain definition not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid domain YAML (expected mapping): {path}")

    return Domain(**data)
