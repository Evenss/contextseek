"""SeekContext storage backends (VFS, file, OceanBase, tiered)."""

from __future__ import annotations

from seekcontext.storage.file_backend import FileBackend
from seekcontext.storage.in_memory_backend import InMemoryBackend
from seekcontext.storage.protocol import SeekVFSAdapter
from seekcontext.storage.protocol import VectorSearchMixin
from seekcontext.storage.storage_adapter import SeekVFSStorageAdapter
from seekcontext.storage.tiered_adapter import TieredSeekVFSAdapter
from seekcontext.storage.vector_memory_adapter import VectorMemoryAdapter

__all__ = [
    "SeekVFSAdapter",
    "VectorSearchMixin",
    "InMemoryBackend",
    "FileBackend",
    "SeekVFSStorageAdapter",
    "TieredSeekVFSAdapter",
    "VectorMemoryAdapter",
    "OceanBaseBackend",
]


def __getattr__(name: str):
    """Load optional backends only when explicitly requested."""
    if name == "OceanBaseBackend":
        from seekcontext.storage.ob_backend import OceanBaseBackend

        return OceanBaseBackend
    raise AttributeError(name)
