# out/social/ — Social Publishing Pipeline Layout

This directory tree is the runtime working area for the LSB social publishing
pipeline (`cdb_social`). It holds queued drafts, published-post records, and
detector state. Only this README is tracked in git; all subdirectories and
their contents are gitignored.

---

## Directory layout

```
out/social/
├── queue/
│   ├── pending/          # SocialDraft JSON files awaiting Mark's review
│   ├── approved/         # Drafts Mark approved; ready to publish
│   ├── published/
│   │   └── {YYYY-MM}/    # SocialPostRecord JSON files for published posts
│   └── failed/           # SocialPostRecord JSON files for publish failures
├── state/
│   ├── seen_models.json       # Bootstrap state for detect_new_model
│   ├── seen_domains.json      # Bootstrap state for detect_new_domain
│   ├── divergence_highs.json  # Bootstrap state for detect_divergence
│   ├── monthly_roundup.json   # Last-fired YYYY-MM for the monthly trigger
│   └── posted_dedupe_keys.json  # Trigger dedupe keys already posted
└── README.md  (this file — the only tracked entry under out/social/)
```

---

## Gitignore policy

The following paths are gitignored (only this README is tracked in git):

- `out/social/queue/` — all subdirectories and their contents
- `out/social/state/` — all state JSON files

This prevents draft text, publish tokens, and detector state from ever being
committed. Queue entries and state files are operational runtime artifacts;
they are operator-local and are not part of the open data bundle.

If you need to migrate state to a new host, copy the `state/` directory
manually alongside any un-reviewed drafts from `queue/pending/` and
`queue/approved/`.

---

## File naming conventions

| Location | File name | Schema |
|---|---|---|
| `queue/pending/{draft_id}.json` | SHA256[:16]-based draft ID | `SocialDraft` |
| `queue/approved/{draft_id}.json` | Same draft ID | `SocialDraft` |
| `queue/published/{YYYY-MM}/{draft_id}.json` | Same draft ID | `SocialPostRecord` |
| `queue/failed/{draft_id}.json` | Same draft ID | `SocialPostRecord` |
| `state/seen_models.json` | Fixed name | Per-domain dict of model lists |
| `state/seen_domains.json` | Fixed name | List of known domain slugs |
| `state/divergence_highs.json` | Fixed name | Per-domain max pairwise distance |
| `state/monthly_roundup.json` | Fixed name | `{"last_fired": "YYYY-MM"}` |
| `state/posted_dedupe_keys.json` | Fixed name | List of dedupe key strings |

Moves between queue states are atomic (`os.rename` within the same
filesystem). The review CLI (`scripts/social_review.py`) and the publisher
(`cdb_social.publisher`) are the only writers to the queue directories.

---

## Schema cross-reference

The canonical Pydantic type definitions for all JSON files under this tree
are in `packages/cdb_core/cdb_core/schemas.py`:

- `SocialTrigger` — the post-worthy event embedded inside every `SocialDraft`
- `SocialDraft` — the JSON shape in `queue/pending/` and `queue/approved/`
- `SocialPostRecord` — the JSON shape in `queue/published/` and `queue/failed/`
- `TriggerType`, `Platform`, `PublishStatus` — enums used in the above types

Full field-level documentation with units, allowed values, and the dedupe-key
construction rule is in `docs/DATA_DICTIONARY.md §13`.

The state JSON files (`state/*.json`) are plain Python dicts; their schemas
are documented in the `cdb_social.triggers` module (T2) and in
`docs/DATA_DICTIONARY.md §13.4`.
