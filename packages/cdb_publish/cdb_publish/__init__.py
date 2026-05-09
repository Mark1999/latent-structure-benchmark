"""cdb_publish -- static JSON build layer for the LSB dashboard.

Reads analysis results and writes precomputed JSON files to
apps/dashboard/public/data/. See ARCHITECTURE.md §4.4.
"""

from cdb_publish.build import build
from cdb_publish.schemas.manifest import Manifest

__all__ = ["build", "Manifest"]
