#!/usr/bin/env python3
"""Inspect InformantRecords, LLM transcripts, and step output.

Filter by model, domain, qa_passed, or informant_id; show verbatim
prompts / responses / thinking traces, parsed piles and matrices,
or a one-line summary. Read-only.

Examples:

    # One-line summary of every record in data/raw/informants.jsonl
    python scripts/inspect.py

    # Records for one model on one domain
    python scripts/inspect.py --model x-ai/grok-4 --domain family

    # Only failed records
    python scripts/inspect.py --failed

    # Show the pile_sort prompt + response for one specific record
    python scripts/inspect.py --id 5e0930e7c2a32cd0 --step pile_sort --show prompt,response

    # Show all pile-sort responses for GLM (the T4 failure class)
    python scripts/inspect.py --model z-ai/glm-5.1 --step pile_sort --show response

    # Show reasoning traces where they exist
    python scripts/inspect.py --model anthropic/claude-opus-4.6 --step pile_sort --show thinking

    # Dump one full record as JSON
    python scripts/inspect.py --id 5e0930e7c2a32cd0 --format json

    # Use a different JSONL file (e.g., the T3 canary subset)
    python scripts/inspect.py --file data/raw/informants.jsonl --failed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_JSONL = Path("data/raw/informants.jsonl")

# Step name aliases: user types "freelist" or "free_list" interchangeably.
STEP_ALIASES = {
    "freelist": "freelist",
    "free_list": "freelist",
    "free-list": "freelist",
    "pile_sort": "pile_sort",
    "pilesort": "pile_sort",
    "pile-sort": "pile_sort",
    "interview": "interview",
    "pile_interview": "interview",
}

SHOW_FIELDS = {"prompt", "response", "thinking", "parsed", "meta", "all", "summary"}


def _load(path: Path) -> list[dict]:
    if not path.exists():
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        sys.exit(2)
    records: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            s = line.strip()
            if not s:
                continue
            try:
                records.append(json.loads(s))
            except json.JSONDecodeError as e:
                print(
                    f"WARN: skipping malformed line {line_num}: {e}",
                    file=sys.stderr,
                )
    return records


def _filter(
    records: list[dict],
    model: str | None,
    domain: str | None,
    informant_id: str | None,
    only_failed: bool,
    only_passed: bool,
) -> list[dict]:
    out = records
    if model:
        out = [r for r in out if r.get("model_id") == model]
    if domain:
        out = [r for r in out if r.get("domain_slug") == domain]
    if informant_id:
        # Accept a prefix match so short hashes work.
        out = [r for r in out if r.get("informant_id", "").startswith(informant_id)]
    if only_failed:
        out = [r for r in out if r.get("qa_passed") is False]
    if only_passed:
        out = [r for r in out if r.get("qa_passed") is True]
    return out


def _truncate(s: str, limit: int) -> str:
    if limit <= 0 or len(s) <= limit:
        return s
    return s[:limit] + f"\n  ... [truncated; {len(s) - limit} more chars]"


def _render_summary(r: dict) -> str:
    iid = r.get("informant_id", "?")[:12]
    mid = r.get("model_id", "?")
    dom = r.get("domain_slug", "?")
    idx = r.get("run_index", "?")
    qa = r.get("qa_passed")
    qa_tag = "PASS" if qa is True else ("FAIL" if qa is False else "????")

    fl = r.get("freelist", {})
    ps = r.get("pile_sort", {})
    iv = r.get("interview", {})

    items = len(fl.get("parsed_items") or [])
    piles = len(ps.get("parsed_piles") or [])
    labels = len(iv.get("parsed_labels") or []) if iv else 0

    notes = r.get("qa_notes") or ""
    notes_tail = f"  {notes}" if notes else ""
    return (
        f"  {iid}  {mid:40s}  {dom:10s}  run={idx}  "
        f"{qa_tag}  fl={items:3d} ps={piles:3d} iv={labels:3d}{notes_tail}"
    )


def _render_step(
    step_name: str, step: dict | None, show: set[str], truncate: int
) -> str:
    if not step:
        return f"--- {step_name} ---\n  <missing>\n"
    lines = [f"--- {step_name} ---"]
    if "prompt" in show or "all" in show:
        p = step.get("prompt_verbatim", "") or ""
        lines.append("  prompt_verbatim:")
        lines.append("    " + _truncate(p, truncate).replace("\n", "\n    "))
    if "response" in show or "all" in show:
        r = step.get("response_verbatim", "") or ""
        lines.append("  response_verbatim:")
        lines.append("    " + _truncate(r, truncate).replace("\n", "\n    "))
    if "thinking" in show or "all" in show:
        t = step.get("thinking_verbatim", "") or ""
        if t:
            lines.append("  thinking_verbatim:")
            lines.append("    " + _truncate(t, truncate).replace("\n", "\n    "))
        elif "thinking" in show:
            lines.append("  thinking_verbatim: <empty>")
    if "parsed" in show or "all" in show:
        # Per step, surface the useful parsed artifact.
        for key in ("parsed_items", "parsed_piles", "parsed_labels", "parsed_matrix"):
            if key in step and step[key] is not None:
                v = step[key]
                if isinstance(v, list):
                    preview = v if len(v) <= 30 else v[:30] + ["..."]
                    lines.append(f"  {key} (n={len(v)}): {preview!r}")
                else:
                    lines.append(f"  {key}: {str(v)[:200]}")
    if "meta" in show or "all" in show:
        meta_keys = (
            "input_tokens",
            "output_tokens",
            "latency_ms",
            "stop_reason",
            "prompt_version",
            "item_source",
        )
        meta = {k: step.get(k) for k in meta_keys if k in step}
        if meta:
            lines.append(f"  meta: {meta}")
    return "\n".join(lines) + "\n"


def _render_detail(r: dict, show: set[str], steps: set[str], truncate: int) -> str:
    header = (
        f"=== informant {r.get('informant_id', '?')[:12]}  "
        f"{r.get('model_id', '?')} × {r.get('domain_slug', '?')}  "
        f"run={r.get('run_index', '?')}  "
        f"qa_passed={r.get('qa_passed')} ==="
    )
    out = [header]

    if "meta" in show or "all" in show:
        for key in (
            "model_version_returned",
            "provider",
            "api_endpoint",
            "collection_date",
            "collection_mode",
            "temperature",
            "top_p",
            "max_tokens",
            "qa_notes",
            "truncation_type",
            "truncation_n",
            "capacity_note",
        ):
            if key in r:
                out.append(f"  {key}: {r[key]!r}")
        out.append("")

    if "freelist" in steps:
        out.append(_render_step("freelist", r.get("freelist"), show, truncate))
    if "pile_sort" in steps:
        out.append(_render_step("pile_sort", r.get("pile_sort"), show, truncate))
    if "interview" in steps:
        out.append(_render_step("interview", r.get("interview"), show, truncate))

    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_JSONL,
        help=f"Path to informants.jsonl (default: {DEFAULT_JSONL})",
    )
    parser.add_argument("--model", help="Filter to one model_id (canonical form)")
    parser.add_argument("--domain", help="Filter to one domain_slug")
    parser.add_argument(
        "--id",
        dest="informant_id",
        help="Filter to one informant_id (prefix match OK)",
    )
    parser.add_argument(
        "--failed",
        action="store_true",
        help="Only records with qa_passed=False",
    )
    parser.add_argument(
        "--passed",
        action="store_true",
        help="Only records with qa_passed=True",
    )
    parser.add_argument(
        "--step",
        default="all",
        help="Comma-separated: freelist,pile_sort,interview,all (default: all)",
    )
    parser.add_argument(
        "--show",
        default="summary",
        help=(
            "Comma-separated: prompt,response,thinking,parsed,meta,all,summary "
            "(default: summary — one line per record). "
            "Anything other than 'summary' switches to detail view."
        ),
    )
    parser.add_argument(
        "--truncate",
        type=int,
        default=2000,
        help="Truncate verbatim fields to N chars in detail view (default: 2000; 0 = no truncate)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. json dumps full record(s) as JSON; text is the default render",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Just print a count by model × domain × qa_passed and exit",
    )

    args = parser.parse_args()

    if args.failed and args.passed:
        print("ERROR: --failed and --passed are mutually exclusive", file=sys.stderr)
        return 2

    records = _load(args.file)
    filtered = _filter(
        records,
        model=args.model,
        domain=args.domain,
        informant_id=args.informant_id,
        only_failed=args.failed,
        only_passed=args.passed,
    )

    if not filtered:
        print(
            f"No records match. File: {args.file} (total: {len(records)})",
            file=sys.stderr,
        )
        return 1

    if args.count:
        from collections import Counter

        tally = Counter(
            (
                r.get("model_id", "?"),
                r.get("domain_slug", "?"),
                r.get("qa_passed"),
            )
            for r in filtered
        )
        print(f"{'model':40s}  {'domain':10s}  qa_passed  count")
        for (m, d, qa), n in sorted(tally.items()):
            qa_tag = "True" if qa is True else ("False" if qa is False else "null")
            print(f"  {m:40s}  {d:10s}  {qa_tag:9s}  {n}")
        print(f"\nTotal: {len(filtered)} records")
        return 0

    if args.format == "json":
        if len(filtered) == 1:
            print(json.dumps(filtered[0], indent=2, ensure_ascii=False))
        else:
            print(json.dumps(filtered, indent=2, ensure_ascii=False))
        return 0

    show = {s.strip() for s in args.show.split(",") if s.strip()}
    bad = show - SHOW_FIELDS
    if bad:
        print(
            f"ERROR: unknown --show field(s): {sorted(bad)}. "
            f"Valid: {sorted(SHOW_FIELDS)}",
            file=sys.stderr,
        )
        return 2

    # Resolve --step
    step_tokens = {s.strip() for s in args.step.split(",") if s.strip()}
    if "all" in step_tokens:
        steps = {"freelist", "pile_sort", "interview"}
    else:
        steps = set()
        for tok in step_tokens:
            canonical = STEP_ALIASES.get(tok)
            if canonical is None:
                print(
                    f"ERROR: unknown --step value: {tok}. "
                    f"Valid: freelist, pile_sort, interview, all",
                    file=sys.stderr,
                )
                return 2
            steps.add(canonical)

    # Summary view (default): one line per record.
    if show == {"summary"}:
        print(f"# File: {args.file}  ({len(filtered)} of {len(records)} records)")
        print(
            f"  {'id[:12]':12s}  {'model_id':40s}  {'domain':10s}  run  "
            f"qa    freelist pile_sort interview_label counts"
        )
        for r in filtered:
            print(_render_summary(r))
        return 0

    # Detail view: full render of each matched record.
    for r in filtered:
        print(_render_detail(r, show, steps, args.truncate))
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
