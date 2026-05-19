# Phase 8 T7 — HuggingFace Dataset Push Runbook

**Date:** 2026-05-19
**Task:** T7.3 — push the open data bundle card and tarball to HuggingFace Datasets
**Operator:** Mark

---

## 1. Prerequisites

Before starting, verify these are in place:

1. **`hf` CLI installed.** The entry point is `hf` (not `huggingface-cli`, which is the deprecated alias from huggingface_hub <1.0).

   ```bash
   hf --version
   ```

   Expected: `huggingface_hub/1.x.x ...` or similar. If not installed:

   ```bash
   pip install huggingface_hub
   ```

2. **Authenticated as `AILLM1999`.**

   ```bash
   hf auth login
   ```

   Paste your HuggingFace write-access token when prompted. Tokens are at `https://huggingface.co/settings/tokens`.

3. **HF dataset repo created.** The dataset slug should be `AILLM1999/latent-structure-benchmark` (substitute if you used a different slug during M7 prep). The slug is referred to as `<HF_DATASET_SLUG>` throughout this runbook.

4. **Tarball staged.** The tarball was built in T6.4 and is at:

   ```
   /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz
   ```

   Confirm it is still present:

   ```bash
   ls -lh /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz
   ```

   Expected size: approximately 1.44 GiB (1,550,226,039 bytes).

---

## 2. Push commands

All commands are copy-pasteable. Substitute `<HF_DATASET_SLUG>` with the actual slug (e.g., `AILLM1999/latent-structure-benchmark`).

### Step 1 — Upload the tarball

```bash
hf upload <HF_DATASET_SLUG> \
  /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz \
  lsb_open_bundle_v1.tar.gz \
  --repo-type=dataset
```

The three positional arguments are: `<repo-id>` `<local-path>` `<path-in-repo>`.

This upload will take several minutes depending on uplink speed (~1.44 GiB). The CLI shows a progress bar.

### Step 2 — Upload the dataset card as `README.md`

HuggingFace renders the file at the root of a repo named `README.md` as the dataset card. The card lives in the repo at `data/open_bundle/huggingface_dataset_card.md` — upload it as `README.md`:

```bash
hf upload <HF_DATASET_SLUG> \
  /opt/lsb-agent/data/open_bundle/huggingface_dataset_card.md \
  README.md \
  --repo-type=dataset
```

---

## 3. Verify post-push

1. Open `https://huggingface.co/datasets/<HF_DATASET_SLUG>` in a browser.

2. **Card renders.** The page should display the formatted card text. The sidebar on the right should show the parsed metadata: License: CC0 1.0, Language: English, Size: 1K<n<10K.

3. **Tarball appears in Files tab.** Click "Files and versions". `lsb_open_bundle_v1.tar.gz` should appear. Reported size should be approximately 1.44 GiB.

4. **SHA256 matches.** Confirm tarball integrity:

   ```bash
   sha256sum /tmp/lsb_bundle_out/lsb_open_bundle_v1.tar.gz
   ```

   Expected: `7064b325a25f90d2555138e7d944b129e78cbc7e18eace663b058166a6cd5983`

---

## 4. License field in HF UI

If the M7 prep step set the dataset repo's license to `cc-by-4.0` in the HuggingFace UI, update it:

1. Go to `https://huggingface.co/datasets/<HF_DATASET_SLUG>/settings`.
2. Under **License**, change to `CC0 1.0` (matches the `license: cc0-1.0` in the card YAML front matter and the `LICENSE-OPENBUNDLE` file in the tarball).
3. Save.

Note: once the card `README.md` is uploaded with `license: cc0-1.0` in the YAML front matter, HuggingFace parses this automatically and the sidebar shows the correct license. The Settings page is a fallback if the YAML parse fails.

---

## 5. Privacy

The dataset repo should remain **private** until M11 (the public flip milestone). Do not flip to public before M11.

At M11, flip visibility via:

1. `https://huggingface.co/datasets/<HF_DATASET_SLUG>/settings`
2. Under **Repository visibility**, change to **Public**.
3. Click **Make this dataset public**.

Perform this at the same moment as the GitHub repo public flip, as described in `docs/status/2026-05-17-phase8-handoff-for-mark.md`.

---

## 6. Post-T8 follow-up (after Zenodo DOI minted)

Once the Zenodo record is published (Phase 8 task T8), replace the `<TBD-T8-DOI>` placeholder in the citation block of `data/open_bundle/huggingface_dataset_card.md` with the real DOI. Then re-upload the card:

```bash
hf upload <HF_DATASET_SLUG> \
  /opt/lsb-agent/data/open_bundle/huggingface_dataset_card.md \
  README.md \
  --repo-type=dataset
```

The tarball does not need to be re-uploaded — only the card changes.

---

*End of runbook.*
