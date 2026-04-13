"""Deterministic run ID generation for LSB.

See ARCHITECTURE.md §3.1.
"""

import hashlib


def run_id(model: str, domain: str, step: str,
           prompt_version: str, run_index: int) -> str:
    """Deterministic SHA256[:16] of the tuple. Stable across machines."""
    key = f"{model}|{domain}|{step}|{prompt_version}|{run_index}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
