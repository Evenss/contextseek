"""Pipeline stage: run tau-bench tasks and write trajectory JSONL."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from eval.taubench import tau2_compat  # noqa: F401  # Python 3.13 compat
from eval.taubench.adapters.base import AgentAdapter, TaskResult


def _result_to_dict(result: TaskResult) -> dict[str, Any]:
    d = asdict(result)
    # Don't dump full message lists into JSONL by default (bloat)
    d.pop("messages", None)
    return d


def load_task_ids(
    domain: str,
    max_tasks: int | None = None,
    task_split: str = "base",
) -> list[int]:
    """Load task IDs for a tau-bench domain.

    Args:
        domain: Domain name (airline, retail, telecom, etc.)
        max_tasks: If set, return only the first N task IDs.
        task_split: Task split name (base, etc.)

    Returns:
        List of task index integers.
    """
    from tau2.run import get_tasks

    tasks = get_tasks(domain, task_split_name=task_split)
    task_ids = list(range(len(tasks)))
    if max_tasks and max_tasks > 0:
        return task_ids[:max_tasks]
    return task_ids


def run_stage(
    adapter: AgentAdapter,
    task_ids: list[int],
    output_path: Path,
    *,
    resume: bool = True,
    num_trials: int = 1,
) -> list[TaskResult]:
    """Run tasks through an adapter, appending JSONL results incrementally.

    Args:
        adapter: The agent adapter to use.
        task_ids: List of task IDs to run.
        output_path: Path to write JSONL results.
        resume: If True, skip tasks already present in the output file.
        num_trials: Number of independent trials per task.

    Returns:
        List of TaskResult objects.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Resume: build set of already-completed (task_id, trial) pairs
    done_pairs: set[tuple[int, int]] = set()
    if resume and output_path.exists():
        with open(output_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    done_pairs.add((rec["task_id"], rec.get("trial", 0)))

    results: list[TaskResult] = []
    total = len(task_ids) * num_trials

    with open(output_path, "a") as f:
        count = 0
        for trial in range(num_trials):
            for task_id in task_ids:
                count += 1
                if (task_id, trial) in done_pairs:
                    print(f"  [{count}/{total}] task={task_id} trial={trial} -- skipped")
                    continue

                print(f"  [{count}/{total}] task={task_id} trial={trial} ...", end=" ", flush=True)
                started_at = time.time()
                result = adapter.run_task(task_id, trial)
                elapsed = time.time() - started_at
                status = "PASS" if result.success else "FAIL"
                line = f"{status} (reward={result.reward:.2f}, {result.num_steps} steps, {elapsed:.1f}s)"
                if result.error:
                    line += f" — {result.error}"
                print(line)

                f.write(json.dumps(_result_to_dict(result), ensure_ascii=False) + "\n")
                f.flush()
                results.append(result)

    return results
