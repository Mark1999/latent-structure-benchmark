"""CDA Step 3 — pile interview / naming. See ARCHITECTURE.md §4.1.1."""

from __future__ import annotations

import re
from pathlib import Path

from cdb_core import InterviewRecord

from cdb_collect.adapters.base import AdapterResult, ModelAdapter

_PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(piles: list[list[str]], version: str = "v1") -> str:
    """Load and substitute the pile-interview prompt template."""
    path = _PROMPTS_DIR / version / "pile_interview.md"
    template = path.read_text(encoding="utf-8")

    # Format piles as numbered groups
    lines: list[str] = []
    for i, pile in enumerate(piles, 1):
        items_str = ", ".join(pile)
        lines.append(f"Group {i}: {items_str}")

    return template.replace("{{piles}}", "\n".join(lines))


class PileInterviewParseResult:
    """Result of parsing a pile-interview response.

    Carries the parsed labels and a mismatch signal when the parser
    extracted a different number of labels than the expected pile count.
    The mismatch is a structured signal (not an exception) so the runner
    can FAIL-and-record per CDA SME option (b) — docs/status/2026-04-20-f2-cda-sme-verdict.md.

    ``label_count_mismatch`` is None on a clean parse, or
    (expected, got) when counts differ. The raw response text is always
    preserved verbatim in the InterviewRecord regardless.
    """

    def __init__(
        self,
        labels: list[str],
        label_count_mismatch: tuple[int, int] | None = None,
    ) -> None:
        self.labels = labels
        self.label_count_mismatch = label_count_mismatch


def parse_pile_interview(
    text: str, expected_count: int,
) -> PileInterviewParseResult:
    """Parse pile interview response into a structured result.

    Args:
        text: Raw response text with one label per pile.
        expected_count: Expected number of labels (= number of piles).

    Returns:
        PileInterviewParseResult with parsed labels and an optional
        mismatch signal. Does NOT raise when counts differ — the caller
        is responsible for detecting the mismatch and handling it per
        the CDA SME FAIL-and-record policy (option b).
    """
    labels: list[str] = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        # Strip numbering: "1.", "1)", "1:", "Group 1:", etc.
        line = re.sub(r"^(?:group\s+)?\d+[\.\)\:]\s*", "", line, flags=re.IGNORECASE)
        line = re.sub(r"^[-\*]\s+", "", line)
        line = line.strip()

        # Skip lines that look like meta-commentary rather than labels
        line_lower = line.lower()
        if not line or any(line_lower.startswith(p) for p in (
            "here is", "here are", "here's", "below is", "below are",
            "the following", "these are", "this is", "i ",
            "sure", "certainly", "of course", "absolutely",
            "note:", "note that", "please note",
            "let me know", "feel free", "hope this",
        )):
            continue
        # Skip lines that are clearly sentences, not labels (>80 chars)
        if len(line) > 80:
            continue

        # Strip surrounding quotes if present
        if len(line) >= 2 and line[0] in ('"', "'") and line[-1] == line[0]:
            line = line[1:-1].strip()

        if line:
            labels.append(line)

    mismatch: tuple[int, int] | None = None
    if len(labels) != expected_count:
        mismatch = (expected_count, len(labels))

    return PileInterviewParseResult(labels=labels, label_count_mismatch=mismatch)


DEFAULT_INTERVIEW_TEMPERATURE: float = 0.3


async def run_pile_interview(
    adapter: ModelAdapter,
    piles: list[list[str]],
    run_index: int,
    prompt_version: str = "v1",
    *,
    temperature: float | None = None,
) -> tuple[InterviewRecord, AdapterResult]:
    """Execute the pile-interview step of the CDA protocol.

    Uses temperature 0.3 per ARCHITECTURE.md §4.1.3 when no override is
    provided.

    Args:
        temperature: Optional override for the sampling temperature. When
            None, uses ``DEFAULT_INTERVIEW_TEMPERATURE`` (0.3). Set to 0.0
            for the shakedown determinism cell.

    Returns:
        (InterviewRecord, AdapterResult) tuple.
    """
    prompt = load_prompt(piles, version=prompt_version)

    effective_temp = (
        temperature if temperature is not None else DEFAULT_INTERVIEW_TEMPERATURE
    )
    result = await adapter.complete(prompt, temperature=effective_temp)

    parse_result = parse_pile_interview(result.text, expected_count=len(piles))

    record = InterviewRecord(
        prompt_verbatim=prompt,
        prompt_version=prompt_version,
        response_verbatim=result.text,
        thinking_verbatim=result.thinking_text,
        response_object_json=result.raw_response,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        thoughts_token_count=result.thoughts_token_count,
        latency_ms=result.latency_ms,
        stop_reason=result.stop_reason,
        parsed_pile_labels=parse_result.labels,
    )

    return record, result
