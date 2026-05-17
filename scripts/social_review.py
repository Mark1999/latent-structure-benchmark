#!/usr/bin/env python3
"""Social post human-review CLI — Phase 7 T5.

Lists drafts in out/social/queue/pending/, sorted oldest-first by created_at.
For each draft, displays canonical fields per CDA SME T5 §5.1 and accepts:

    y  →  approve (move to approved/)
    n  →  reject  (prompt for rejection reason; move to failed/ + sidecar JSON)
    e  →  edit    ($EDITOR with original text; re-validate; move to approved/
                   on pass, stay in pending/ with text_history updated on fail)
    s  →  skip    (advance to next draft; no state change)
    q  →  quit    (stop; remaining drafts stay in pending/)

CDA SME T5 binding notes applied:
  §5.1  — six canonical column headers; "Drafter self-rating" NOT "Confidence"
  §5.2  — four canonical framing_checks keys displayed verbatim + BUG flag
  §5.3  — five closed rejection-reason codes + optional free-text note;
           Choice B (sidecar JSON) — no schema change
  §5.4  — editor opens with original draft text; tempfile preamble stripped
  §5.5  — edit-failure screen with neutral validator-as-subject wording
  §5.6  — q leaves draft in pending/ unchanged; no "deferred" state
  §5.7  — five canonical per-TriggerType summary strings
  §5.8  — sorted oldest-first by created_at
  §5.9  — [BUG] rendering on queue-contract violations
  §5.10 — no real API calls; only reads/writes out/social/queue/ and $EDITOR tempfile
  §5.11 — MONTHLY_ROUNDUP uses T1 §5.7-compliant phrasing at display layer
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Ensure the project packages are importable when run directly.
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT / "packages" / "cdb_core"))
sys.path.insert(0, str(_REPO_ROOT / "packages" / "cdb_social"))

from cdb_core.schemas import SocialDraft, SocialTrigger, TriggerType  # noqa: E402
from cdb_social.drafters import validate_draft  # noqa: E402
from cdb_social.queue import (  # noqa: E402
    DraftNotFoundError,
    WrongQueueStateError,
    list_pending,
    load_draft,
    move,
    save_draft,
)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_QUEUE_ROOT = Path("out/social/queue")

REJECTION_CODES = ("forbidden_vocab", "register_boundary", "bare_numeric", "off_topic", "other")

_PASS_SYMBOL = "✓"  # ✓
_FAIL_SYMBOL = "✗"  # ✗

# ANSI codes — used only for the [BUG] marker (§5.9).
_ANSI_RED_BOLD = "\033[1;31m"
_ANSI_RESET = "\033[0m"

# ─────────────────────────────────────────────────────────────────────────────
# §5.7 — Trigger summary strings (binding wording per CDA SME T5)
# ─────────────────────────────────────────────────────────────────────────────


def format_trigger_summary(trigger: SocialTrigger) -> str:
    """Return the canonical per-TriggerType summary string.

    Wording bindings per CDA SME T5 §5.7:
    - DIVERGENCE: "max pairwise distance" (NOT "pairwise gap")
    - DRIFT: "Procrustes distance" verbatim; placeholder caveat mandatory
    - MONTHLY_ROUNDUP: "monthly cross-domain categorical-structure roundup"
      (T1 §5.7-compliant; applied early at display layer per §5.11)
    """
    ev: dict[str, Any] = trigger.evidence or {}
    tt = trigger.trigger_type

    def _get(key: str) -> str:
        val = ev.get(key)
        return str(val) if val is not None else "??"

    if tt == TriggerType.NEW_MODEL:
        model_id = trigger.model_id or ev.get("model_id") or "??"
        domain_slug = trigger.domain_slug or ev.get("first_seen_in_domain") or "??"
        return f"{model_id} added to {domain_slug} domain (first seen in domain)."

    if tt == TriggerType.NEW_DOMAIN:
        domain_slug = trigger.domain_slug or ev.get("domain_slug") or "??"
        n_models = _get("n_models")
        return f"{domain_slug} domain added (n={n_models} models)."

    if tt == TriggerType.DIVERGENCE:
        domain_slug = trigger.domain_slug or ev.get("domain_slug") or "??"
        model_pair: list[str] = ev.get("model_pair", ["??", "??"])
        mp0 = model_pair[0] if len(model_pair) > 0 else "??"
        mp1 = model_pair[1] if len(model_pair) > 1 else "??"
        try:
            old_high = float(ev["old_high"])
            new_high = float(ev["new_high"])
            gap_delta = float(ev["gap_delta"])
            return (
                f"{domain_slug}: max pairwise distance increased from {old_high:.3f} "
                f"to {new_high:.3f} (Δ {gap_delta:+.3f}) between {mp0} and {mp1}."
            )
        except (KeyError, TypeError, ValueError):
            return (
                f"{domain_slug}: max pairwise distance increased from {_get('old_high')} "
                f"to {_get('new_high')} (Δ {_get('gap_delta')}) between {mp0} and {mp1}."
            )

    if tt == TriggerType.DRIFT:
        model_version = ev.get("model_version_returned", "??")
        try:
            proc_dist = float(ev["procrustes_distance"])
            proc_dist_str = f"{proc_dist:.3f}"
        except (KeyError, TypeError, ValueError):
            proc_dist_str = _get("procrustes_distance")
        date_pair: list[str] = ev.get("date_pair", ["??", "??"])
        dp0 = date_pair[0] if len(date_pair) > 0 else "??"
        dp1 = date_pair[1] if len(date_pair) > 1 else "??"
        # Mandatory placeholder caveat per §5.7 while kickoff §7.3 lockout is engaged.
        return (
            f"{model_version}: Procrustes distance {proc_dist_str} "
            f"between {dp0} and {dp1} "
            f"(threshold 0.15 placeholder; drift trigger lockout is engaged per "
            f"kickoff §7.3 until multi-date data validates threshold)."
        )

    if tt == TriggerType.MONTHLY_ROUNDUP:
        # §5.7 / §5.11: T1 §5.7-compliant phrasing applied early at display layer.
        month = ev.get("month", "??")
        return f"Monthly cross-domain categorical-structure roundup for {month}."

    # Fallback for unknown trigger types.
    return f"[WARN] Unknown trigger type: {tt!r}. Evidence: {ev}"


# ─────────────────────────────────────────────────────────────────────────────
# §5.2 — Framing checks display
# ─────────────────────────────────────────────────────────────────────────────

_CANONICAL_FRAMING_CHECK_KEYS = (
    "hypothesis_framing",
    "cognition_attribution",
    "bare_numeric_without_ci",
    "register_boundary",
)


def _format_framing_checks(draft: SocialDraft) -> str:
    """Format the framing_checks dict per §5.2.

    Four canonical keys displayed verbatim first; additional keys (platform-
    specific) rendered below, sorted alphabetically.  Pass/fail symbols per spec.
    """
    checks = draft.framing_checks
    lines: list[str] = []

    # Render the four canonical keys in canonical order.
    for key in _CANONICAL_FRAMING_CHECK_KEYS:
        val = checks.get(key)
        symbol = "?" if val is None else (_PASS_SYMBOL if val else _FAIL_SYMBOL)
        lines.append(f"  {key:<28} {symbol}")

    # Render any additional keys (platform-specific) in sorted order.
    extra_keys = sorted(k for k in checks if k not in _CANONICAL_FRAMING_CHECK_KEYS)
    for key in extra_keys:
        val = checks[key]
        symbol = _PASS_SYMBOL if val else _FAIL_SYMBOL
        lines.append(f"  {key:<28} {symbol}")

    return "\n".join(lines)


def _format_forbidden_terms(draft: SocialDraft) -> str:
    """Format the forbidden_terms_hit field.

    Non-empty list signals a queue-contract violation (§5.9).
    """
    hits = draft.forbidden_terms_hit
    if not hits:
        return "  none"
    # [BUG] rendering per §5.9 — bold-red for visibility.
    bug_header = (
        f"{_ANSI_RED_BOLD}[BUG] Queue-contract violation: "
        f"this draft should not have reached pending/{_ANSI_RESET}"
    )
    items = ", ".join(repr(h) for h in hits)
    return (
        f"  {bug_header}\n"
        f"  Matched: {items}\n"
        f"  Likely cause: drafter validator bypass. Do not approve;\n"
        f"  reject with reason 'other' and document the bypass."
    )


def _check_queue_contract(draft: SocialDraft) -> bool:
    """Return True if the draft satisfies the queue-acceptance contract."""
    return (
        not draft.forbidden_terms_hit
        and draft.framing_check_passed
        and all(v is not False for v in draft.framing_checks.values())
    )


# ─────────────────────────────────────────────────────────────────────────────
# Display a draft
# ─────────────────────────────────────────────────────────────────────────────

def _display_draft(draft: SocialDraft, index: int, total: int) -> None:
    """Print a draft to stdout per the canonical §5.1 display format."""
    contract_ok = _check_queue_contract(draft)

    print()
    print(f"─── Draft {index} of {total} ───")

    # §5.1 canonical column headers.
    print(f"Draft ID:            {draft.draft_id}")
    print(f"Platform:            {draft.platform.value}")
    print(f"Drafter version:     {draft.drafter_version}")
    print(f"Prompt version:      {draft.prompt_version}")
    # "Drafter self-rating" — NEVER "Confidence" per §5.1 / T1 §5.4.
    print(f"Drafter self-rating: {draft.drafter_self_rating:.2f}")
    print(f"Created at:          {draft.created_at.isoformat()}")
    print(f"Suggested posting:   {draft.suggested_posting_time.isoformat()}")
    print()

    # §5.7 Trigger summary.
    print("Trigger:")
    print(f"  Type:    {draft.trigger.trigger_type.value}")
    summary = format_trigger_summary(draft.trigger)
    for line in summary.splitlines():
        print(f"  Summary: {line}")
    print()

    # Draft text verbatim.
    print("Draft text (verbatim):")
    print("─" * 45)
    print(draft.text)
    print("─" * 45)
    print()

    # §5.2 Framing checks — four canonical keys verbatim.
    print("Framing checks:")
    print(_format_framing_checks(draft))
    print()

    # forbidden_terms_hit — with [BUG] flag if non-empty (§5.9).
    print("Forbidden terms hit:")
    print(_format_forbidden_terms(draft))
    print()

    # Queue-contract [BUG] summary (§5.9).
    if not contract_ok:
        print(
            f"{_ANSI_RED_BOLD}[BUG] Queue-contract violation: "
            f"framing_check_passed={draft.framing_check_passed}. "
            f"Do not approve; reject with reason 'other' and "
            f"document the bypass.{_ANSI_RESET}"
        )
        print()

    # §5.1 remaining canonical fields.
    print(f"Methodology URL: {draft.methodology_url}")
    print(f"Dashboard URL:   {draft.dashboard_url}")

    if draft.text_history:
        print(f"Edit history:    {len(draft.text_history)} prior version(s) in text_history")

    print()


# ─────────────────────────────────────────────────────────────────────────────
# §5.3 — Reject flow (Choice B: sidecar JSON)
# ─────────────────────────────────────────────────────────────────────────────

def _prompt_rejection_reason() -> tuple[str, str | None]:
    """Prompt operator for a rejection reason (5-code enum) and optional note.

    Returns (reason_code, free_text_note_or_None).
    Re-prompts on invalid input.
    """
    code_labels = "/".join(REJECTION_CODES)
    while True:
        reason = input(f"Rejection reason? [{code_labels}] ").strip().lower()
        if reason in REJECTION_CODES:
            break
        print(f"  Invalid reason. Choose one of: {code_labels}")

    note_raw = input("(optional) Free-text note: ").strip()
    note = note_raw if note_raw else None
    return reason, note


def _write_rejection_sidecar(
    draft_id: str,
    reason: str,
    note: str | None,
    queue_root: Path,
) -> None:
    """Write the sidecar JSON at failed/{draft_id}.reason.json (Choice B per §5.3)."""
    sidecar_path = queue_root / "failed" / f"{draft_id}.reason.json"
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "rejection_reason": reason,
        "free_text_note": note,
        "rejected_at": datetime.now(UTC).isoformat(),
    }
    sidecar_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# §5.4 — Edit flow ($EDITOR with original text; preamble stripped)
# ─────────────────────────────────────────────────────────────────────────────

_PREAMBLE_SENTINEL = "# LSB-REVIEW-PREAMBLE"

def _build_tempfile_preamble(draft: SocialDraft) -> str:
    """Build the §5.4 tempfile preamble (stripped before re-validation)."""
    lines = [
        _PREAMBLE_SENTINEL,
        f"# Editing draft {draft.draft_id} for {draft.platform.value}.",
        "# §1.5.4 forbidden vocab: no \"believes\" / \"thinks\" / \"worldview\" applied",
        "# to models; no \"within-model consensus\" or \"within-model CCM\" phrasings.",
        "# Every numeric finding requires an adjacent CI. Save and quit to validate.",
        "# Lines starting with `#` are stripped before validation.",
        _PREAMBLE_SENTINEL,
        "",
    ]
    return "\n".join(lines)


def _strip_preamble(raw: str) -> str:
    """Strip all lines beginning with '#' (the §5.4 preamble stripping rule)."""
    return "\n".join(
        line for line in raw.splitlines() if not line.startswith("#")
    ).strip()


def _get_editor() -> str:
    """Return the editor to use: $EDITOR, then $VISUAL, then vi."""
    return os.environ.get("EDITOR") or os.environ.get("VISUAL") or "vi"


def _open_editor(initial_text: str) -> str:
    """Open $EDITOR with initial_text, return the edited content after save+quit."""
    editor = _get_editor()
    preamble = _build_tempfile_preamble_raw()
    full_content = preamble + initial_text

    import contextlib

    fd, tmp_path = tempfile.mkstemp(suffix=".txt", prefix="lsb_draft_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(full_content)
        subprocess.run([editor, tmp_path], check=False)
        return Path(tmp_path).read_text(encoding="utf-8")
    finally:
        with contextlib.suppress(OSError):
            Path(tmp_path).unlink(missing_ok=True)


def _build_tempfile_preamble_raw() -> str:
    """Return raw preamble string (no draft-specific data; used by _open_editor)."""
    lines = [
        "# LSB Social Draft Editor",
        "# §1.5.4 forbidden vocab: no \"believes\" / \"thinks\" / \"worldview\" applied",
        "# to models; no \"within-model consensus\" or \"within-model CCM\" phrasings.",
        "# Every numeric finding requires an adjacent CI. Save and quit to validate.",
        "# Lines starting with `#` are stripped before validation.",
        "",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# §5.5 — Edit-failure display (validator-as-subject; no operator-shaming)
# ─────────────────────────────────────────────────────────────────────────────

def _display_edit_failure(
    forbidden_terms: list[str],
    framing_checks: dict[str, bool],
    bare_numerics: list[str] | None = None,
) -> None:
    """Display the §5.5 edit-failure screen.

    Subject is the validator; no operator-shaming language.
    """
    print()
    print("Edit did not pass validator. Draft returned to pending/ with edit history.")
    print()
    print("Failed checks:")

    # Report each failing framing check.
    matched_check_keys: set[str] = set()
    for key, passed in framing_checks.items():
        if not passed:
            if key == "bare_numeric_without_ci" and bare_numerics:
                for num in bare_numerics:
                    print(f"  {key}  — bare numeric {num!r} without adjacent CI")
                matched_check_keys.add(key)
            elif key in (
                "cognition_attribution",
                "hypothesis_framing",
                "register_boundary",
            ) and forbidden_terms:
                for term in forbidden_terms:
                    print(f"  {key}  — matched: {term!r}")
                matched_check_keys.add(key)
            else:
                print(f"  {key}  — check failed")

    # Any forbidden terms not already surfaced under a specific framing check.
    if forbidden_terms and not matched_check_keys - {"bare_numeric_without_ci"}:
        for term in forbidden_terms:
            print(f"  forbidden_terms_hit  — matched: {term!r}")

    print()


# ─────────────────────────────────────────────────────────────────────────────
# Main review loop
# ─────────────────────────────────────────────────────────────────────────────

def _run_review(queue_root: Path) -> None:
    """Execute the interactive review loop over pending/ drafts."""
    pending = list_pending(queue_root)
    total = len(pending)

    if total == 0:
        print("No drafts in pending/.")
        return

    print(f"Found {total} draft(s) in pending/.")

    reviewed = 0

    for i, path in enumerate(pending, start=1):
        # Load the draft (may have been moved by an earlier action).
        if not path.exists():
            # Draft was moved/deleted between list and loop — skip silently.
            continue

        try:
            draft = load_draft(path)
        except Exception as e:
            print(f"[WARN] Could not load draft from {path}: {e}. Skipping.")
            continue

        _display_draft(draft, i, total)

        # Action loop for this draft.
        while True:
            try:
                action = input("[y/n/e/s/q] ? ").strip().lower()
            except EOFError:
                action = "q"

            if action == "q":
                remaining = total - reviewed
                print(f"Quit. {remaining} draft(s) remain in pending/.")
                return

            if action == "s":
                print("Skipped.")
                reviewed += 1
                break

            if action == "y":
                try:
                    new_path = move(draft.draft_id, "pending", "approved", queue_root=queue_root)
                    print(f"Approved. Moved to {new_path}.")
                except (WrongQueueStateError, DraftNotFoundError) as e:
                    print(f"[ERROR] Could not approve: {e}")
                reviewed += 1
                break

            if action == "n":
                reason, note = _prompt_rejection_reason()
                try:
                    move(draft.draft_id, "pending", "failed", queue_root=queue_root)
                    _write_rejection_sidecar(draft.draft_id, reason, note, queue_root)
                    print(f"Rejected ({reason}). Moved to failed/.")
                except (WrongQueueStateError, DraftNotFoundError) as e:
                    print(f"[ERROR] Could not reject: {e}")
                reviewed += 1
                break

            if action == "e":
                # §5.4: open editor with original draft text.
                # The edit loop continues until validator passes or operator declines.
                edit_buffer = draft.text  # start with the current draft text
                edit_done = False
                edit_approved = False

                while not edit_done:
                    edited_raw = _open_editor(edit_buffer)
                    edited_text = _strip_preamble(edited_raw)

                    if not edited_text.strip():
                        print("Edit was empty. Draft returned to pending/ unchanged.")
                        edit_done = True
                        break

                    # §5.5: re-validate the edited text.
                    from cdb_social.drafters.base import validate_draft_numeric_ci_adjacency
                    forbidden_terms, framing_checks = validate_draft(edited_text)
                    framing_check_passed = not forbidden_terms and all(framing_checks.values())

                    if framing_check_passed:
                        # Update draft: append original text to text_history, set new text.
                        updated = draft.model_copy(
                            update={
                                "text_history": draft.text_history + [draft.text],
                                "text": edited_text,
                                "forbidden_terms_hit": forbidden_terms,
                                "framing_checks": framing_checks,
                                "framing_check_passed": framing_check_passed,
                            }
                        )
                        save_draft(updated, path)
                        try:
                            new_path = move(
                                updated.draft_id, "pending", "approved", queue_root=queue_root
                            )
                            print(f"Edit passed validator. Approved. Moved to {new_path}.")
                        except (WrongQueueStateError, DraftNotFoundError) as e:
                            print(f"[ERROR] Could not approve after edit: {e}")
                        edit_done = True
                        edit_approved = True
                    else:
                        # §5.5: surface failure with neutral validator-as-subject wording.
                        _ci_ok, bare_numerics = validate_draft_numeric_ci_adjacency(edited_text)
                        _display_edit_failure(forbidden_terms, framing_checks, bare_numerics)

                        # Append failed edit to text_history; do NOT overwrite draft.text.
                        updated = draft.model_copy(
                            update={
                                "text_history": draft.text_history + [edited_text],
                            }
                        )
                        save_draft(updated, path)
                        draft = updated

                        # §5.5: offer to edit again.
                        try:
                            again = input("Edit again? [y/n] ").strip().lower()
                        except EOFError:
                            again = "n"

                        if again == "y":
                            # Reopen editor with the failed edit as buffer.
                            edit_buffer = edited_text
                            # Continue the inner edit while loop.
                        else:
                            print("Draft returned to pending/.")
                            edit_done = True

                if edit_approved:
                    reviewed += 1
                    break
                # If not approved, fall through to continue the action loop
                # (re-prompt action for this draft).
                continue

            else:
                print("  Unknown action. Enter y, n, e, s, or q.")

    remaining = total - reviewed
    if remaining > 0:
        print(f"Review complete. {remaining} draft(s) were not reviewed (skipped).")
    else:
        print("Review complete. All drafts reviewed.")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Human review CLI for social drafts in out/social/queue/pending/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--queue-root",
        type=Path,
        default=DEFAULT_QUEUE_ROOT,
        help=f"Path to the queue root directory (default: {DEFAULT_QUEUE_ROOT}).",
    )
    parser.add_argument(
        "--sort",
        choices=["created_at", "self_rating"],
        default="created_at",
        help=(
            "Sort order for pending drafts. "
            "'created_at' (default): oldest-first per §5.8. "
            "'self_rating': drafter-self-rating-descending (operator convenience)."
        ),
    )
    args = parser.parse_args(argv)

    queue_root: Path = args.queue_root.resolve()

    if not queue_root.exists():
        print(f"Queue root not found: {queue_root}")
        sys.exit(1)

    _run_review(queue_root)


if __name__ == "__main__":
    main()
