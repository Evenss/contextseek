"""Registry for bridge discovery by framework and capability."""

from __future__ import annotations

from typing import cast

from seekcontext.bridges.base import AdapterCapability
from seekcontext.bridges.base import AdapterContract
from seekcontext.bridges.base import AdapterSpec

_REGISTRY: dict[tuple[str, AdapterCapability], type[AdapterContract]] = {}
_SPEC_INDEX: dict[str, AdapterSpec] = {}


def register_adapter(adapter_cls: type[AdapterContract]) -> None:
    """Register one adapter class for all declared capabilities."""
    spec = adapter_cls.spec()
    _SPEC_INDEX[spec.name] = spec
    for capability in spec.capabilities:
        _REGISTRY[(spec.framework, capability)] = adapter_cls


def get_adapter(
    framework: str, capability: AdapterCapability
) -> type[AdapterContract] | None:
    """Lookup adapter class by framework and capability."""
    return _REGISTRY.get((framework, capability))


def list_adapter_specs(*, framework: str | None = None) -> list[AdapterSpec]:
    """List unique adapter specs, optionally filtered by framework."""
    specs = list(_SPEC_INDEX.values())
    if framework is None:
        return sorted(specs, key=lambda item: item.name)
    return sorted(
        [item for item in specs if item.framework == framework],
        key=lambda item: item.name,
    )


def register_builtin_adapters() -> None:
    """Register built-in adapters shipped in this package."""
    from seekcontext.bridges.deepagents.context_store import ContextStore
    from seekcontext.bridges.deepagents.trace_sink import TraceSink
    from seekcontext.bridges.langchain.memory import SeekContextMemory
    from seekcontext.bridges.langchain.retriever import SeekContextRetriever

    for adapter_cls in (SeekContextRetriever, SeekContextMemory, ContextStore, TraceSink):
        register_adapter(cast(type[AdapterContract], adapter_cls))
