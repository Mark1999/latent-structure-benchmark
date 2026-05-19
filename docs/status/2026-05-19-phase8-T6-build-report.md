# Phase 8 T6 — Open Data Bundle Build Report

**Date:** 2026-05-19
**Builder:** scripts/build_open_bundle.py (T6.1)
**Operator:** Coder agent (Phase 8 T6)
**Input data:** data/raw/informants.jsonl, data/raw/failures.jsonl, data/raw/decline_interviews.jsonl

---

## 1. Record counts (from lsb.sqlite)

| Table | Count |
|---|---|
| `informants` | 1,291 |
| `freelist_items` | 248,050 |
| `pilesort_cells` | 48,738,503 |
| `interview_labels` | 26,161 |
| `decline_interviews` | 27 |

Additional raw files included (not in SQLite):
- `failures.jsonl`: 36 lines (raw dict entries, not a pydantic table)

---

## 2. Tarball summary

| Field | Value |
|---|---|
| Tarball name | `lsb_open_bundle_v1.tar.gz` |
| Tarball size | 1,550,226,039 bytes (~1.44 GiB) |
| Tarball SHA256 | `7064b325a25f90d2555138e7d944b129e78cbc7e18eace663b058166a6cd5983` |
| SQLite size (uncompressed) | 8,833,261,568 bytes (~8.22 GiB) |
| Build tool | `scripts/build_open_bundle.py --output-dir /tmp/lsb_bundle_out` |

---

## 3. MANIFEST.txt (embedded in tarball)

```
85099dbcf900a198da3020fc01a598755541cfa367ae756db739160436572d2d	120551	lsb_open_bundle_v1/DATA_DICTIONARY.md
643ff11cfae118f1f5f0e90b4611079b6ee10eda33de77f537515d8af0629392	1908	lsb_open_bundle_v1/LICENSE-OPENBUNDLE
7ba0decf8f9a88ffe585f11feb80568755785dc50a89b6735c2d8444b4e83d86	2803	lsb_open_bundle_v1/README.md
8137e649e0e37ca94711dc92c902c243cc9852fd50be0fcc3fd00c1d1ddb97e1	17171	lsb_open_bundle_v1/build_db.py
c02a57f44ae45e9877599c7d438728d4fc73ca05cd73ab4e7d34f6292cb2ba23	107501	lsb_open_bundle_v1/decline_interviews.jsonl
ca9eb689220337288bf02b4f3f9782c74c3dcd993a85d59608af3fbfa3275d2f	129	lsb_open_bundle_v1/domains/v1/family.yaml
9c3585cda1658f135ac1ab45874692c1b782f40a3ec659d2847fe7fc1523b9d0	95	lsb_open_bundle_v1/domains/v1/food.yaml
94d67272856a5e1178b136dc68e93b17a977cd52799a1773088dbbd682b2c7c9	128	lsb_open_bundle_v1/domains/v1/holidays.yaml
8db9267d4257a0e045bced647631db69837f931ae8ef7ba23842e4c9735c3106	257508	lsb_open_bundle_v1/failures.jsonl
60e43c28a3ed55a0806072716bd57040d754c43b98a2cc3e6fdf1303e6e2dff7	166281794	lsb_open_bundle_v1/informants.jsonl
3fbc94bfb031c73bc0864322872dce57498515c1247a745fcb72dd09afabd01a	8833261568	lsb_open_bundle_v1/lsb.sqlite
15c8a6047bc532b67f2e6348136f157c2eddaaa37be18f0fa30dec666085aa9f	249	lsb_open_bundle_v1/prompts/v1/free_list.md
222c40cfbe71192013a0961b70a7a5c6bf74078ca7f341a10bd495d5c534c352	276	lsb_open_bundle_v1/prompts/v1/pile_interview.md
78619f2690e6f10707dfe318ef94b0885d040986d94fa31b16d711413171bf3f	390	lsb_open_bundle_v1/prompts/v1/pile_sort.md
```

---

## 4. Verify result

```
$ uv run python scripts/build_open_bundle.py --verify /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz

Verifying /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz …
OK    lsb_open_bundle_v1/DATA_DICTIONARY.md
OK    lsb_open_bundle_v1/LICENSE-OPENBUNDLE
OK    lsb_open_bundle_v1/README.md
OK    lsb_open_bundle_v1/build_db.py
OK    lsb_open_bundle_v1/decline_interviews.jsonl
OK    lsb_open_bundle_v1/domains/v1/family.yaml
OK    lsb_open_bundle_v1/domains/v1/food.yaml
OK    lsb_open_bundle_v1/domains/v1/holidays.yaml
OK    lsb_open_bundle_v1/failures.jsonl
OK    lsb_open_bundle_v1/informants.jsonl
OK    lsb_open_bundle_v1/lsb.sqlite
OK    lsb_open_bundle_v1/prompts/v1/free_list.md
OK    lsb_open_bundle_v1/prompts/v1/pile_interview.md
OK    lsb_open_bundle_v1/prompts/v1/pile_sort.md

VERIFY PASS: all 14 manifest entries verified.
```

---

## 5. B2 Upload Runbook (T6.5)

Mark runs this to publish the bundle to Backblaze B2. The builder does not upload — upload is a manual step.

### Prerequisites

Credentials are in `.env` and 1Password per `HOSTING_AND_DEV_OPS.md` §8:
- `B2_KEY_ID` — Backblaze B2 application key ID
- `B2_APPLICATION_KEY` — Backblaze B2 application key (scoped to `lsb-open-data` bucket)

The B2 CLI must be installed: `pip install b2` or check `b2 --version`.

Target bucket: `lsb-open-data` (see `HOSTING_AND_DEV_OPS.md` §7.1).

### Step 1 — Dry run (verify upload path)

```bash
# Substitute actual tarball path
b2 file upload \
  --no-progress \
  lsb-open-data \
  /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz \
  lsb_open_bundle_v1.tar.gz
```

Note: the B2 CLI does not have a separate `--dry-run` flag for uploads. Verify the bucket name and file name before uploading. Use `b2 ls lsb-open-data` to inspect current bucket contents first.

### Step 2 — Full upload

```bash
# Authenticate first (if not already done)
export B2_KEY_ID=$(grep B2_KEY_ID /opt/lsb-agent/.env | cut -d= -f2)
export B2_APPLICATION_KEY=$(grep B2_APPLICATION_KEY /opt/lsb-agent/.env | cut -d= -f2)

b2 account authorize "$B2_KEY_ID" "$B2_APPLICATION_KEY"

# Upload the tarball
b2 file upload \
  lsb-open-data \
  /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz \
  lsb_open_bundle_v1.tar.gz
```

After upload, verify with:

```bash
b2 ls lsb-open-data
```

### Step 3 — Confirm public URL

The bundle download URL depends on the B2 region of the account. Mark's account is in region **005** (confirmed 2026-05-19 via `b2 account authorize` response), so the URL is:

```
https://f005.backblazeb2.com/file/lsb-open-data/lsb_open_bundle_v1.tar.gz
```

This URL goes in the `DATA_DICTIONARY.md` §6 reproduce recipe and in the bundle README's citation block once the bucket is flipped to public (at M11 per the Path A reorder in `docs/status/2026-05-17-phase8-handoff-for-mark.md`).

### Notes

- The bucket was `allPrivate` at creation. Flip to public at M11 (the GitHub repo public flip).
- The expected SHA256 of the tarball is `7064b325a25f90d2555138e7d944b129e78cbc7e18eace663b058166a6cd5983`. Confirm locally with `sha256sum` before relying on the upload. B2's `file info` exposes `large_file_sha1` (not SHA256) for chunked uploads.
- The tarball is 1,550,226,039 bytes (~1.44 GiB). Upload completed 2026-05-19 (~12 seconds on Linode uplink at ~130 MB/s).

---

*End of build report.*
