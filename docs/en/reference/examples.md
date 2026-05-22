# Examples

All scripts live in [`examples/`](../../../examples/). Run them with `uv run python examples/<script>.py` unless noted otherwise.

---

## Script index

| Script | Purpose | Required extras |
|---|---|---|
| [`full_pipeline_file.py`](../../../examples/full_pipeline_file.py) | FileBackend end-to-end: add, retrieve, expand, RetrievalOrchestrator | *(none)* |
| [`full_pipeline_ob.py`](../../../examples/full_pipeline_ob.py) | OceanBase + LangChain embedder: hybrid vector + full-text recall | `oceanbase`, `langchain`, `openai` |
| [`langchain_pipeline.py`](../../../examples/langchain_pipeline.py) | `ContextSeekMemory` and `ContextSeekRetriever` bridge adapters | `langchain`, `openai` |
| [`research_agent_demo.py`](../../../examples/research_agent_demo.py) | Comprehensive demo: all core features, zero external deps | *(none)* |
| [`powermem_minimal.py`](../../../examples/powermem_minimal.py) | Minimal PowerMem → ContextSeek plug integration | *(none)* |
| [`powermem_plug_demo.py`](../../../examples/powermem_plug_demo.py) | Full `PowerMemPlug` walkthrough with mixed-source `retrieve()` | *(none — or `pip install powermem` for live mode)* |
| [`llm_full_pipeline_oceanbase.py`](../../../examples/llm_full_pipeline_oceanbase.py) | Real LLM calls with OceanBase: all `EVOLUTION_LLM_*` features end-to-end | `oceanbase`, `langchain`, `openai` |

---

## Feature coverage

| Feature | Example(s) |
|---|---|
| InMemory / File backend | `full_pipeline_file.py`, `research_agent_demo.py` |
| OceanBase + hybrid search | `full_pipeline_ob.py`, `llm_full_pipeline_oceanbase.py` |
| LangChain bridges | `langchain_pipeline.py` |
| DataPlugs (RAG, memory, trace) | `powermem_minimal.py`, `powermem_plug_demo.py` |
| Evolution (`compact`, `dream`, `feedback`) | `research_agent_demo.py`, `llm_full_pipeline_oceanbase.py` |
| Evidence chain + provenance | `research_agent_demo.py` |
| `skill_tools()` / `skill_context()` | `research_agent_demo.py` |
| Strategy routing + canary | `research_agent_demo.py` |
| LLM reranking + summarization | `llm_full_pipeline_oceanbase.py` |
| Trace export | `research_agent_demo.py` |

---

See [`examples/README.md`](../../../examples/README.md) for per-script run instructions and expected output.
