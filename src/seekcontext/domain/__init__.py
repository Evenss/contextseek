"""Domain models for SeekContext — unified ContextItem model."""

from seekcontext.domain.conflicts import (
    ConflictCheckResult,
    ConflictType,
    WriteConflict,
    detect_conflicts,
)
from seekcontext.domain.context_item import ContextItem
from seekcontext.domain.levels import ContentLevel
from seekcontext.domain.evidence_chain import (
    ChainEdge,
    ChainNode,
    ConflictReport,
    EvidenceChain,
    compute_chain_confidence,
    compute_evidence_chain,
)
from seekcontext.domain.inference import build_provenance, infer_confidence, infer_stability, infer_stage
from seekcontext.domain.invalidation import DegradedItem, InvalidationResult, propagate_invalidation
from seekcontext.domain.links import Link, LinkType
from seekcontext.domain.provenance import Provenance, SourceType
from seekcontext.domain.results import (
    CompactReport,
    EvolutionReport,
    ResponseMeta,
    RetrieveResponse,
    SearchHit,
)
from seekcontext.domain.serialization import deserialize_context_item, serialize_context_item
from seekcontext.domain.stages import STAGE_CONFIDENCE, STAGE_DEFAULT_STABILITY, Stability, Stage
from seekcontext.domain.tools import ToolSpec, default_tool_specs

__all__ = [
    "ChainEdge",
    "ChainNode",
    "CompactReport",
    "ConflictCheckResult",
    "ConflictReport",
    "ConflictType",
    "ContentLevel",
    "ContextItem",
    "DegradedItem",
    "EvolutionReport",
    "EvidenceChain",
    "InvalidationResult",
    "Link",
    "LinkType",
    "Provenance",
    "ResponseMeta",
    "RetrieveResponse",
    "SearchHit",
    "SourceType",
    "Stability",
    "Stage",
    "STAGE_CONFIDENCE",
    "STAGE_DEFAULT_STABILITY",
    "ToolSpec",
    "WriteConflict",
    "default_tool_specs",
    "build_provenance",
    "compute_chain_confidence",
    "compute_evidence_chain",
    "deserialize_context_item",
    "detect_conflicts",
    "infer_confidence",
    "infer_stability",
    "infer_stage",
    "propagate_invalidation",
    "serialize_context_item",
]
