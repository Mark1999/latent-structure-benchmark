"""CDA protocol as code — the three-step pipeline.

See ARCHITECTURE.md §4.1.1.
"""

from cdb_collect.protocol.free_list import parse_free_list, run_free_list

__all__ = ["parse_free_list", "run_free_list"]
