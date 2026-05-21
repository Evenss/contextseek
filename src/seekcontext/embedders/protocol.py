"""Embedder type for seekcontext."""
from __future__ import annotations
from typing import Callable

Embedder = Callable[[str], list[float]]

__all__ = ["Embedder"]
