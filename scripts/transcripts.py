#!/usr/bin/env python3
"""Render informant JSONL records into human-readable verbatim transcripts.

This script is a mechanical formatter. It reads data/raw/informants.jsonl
and writes one Markdown file per informant session to data/transcripts/.
Each transcript contains ONLY:

  - Session metadata (mechanical facts from the record)
  - The exact prompt sent to the model (interviewer question)
  - The exact response returned by the model (informant answer)

NO parsed/coded fields. NO commentary. NO analysis. NO interpretation.
The parsed_items, parsed_piles, and parsed_pile_labels are the researcher's
coding layer and do not belong in the transcript — just as a human
interview transcript would not contain the researcher's margin notes.

Usage:
    python scripts/transcripts.py                    # render all records
    python scripts/transcripts.py --model gpt-4o     # filter by model substring
    python scripts/transcripts.py --run 0            # filter by run index
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path("data/raw")
OUT_DIR = Path("data/transcripts")
JSONL_PATH = DATA_DIR / "informants.jsonl"


def render_transcript(rec: dict) -> str:
    """Render one InformantRecord dict into a verbatim Markdown transcript."""
    lines: list[str] = []

    # ── Session header ──────────────────────────────────────────────
    lines.append(f"# Informant Transcript: {rec['informant_id']}")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for key in [
        "informant_id",
        "model_id",
        "model_version_returned",
        "family",
        "provider",
        "collection_method",
        "origin_country",
        "open_weights",
        "domain_slug",
        "run_index",
        "collection_date",
        "temperature",
        "top_p",
        "max_tokens",
        "system_prompt",
        "provider_request_id",
        "api_endpoint",
        "api_version",
        "knowledge_cutoff",
        "alignment_method",
        "qa_passed",
        "qa_notes",
        "sha256_manifest",
    ]:
        val = rec.get(key)
        if val is None:
            val = ""
        # SHA256 is a dict — render each hash on its own line
        if key == "sha256_manifest" and isinstance(val, dict):
            val = "<br>".join(f"`{k}`: `{v}`" for k, v in val.items())
        lines.append(f"| {key} | {val} |")
    lines.append("")

    # ── Steps ───────────────────────────────────────────────────────
    step_map = [
        ("freelist", "Step 1: Free List"),
        ("pile_sort", "Step 2: Pile Sort"),
        ("interview", "Step 3: Pile Interview"),
    ]

    for step_key, step_title in step_map:
        step = rec.get(step_key)
        if not step:
            lines.append(f"## {step_title}")
            lines.append("")
            lines.append("*(not collected)*")
            lines.append("")
            continue

        stop = step.get("stop_reason", "")
        if stop == "not_collected":
            lines.append(f"## {step_title}")
            lines.append("")
            lines.append("*(not collected)*")
            lines.append("")
            continue

        lines.append(f"## {step_title}")
        lines.append("")
        lines.append(
            f"| Prompt version | Tokens in | Tokens out "
            f"| Latency (ms) | Stop reason |"
        )
        lines.append("|---|---|---|---|---|")
        lines.append(
            f"| {step.get('prompt_version', '')} "
            f"| {step.get('input_tokens', '')} "
            f"| {step.get('output_tokens', '')} "
            f"| {step.get('latency_ms', '')} "
            f"| {step.get('stop_reason', '')} |"
        )
        lines.append("")

        # Interviewer prompt — verbatim, in a fenced block
        lines.append("### Prompt (verbatim)")
        lines.append("")
        lines.append("```")
        lines.append(step.get("prompt_verbatim", ""))
        lines.append("```")
        lines.append("")

        # Informant response — verbatim, in a fenced block
        lines.append("### Response (verbatim)")
        lines.append("")
        lines.append("```")
        lines.append(step.get("response_verbatim", ""))
        lines.append("```")
        lines.append("")

    # ── Footer ──────────────────────────────────────────────────────
    lines.append("---")
    lines.append(
        "*This transcript is a mechanical rendering of the verbatim "
        "prompts and responses stored in the informant record. "
        "It has not been edited, interpreted, or annotated.*"
    )
    lines.append("")

    return "\n".join(lines)


def safe_filename(model_id: str) -> str:
    """Turn a model_id like 'openai/gpt-4o' into a filesystem-safe name."""
    return model_id.replace("/", "__")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render verbatim informant transcripts from JSONL."
    )
    parser.add_argument(
        "--model",
        help="Filter to records whose model_id contains this substring.",
    )
    parser.add_argument(
        "--run", type=int, help="Filter to a specific run_index."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUT_DIR,
        help=f"Output directory (default: {OUT_DIR}).",
    )
    args = parser.parse_args()

    if not JSONL_PATH.exists():
        print(f"Error: {JSONL_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    written = 0
    with open(JSONL_PATH) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)

            # Apply filters
            if args.model and args.model not in rec.get("model_id", ""):
                continue
            if args.run is not None and rec.get("run_index") != args.run:
                continue

            model_dir = safe_filename(rec.get("model_id", "unknown"))
            domain = rec.get("domain_slug", "unknown")
            run_idx = rec.get("run_index", 0)

            out_path = args.out / model_dir / domain / f"run_{run_idx:03d}.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)

            transcript = render_transcript(rec)
            out_path.write_text(transcript)
            written += 1

    print(f"Wrote {written} transcript(s) to {args.out}/")


if __name__ == "__main__":
    main()
