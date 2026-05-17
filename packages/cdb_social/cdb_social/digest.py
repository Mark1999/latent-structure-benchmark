"""Format a list of SocialTrigger objects as a plain-text daily digest email.

Wording bindings (T5 CDA SME verdict §5.5 / §5.7 — Reviewer enforces):
  DIVERGENCE:      "max pairwise distance" (NOT "pairwise gap")
  DRIFT:           "Procrustes distance" verbatim + placeholder caveat
  MONTHLY_ROUNDUP: "Monthly cross-domain categorical-structure roundup"
                   (NOT "state of cultural alignment roundup")

No LLM imports here — this module is pure text formatting per
Phase 7 §11.1 binding B-1.

See docs/status/2026-05-17-phase7-architect-kickoff.md §11.5 and
docs/status/2026-05-17-phase7-T5-cda-sme-verdict.md §5.5, §5.7.
"""

from __future__ import annotations

from datetime import datetime

from cdb_core.schemas import SocialTrigger, TriggerType

# ─────────────────────────────────────────────────────────────────────────────
# Per-trigger summary strings
# ─────────────────────────────────────────────────────────────────────────────
# Wording is binding per T5 CDA SME verdict §5.7.  The Reviewer enforces
# the exact canonical phrasing for DIVERGENCE, DRIFT, and MONTHLY_ROUNDUP.


def format_trigger_summary(trigger: SocialTrigger) -> str:
    """Return a one-to-two line summary string for a SocialTrigger.

    Wording per T5 CDA SME §5.7 (binding):
    - NEW_MODEL:       "{model_id} added to {domain_slug} domain"
    - NEW_DOMAIN:      "{domain_slug} domain added (n={n_models} models)"
    - DIVERGENCE:      "{domain_slug}/{model_pair[0]}↔{model_pair[1]}: max pairwise
                        distance went from {old_high} to {new_high} (Δ {gap_delta})"
    - DRIFT:           "{model_version_returned}: Procrustes distance
                        {procrustes_distance} between {date_pair[0]} and
                        {date_pair[1]}\n  ⚠ threshold 0.15 placeholder; lockout engaged"
    - MONTHLY_ROUNDUP: "Monthly cross-domain categorical-structure roundup for {month}"

    Missing evidence keys produce a {key}=?? placeholder (per §5.7 defensive pattern).
    """
    ev = trigger.evidence

    if trigger.trigger_type == TriggerType.NEW_MODEL:
        model_id = trigger.model_id or ev.get("model_id", "??")
        domain = trigger.domain_slug or ev.get("first_seen_in_domain", "??")
        return f"{model_id} added to {domain} domain"

    if trigger.trigger_type == TriggerType.NEW_DOMAIN:
        domain = trigger.domain_slug or ev.get("domain_slug", "??")
        n_models = ev.get("n_models", "??")
        return f"{domain} domain added (n={n_models} models)"

    if trigger.trigger_type == TriggerType.DIVERGENCE:
        domain = trigger.domain_slug or ev.get("domain_slug", "??")
        model_pair = ev.get("model_pair", ["??", "??"])
        m0 = model_pair[0] if len(model_pair) > 0 else "??"
        m1 = model_pair[1] if len(model_pair) > 1 else "??"
        old_high = ev.get("old_high", "??")
        new_high = ev.get("new_high", "??")
        gap_delta = ev.get("gap_delta", "??")
        # Format floats to 2 decimal places if they are numbers
        old_high_str = f"{old_high:.2f}" if isinstance(old_high, float) else str(old_high)
        new_high_str = f"{new_high:.2f}" if isinstance(new_high, float) else str(new_high)
        gap_delta_str = (
            f"{gap_delta:.2f}" if isinstance(gap_delta, float) else str(gap_delta)
        )
        return (
            f"{domain}/{m0}↔{m1}: max pairwise distance went from "
            f"{old_high_str} to {new_high_str} (Δ {gap_delta_str})"
        )

    if trigger.trigger_type == TriggerType.DRIFT:
        model_ver = ev.get("model_version_returned", "??")
        proc_dist = ev.get("procrustes_distance", "??")
        date_pair = ev.get("date_pair", ["??", "??"])
        d0 = date_pair[0] if len(date_pair) > 0 else "??"
        d1 = date_pair[1] if len(date_pair) > 1 else "??"
        proc_dist_str = (
            f"{proc_dist:.2f}" if isinstance(proc_dist, float) else str(proc_dist)
        )
        # Caveat is mandatory while the §7.3 lockout is engaged (§5.7 binding)
        return (
            f"{model_ver}: Procrustes distance {proc_dist_str} between {d0} and {d1}\n"
            "  ⚠ threshold 0.15 placeholder; lockout engaged"
        )

    if trigger.trigger_type == TriggerType.MONTHLY_ROUNDUP:
        month = ev.get("month", "??")
        # Binding phrasing per T5 CDA SME §5.7 / T1 §5.7 amendment
        return f"Monthly cross-domain categorical-structure roundup for {month}"

    # Fallback for unrecognized trigger type
    return f"{trigger.trigger_type} (no summary pattern defined)"


# ─────────────────────────────────────────────────────────────────────────────
# Full digest formatter
# ─────────────────────────────────────────────────────────────────────────────


def format_digest(
    triggers: list[SocialTrigger],
    *,
    queue_counts: dict[str, int],
    digest_date: datetime,
) -> tuple[str, str]:
    """Format a list of SocialTrigger objects as a plain-text email digest.

    Args:
        triggers:     Triggers detected since the last digest.  Must be
                      non-empty — the caller (cli.py) enforces the zero-trigger
                      silence invariant (per §11.9.4: no empty digests).
        queue_counts: Dict with keys "pending", "approved", "published",
                      "failed" and integer values.  The "published" value
                      carries both total and a current-period count; callers
                      may pass a formatted string value for that key if needed.
        digest_date:  The date to display in the subject and header.

    Returns:
        (subject, body) — both plain text.

    Subject: "LSB daily digest YYYY-MM-DD"

    The body raises ValueError if triggers is empty — use the caller-side
    zero-trigger check to avoid calling format_digest with an empty list.
    """
    if not triggers:
        raise ValueError(
            "format_digest called with empty trigger list. "
            "The CLI enforces zero-trigger silence — do not call format_digest "
            "when there are no new triggers."
        )

    date_str = digest_date.strftime("%Y-%m-%d")
    subject = f"LSB daily digest {date_str}"

    n = len(triggers)
    header = f"LSB daily digest {date_str}\n{'=' * 28}\n"

    lines: list[str] = [
        header,
        f"{n} trigger(s) detected since the last digest:\n",
    ]

    for i, trigger in enumerate(triggers, start=1):
        summary = format_trigger_summary(trigger)
        # Indent continuation lines (multi-line summaries like DRIFT)
        summary_indented = summary.replace("\n", "\n    ")
        lines.append(f"[{i}] {trigger.trigger_type.upper()}: {summary_indented}")

    lines.append("")
    lines.append("Queue status:")

    pending = queue_counts.get("pending", 0)
    approved = queue_counts.get("approved", 0)
    published = queue_counts.get("published", 0)
    failed = queue_counts.get("failed", 0)

    lines.append(f"  pending:    {pending} draft(s) awaiting your review")
    lines.append(f"  approved:   {approved} draft(s) awaiting publication")
    lines.append(f"  published:  {published}")
    lines.append(f"  failed:     {failed} (lifetime)")

    lines.append("")
    lines.append("To act on these triggers and drafts, run on the VPS:")
    lines.append("")
    lines.append("    python -m cdb_social.admin_console")
    lines.append("")
    lines.append("The console listens on 127.0.0.1:8000 (loopback only).")
    lines.append("")

    body = "\n".join(lines)
    return subject, body
