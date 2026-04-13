"""Collection orchestrator — runs the three-step CDA protocol for a (model, domain) pair.

See ARCHITECTURE.md §4.1.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime

from cdb_core import Domain, InformantRecord

from cdb_collect.adapters.base import ModelAdapter
from cdb_collect.manifest import compute_manifest
from cdb_collect.protocol.free_list import run_free_list
from cdb_collect.protocol.pile_interview import run_pile_interview
from cdb_collect.protocol.pile_sort import run_pile_sort

logger = logging.getLogger(__name__)


def _informant_id(
    model_id: str, domain_slug: str, run_index: int, collection_date: str,
) -> str:
    """Deterministic informant ID: SHA256[:16] of the identity tuple."""
    key = f"{model_id}|{domain_slug}|{run_index}|{collection_date}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


async def run_informant(
    adapter: ModelAdapter,
    domain: Domain,
    run_index: int,
    *,
    prompt_version: str = "v1",
    system_prompt: str = "",
) -> InformantRecord:
    """Run the full CDA protocol and assemble an InformantRecord.

    Executes all three steps sequentially, chaining data between them:
    1. Free listing → parsed items
    2. Pile sorting (using free list items) → piles + binary matrix
    3. Pile interview (using piles) → pile labels

    Args:
        adapter: The model adapter to use.
        domain: The domain definition.
        run_index: The 0-based run index.
        prompt_version: Prompt template version.
        system_prompt: System prompt used for all steps.

    Returns:
        A fully populated InformantRecord.
    """
    now = datetime.now()
    collection_date_str = now.strftime("%Y-%m-%dT%H:%M:%S")

    # Step 1: Free listing (temperature 0.7)
    freelist_record, freelist_result = await run_free_list(
        adapter, domain, run_index, prompt_version=prompt_version,
    )

    # Step 2: Pile sorting (temperature 0.3) — receives items from Step 1
    pilesort_record, pilesort_result = await run_pile_sort(
        adapter,
        items=freelist_record.parsed_items,
        domain_seed=domain.prompt_seed,
        run_index=run_index,
        prompt_version=prompt_version,
    )

    # Step 3: Pile interview (temperature 0.3) — receives piles from Step 2
    interview_record, interview_result = await run_pile_interview(
        adapter,
        piles=pilesort_record.parsed_piles,
        run_index=run_index,
        prompt_version=prompt_version,
    )

    # Compute SHA256 manifest
    request_params = {
        "model_id": adapter.model.model_id,
        "domain_slug": domain.slug,
        "run_index": run_index,
        "prompt_version": prompt_version,
        "temperature_freelist": 0.7,
        "temperature_pilesort": 0.3,
        "temperature_interview": 0.3,
    }

    manifest = compute_manifest(
        freelist_prompt=freelist_record.prompt_verbatim,
        freelist_response=freelist_record.response_verbatim,
        pilesort_prompt=pilesort_record.prompt_verbatim,
        pilesort_response=pilesort_record.response_verbatim,
        interview_prompt=interview_record.prompt_verbatim,
        interview_response=interview_record.response_verbatim,
        request_params=request_params,
    )

    informant_id = _informant_id(
        adapter.model.model_id, domain.slug, run_index, collection_date_str,
    )

    return InformantRecord(
        informant_id=informant_id,
        domain_slug=domain.slug,
        run_index=run_index,
        collection_date=now,
        model_id=adapter.model.model_id,
        model_version_returned=freelist_result.model_version_returned,
        family=adapter.model.family,
        provider=adapter.model.provider,
        provider_request_id=freelist_result.provider_request_id,
        knowledge_cutoff=None,
        open_weights=adapter.model.open_weights,
        origin_country=adapter.model.origin,
        alignment_method=None,
        collection_method=adapter.model.collection_method,
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt=system_prompt,
        freelist=freelist_record,
        pile_sort=pilesort_record,
        interview=interview_record,
        sha256_manifest=manifest,
        qa_passed=True,
        qa_notes="",
    )
