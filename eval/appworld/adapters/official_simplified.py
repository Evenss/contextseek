"""Adapter for AppWorld's official simplified CLI agent."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from .base import AgentAdapter, RunResult, TrajectoryStep


class OfficialSimplifiedAdapter(AgentAdapter):
    """Run the official AppWorld simplified agent through its CLI."""

    @property
    def name(self) -> str:
        return "official_simplified"

    def configure(self, config: dict[str, Any]) -> None:
        self._conda_env = config.get("conda_env", "appworld-paper")
        self._max_steps = config.get("max_steps", 25)
        self._output_root = config.get("output_dir", "./output")
        self._data_dir = os.path.expanduser(config.get("data_dir", ""))

    def run_task(self, task_id: str, **kwargs: Any) -> RunResult:
        started_at = time.time()
        run_dir = Path(self._output_root) / self.name / task_id
        run_dir.mkdir(parents=True, exist_ok=True)
        try:
            cmd = [
                "conda",
                "run",
                "-n",
                self._conda_env,
                "--no-banner",
                "appworld",
                "run",
                "--task_id",
                task_id,
                "--max_steps",
                str(self._max_steps),
                "--output_dir",
                str(run_dir),
            ]
            if self._data_dir:
                cmd.extend(["--data_dir", self._data_dir])
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            success = False
            eval_path = run_dir / "evaluation.json"
            if eval_path.exists():
                with open(eval_path) as f:
                    success = bool(json.load(f).get("success", False))

            steps: list[TrajectoryStep] = []
            traj_path = run_dir / "trajectory.jsonl"
            if traj_path.exists():
                with open(traj_path) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        record = json.loads(line)
                        steps.append(
                            TrajectoryStep(
                                thought=record.get("thought", ""),
                                code=record.get("code"),
                                observation=record.get("observation"),
                            )
                        )

            return RunResult(
                task_id=task_id,
                agent=self.name,
                success=success,
                num_steps=len(steps),
                duration_ms=int((time.time() - started_at) * 1000),
                steps=steps,
                metadata={"llm_model": "official_cli"},
                error=None if proc.returncode == 0 else (proc.stderr or "")[:500],
            )
        except Exception as exc:
            return RunResult(
                task_id=task_id,
                agent=self.name,
                success=False,
                num_steps=0,
                duration_ms=int((time.time() - started_at) * 1000),
                metadata={"llm_model": "official_cli"},
                error=str(exc),
            )
