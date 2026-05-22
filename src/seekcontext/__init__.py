"""Public exports for SeekContext SDK."""

from seekcontext._version import __version__

from seekcontext.client.seekcontext import SeekContext
from seekcontext.config.settings import SeekContextSettings
from seekcontext.domain.context_item import ContextItem
from seekcontext.domain.links import Link, LinkType
from seekcontext.domain.provenance import Provenance, SourceType
from seekcontext.domain.results import (
    CompactReport,
    EvolutionReport,
    ResponseMeta,
    RetrieveResponse,
    SearchHit,
)
from seekcontext.domain.stages import Stage, Stability
from seekcontext.domain.tools import ToolSpec, default_tool_specs
from seekcontext.scope import (
    ScopeBuilder,
    ScopeLintWarning,
    ScopeStats,
    ScopeTemplates,
    ScopeTree,
)

__all__ = [
    "__version__",
    "ContextItem",
    "CompactReport",
    "EvolutionReport",
    "Link",
    "LinkType",
    "Provenance",
    "ResponseMeta",
    "RetrieveResponse",
    "ScopeBuilder",
    "ScopeLintWarning",
    "ScopeStats",
    "ScopeTemplates",
    "ScopeTree",
    "SearchHit",
    "SeekContext",
    "SeekContextSettings",
    "SourceType",
    "Stage",
    "Stability",
    "ToolSpec",
    "default_tool_specs",
]
