"""Static check: no LLM client imports in cdb_analyze.

Walks packages/cdb_analyze/ and rejects any file containing an import
statement referencing LLM client libraries. Exits non-zero on detection.

This enforces ARCHITECTURE.md §1 commitment 6 and §4.2 binding constraint:
LLMs are informants in cdb_collect, not analysts in cdb_analyze.

See also PHASE_0_TASKS.md P0-T6.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

FORBIDDEN_MODULES = {
    "anthropic",
    "openai",
    "google.generativeai",
    "huggingface_hub.InferenceClient",
    "huggingface_hub",
    "litellm",
    "langchain",
    "langchain_core",
    "langchain_community",
    "langchain_anthropic",
    "langchain_openai",
    "llama_index",
}

ANALYZE_DIR = Path(__file__).resolve().parent.parent / "packages" / "cdb_analyze"


def check_file(filepath: Path) -> list[str]:
    """Check a single Python file for forbidden imports. Returns list of violations."""
    violations = []
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in FORBIDDEN_MODULES:
                    if alias.name == forbidden or alias.name.startswith(forbidden + "."):
                        violations.append(
                            f"{filepath}:{node.lineno}: "
                            f"forbidden import '{alias.name}' "
                            f"(LLM client libraries not permitted in cdb_analyze)"
                        )
        elif isinstance(node, ast.ImportFrom) and node.module:
            for forbidden in FORBIDDEN_MODULES:
                if node.module == forbidden or node.module.startswith(forbidden + "."):
                    violations.append(
                        f"{filepath}:{node.lineno}: "
                        f"forbidden 'from {node.module} import ...' "
                        f"(LLM client libraries not permitted in cdb_analyze)"
                    )
    return violations


def main(target_dir: Path | None = None) -> int:
    """Run the check. Returns 0 if clean, 1 if violations found."""
    search_dir = target_dir or ANALYZE_DIR

    if not search_dir.is_dir():
        print(f"Directory not found: {search_dir}")
        return 1

    all_violations: list[str] = []
    for pyfile in sorted(search_dir.rglob("*.py")):
        all_violations.extend(check_file(pyfile))

    if all_violations:
        print("ERROR: LLM client imports detected in cdb_analyze:\n")
        for v in all_violations:
            print(f"  {v}")
        print(
            "\nLLMs are informants in cdb_collect, not analysts in cdb_analyze."
            "\nSee ARCHITECTURE.md §1 commitment 6, §4.2 binding constraint."
        )
        return 1

    print(f"OK: no LLM client imports found in {search_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
