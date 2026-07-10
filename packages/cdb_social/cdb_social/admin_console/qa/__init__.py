"""QA panel modules for the LSB ops console.

Three sub-modules:
- histogram: bucket run_record_checks failures by check number per model
- divergence: compare persisted qa_passed against recomputed check results
- dispatch_templates: copy-ready Markdown blocks pre-filled with numeric evidence

No LLM imports. Read-only over informants.jsonl. Rule 14 compliant.
Rule 15 compliant: no new statistical computation; runs existing checks.
"""
