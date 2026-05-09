"""Lede sentence patterns -- v1 (template-based, deterministic).

Versioned per CLAUDE.md §6 R7: prompt templates and lede templates are
both versioned so future LLM-based lede swaps (Phase 6) carry a new
version number. Reviewer rejects in-place edits; create lede_v2.py
for any future change.

Framing disciplines (binding per CDA SME plan-level verdict Q1--Q5 and
carry-forward notes B6/T8/T9/T14):

- Descriptive-locational frame only (Q3): uses position language
  ("organized around", "shows where each model sits", "located in a
  different region"). No convergence-to-truth language. No causal
  language. No introspective language.
- Schema-literal branch predicates (Q1): all ConsensusType values are
  the six schema literals. "NO_CONSENSUS" does not exist and must not
  appear anywhere.
- R1-b (low output concentration) surfaced in strong-consensus branch
  per Q5 binding.
- §1.5.4 forbidden vocabulary absent: no "believes", "thinks",
  "worldview", "the model understands", "the model recognizes",
  "the model interprets", "the model perceives", "the model
  comprehends", "the model identifies".
- T9 forbidden softer verbs absent: no "recognizes", "identifies",
  "interprets", "comprehends", "perceives" applied to models.
- T14 binding: no "publishable" or "publication" framing.
- US English throughout: "organized" not "organised".

Format placeholders use Python str.format_map():
  {n}          -- number of models on the cross-model map
  {domain}     -- domain slug (e.g. "family", "holidays")
  {s}          -- Smith's S consensus score, formatted to 2 decimals
  {lo}         -- lower bound of 95% CI, formatted to 2 decimals
  {hi}         -- upper bound of 95% CI, formatted to 2 decimals
  {n_low_oci}  -- count of R1-b models (OCI < threshold AND not
                 deterministic_output), used in *_with_low_oci patterns

See generate_lede() in cdb_publish/lede.py for the branch logic and
formatting.
"""

LEDE_VERSION = "v1"

# Keys map to pattern_name strings returned by _select_pattern().
# Each value is the format string for that pattern.
PATTERNS: dict[str, str] = {
    # ----------------------------------------------------------------
    # STRONG_CONSENSUS -- all models R1-a (typical concentration)
    # ----------------------------------------------------------------
    "strong_consensus_homogeneous": (
        "Across {n} frontier models, {domain} vocabulary is organized around"
        " a single shared categorical structure"
        " (Smith's S = {s}, 95% CI [{lo}, {hi}])."
        " The map below shows where each model sits relative to that"
        " consensus -- and which models diverge from it."
    ),

    # ----------------------------------------------------------------
    # STRONG_CONSENSUS -- minority of models are R1-b (low OCI)
    # ----------------------------------------------------------------
    "strong_consensus_with_low_oci": (
        "Across {n} frontier models, {domain} vocabulary is organized around"
        " a shared categorical structure"
        " (Smith's S = {s}, 95% CI [{lo}, {hi}])."
        " {n_low_oci} of these {n} models produced low output concentration"
        " on this domain -- their position on the map is shown without a"
        " confidence ellipse, signalling that the runs did not converge on a"
        " single sort."
    ),

    # ----------------------------------------------------------------
    # STRONG_CONSENSUS -- majority (>50%) of models are R1-b
    # ----------------------------------------------------------------
    "strong_consensus_majority_low_oci": (
        "Across {n} frontier models, {domain} vocabulary is organized around"
        " a shared categorical structure"
        " (Smith's S = {s}, 95% CI [{lo}, {hi}]),"
        " but a majority of these models produced low output concentration"
        " on this domain -- the consensus measurement may be dominated by"
        " a smaller group of high-concentration models. See the per-model"
        " OCI badges and the methodology page."
    ),

    # ----------------------------------------------------------------
    # WEAK_CONSENSUS
    # ----------------------------------------------------------------
    "weak_consensus": (
        "Across {n} frontier models, {domain} vocabulary shows partial"
        " categorical agreement"
        " (Smith's S = {s}, 95% CI [{lo}, {hi}])."
        " The map below shows the points of agreement and the specific"
        " divergences."
    ),

    # ----------------------------------------------------------------
    # SUBCULTURAL -- competing sub-structures, negative centrality present
    # ----------------------------------------------------------------
    "subcultural": (
        "Across {n} frontier models, {domain} vocabulary organizes into"
        " multiple distinct categorical sub-structures"
        " (Smith's S = {s}, 95% CI [{lo}, {hi}])."
        " One or more models show negative centrality, locating them in a"
        " different region of cognitive space than the majority."
    ),

    # ----------------------------------------------------------------
    # TURBULENT -- low ratio, no shared structure, centrality scores positive
    # ----------------------------------------------------------------
    "turbulent": (
        "Across {n} frontier models, {domain} vocabulary does not organize"
        " around a shared categorical structure"
        " (Smith's S = {s}, 95% CI [{lo}, {hi}])."
        " The map below shows how each model's output distribution"
        " organizes the same terms differently."
    ),

    # ----------------------------------------------------------------
    # CONTESTED -- low ratio with negative centrality
    # ----------------------------------------------------------------
    "contested": (
        "Across {n} frontier models, {domain} vocabulary shows active"
        " categorical divergence"
        " (Smith's S = {s}, 95% CI [{lo}, {hi}])"
        " with negative centrality on one or more models, indicating that"
        " some models organize the terms in a way that diverges from the rest."
    ),

    # ----------------------------------------------------------------
    # ALL-DETERMINISTIC edge case -- verbatim per DESIGN_SYSTEM.md §3.3.5 item 6.
    # Any edit to this string requires creating lede_v2.py (per CLAUDE.md §6 R7).
    # ----------------------------------------------------------------
    "all_deterministic": (
        "All selected models produced deterministic output on this domain"
        " — the same categorical structure on every run."
        " Cross-model comparison remains valid; see below."
        " Methodology page explains what deterministic output signals about"
        " model architecture."
    ),
}
