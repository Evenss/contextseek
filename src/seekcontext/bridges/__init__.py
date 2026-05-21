"""Framework bridges (LangChain, DeepAgents) and discovery registry."""

from seekcontext.bridges.base import AdapterCapability
from seekcontext.bridges.base import AdapterContract
from seekcontext.bridges.base import AdapterSpec
from seekcontext.bridges.registry import get_adapter
from seekcontext.bridges.registry import list_adapter_specs
from seekcontext.bridges.registry import register_adapter
from seekcontext.bridges.registry import register_builtin_adapters

__all__ = [
    "AdapterCapability",
    "AdapterContract",
    "AdapterSpec",
    "get_adapter",
    "list_adapter_specs",
    "register_adapter",
    "register_builtin_adapters",
]
