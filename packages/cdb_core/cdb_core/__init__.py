"""cdb_core — shared types, IDs, and schemas for the Latent Structure Benchmark.

See ARCHITECTURE.md §3 for the core data model.
"""

from cdb_core.ids import run_id
from cdb_core.schemas import (
    ROMNEY_THRESHOLD_CLASSIC,
    ROMNEY_THRESHOLD_LSB,
    BootstrapEllipse,
    ConsensusType,
    CooccurrenceMatrix,
    DeclineInterview,
    Domain,
    DomainResult,
    FreeList,
    FreelistRecord,
    GroundingRef,
    InformantRecord,
    InterviewRecord,
    MantelPair,
    ModelRef,
    NolanIndexPair,
    PileSort,
    PileSortRecord,
    RawResponse,
    SutropCSI,
    WithinModelResult,
)

__all__ = [
    "run_id",
    "BootstrapEllipse",
    "ConsensusType",
    "CooccurrenceMatrix",
    "DeclineInterview",
    "Domain",
    "DomainResult",
    "FreeList",
    "FreelistRecord",
    "GroundingRef",
    "InformantRecord",
    "InterviewRecord",
    "MantelPair",
    "ModelRef",
    "NolanIndexPair",
    "PileSort",
    "PileSortRecord",
    "RawResponse",
    "ROMNEY_THRESHOLD_CLASSIC",
    "ROMNEY_THRESHOLD_LSB",
    "SutropCSI",
    "WithinModelResult",
]
