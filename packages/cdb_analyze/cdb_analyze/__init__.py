"""cdb_analyze — analysis layer for the Latent Structure Benchmark.

Pure deterministic Python: sklearn, numpy, scipy, networkx. Transforms raw
collection data into MDS coordinates, similarity matrices, consensus scores,
bootstrap uncertainty, and drift metrics. See ARCHITECTURE.md §4.2.

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NO LLM CALLS PERMITTED IN THIS PACKAGE.
#
# LLMs are informants in cdb_collect, not analysts in cdb_analyze.
# The Reviewer agent must reject any PR that introduces an LLM call
# into this package. This includes: anthropic, openai, google.generativeai,
# huggingface_hub.InferenceClient, litellm, langchain, llama_index, or
# any other LLM client library.
#
# The single exception is the lede generator, which lives in cdb_publish
# (not cdb_analyze) precisely to keep this boundary visible.
#
# See ARCHITECTURE.md §1 commitment 6, §4.2 binding constraint.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
