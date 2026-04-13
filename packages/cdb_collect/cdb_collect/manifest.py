"""SHA256 manifest computation for InformantRecords. See ARCHITECTURE.md §1 commitment 7."""

from __future__ import annotations

import hashlib
import json


def _sha256(text: str) -> str:
    """Compute SHA256 hex digest of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_manifest(
    freelist_prompt: str,
    freelist_response: str,
    pilesort_prompt: str,
    pilesort_response: str,
    interview_prompt: str,
    interview_response: str,
    request_params: dict,
) -> dict[str, str]:
    """Compute the 8-key SHA256 manifest for an InformantRecord.

    The 8 keys are: freelist_prompt, freelist_response, pilesort_prompt,
    pilesort_response, interview_prompt, interview_response, request_params,
    informant_record_total.

    Args:
        freelist_prompt: Verbatim free-list prompt.
        freelist_response: Verbatim free-list response.
        pilesort_prompt: Verbatim pile-sort prompt (empty for Milestone A).
        pilesort_response: Verbatim pile-sort response (empty for Milestone A).
        interview_prompt: Verbatim interview prompt (empty for Milestone A).
        interview_response: Verbatim interview response (empty for Milestone A).
        request_params: Dict of collection parameters.

    Returns:
        Dict with exactly 8 SHA256 hex digest strings.
    """
    manifest: dict[str, str] = {
        "freelist_prompt": _sha256(freelist_prompt),
        "freelist_response": _sha256(freelist_response),
        "pilesort_prompt": _sha256(pilesort_prompt),
        "pilesort_response": _sha256(pilesort_response),
        "interview_prompt": _sha256(interview_prompt),
        "interview_response": _sha256(interview_response),
        "request_params": _sha256(
            json.dumps(request_params, sort_keys=True)
        ),
    }

    # Total hash covers all other manifest entries
    total_input = "|".join(
        f"{k}={v}" for k, v in sorted(manifest.items())
    )
    manifest["informant_record_total"] = _sha256(total_input)

    return manifest
