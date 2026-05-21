"""Abstract adapter interface for AppWorld evaluation agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrajectoryStep:
    """One ReAct step in an AppWorld task trajectory."""

    thought: str = ""
    code: str | None = None
    observation: str | None = None


@dataclass
class RunResult:
    """Standard output record for a single AppWorld task run."""

    task_id: str
    agent: str
    success: bool
    num_steps: int
    duration_ms: int = 0
    token_usage: dict[str, int] = field(default_factory=dict)
    steps: list[TrajectoryStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class AgentAdapter(ABC):
    """Uniform interface used by the AppWorld evaluation pipeline."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier used in trajectory and report file names."""
        ...

    @abstractmethod
    def configure(self, config: dict[str, Any]) -> None:
        """Configure the adapter from merged YAML config."""
        ...

    @abstractmethod
    def run_task(self, task_id: str, **kwargs: Any) -> RunResult:
        """Run one task and return a standardized result."""
        ...

    def run_dataset(self, task_ids: list[str], **kwargs: Any) -> list[RunResult]:
        """Run tasks sequentially by default."""
        return [self.run_task(task_id, **kwargs) for task_id in task_ids]
