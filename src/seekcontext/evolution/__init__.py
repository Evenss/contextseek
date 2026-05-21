"""Evolution module — drives the Stage progression pipeline.

raw → extracted → knowledge → skill
Plus dreaming: consolidation + divergence for creative evolution.
"""

from seekcontext.evolution.engine import EvolutionEngine
from seekcontext.evolution.extractor import HeuristicExtractor, LLMExtractor
from seekcontext.evolution.merger import ConvergenceMerger
from seekcontext.evolution.distiller import SkillDistiller
from seekcontext.evolution.dreaming import (
    ConsolidationEngine,
    ConsolidationResult,
    DivergenceEngine,
    DivergenceResult,
    DreamEngine,
    DreamReport,
)
from seekcontext.evolution.rules import EvolutionRule, DEFAULT_RULES

__all__ = [
    "ConsolidationEngine",
    "ConsolidationResult",
    "ConvergenceMerger",
    "DEFAULT_RULES",
    "DivergenceEngine",
    "DivergenceResult",
    "DreamEngine",
    "DreamReport",
    "EvolutionEngine",
    "EvolutionRule",
    "HeuristicExtractor",
    "LLMExtractor",
    "SkillDistiller",
]
