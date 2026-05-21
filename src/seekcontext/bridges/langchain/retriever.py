"""LangChain retriever adapter for SeekContext (unified ContextItem API)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from seekcontext.bridges.base import AdapterCapability
from seekcontext.bridges.base import AdapterSpec
from seekcontext.bridges.compat import BaseRetriever
from seekcontext.bridges.compat import CallbackManagerForRetrieverRun
from seekcontext.bridges.compat import ConfigDict
from seekcontext.bridges.compat import Document
from seekcontext.bridges.compat import LANGCHAIN_RETRIEVER_AVAILABLE

if TYPE_CHECKING:
    from seekcontext.client.seekcontext import SeekContext
    from seekcontext.domain import Stage


def _to_documents(
    *, client: "SeekContext", scope: str, query: str, k: int, stage: "Stage | None" = None
) -> list[Document]:
    """Convert SeekContext ranked hits to LangChain Documents."""
    response = client.retrieve(query, scope=scope, k=k)
    docs: list[Document] = []
    for hit in response:
        if stage is not None and hit.item.stage != stage:
            continue
        page_content = hit.item.summary or hit.item.content_text
        docs.append(
            Document(
                page_content=page_content,
                metadata={
                    "id": hit.item.id,
                    "score": hit.score,
                    "stage": hit.item.stage.value if hit.item.stage else None,
                    "stage_confidence": hit.stage_confidence,
                    "provenance_summary": hit.provenance_summary,
                    "scope": hit.item.scope,
                    "tags": list(hit.item.tags),
                    "recall_path": hit.recall_path,
                },
            )
        )
    return docs


_SPEC = AdapterSpec(
    name="seekcontext.langchain.retriever",
    framework="langchain",
    capabilities=(AdapterCapability.RETRIEVAL,),
    description="LangChain BaseRetriever adapter for SeekContext unified ContextItem API.",
    required_packages=("langchain-core",),
)


if LANGCHAIN_RETRIEVER_AVAILABLE:

    class SeekContextRetriever(BaseRetriever):
        """Retriever adapter aligned with `langchain_core.BaseRetriever`.

        Uses the new unified SeekContext client with scope-based access.
        """

        client: Any
        scope: str
        k: int = 20
        stage: Any = None  # Optional[Stage]

        model_config = ConfigDict(arbitrary_types_allowed=True)

        def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
        ) -> list[Document]:
            del run_manager
            return _to_documents(
                client=self.client, scope=self.scope, query=query, k=self.k, stage=self.stage
            )

        def get_relevant_documents(self, query: str) -> list[Document]:
            """Compatibility alias for legacy LangChain usage."""
            return self.invoke(query)

        @classmethod
        def spec(cls) -> AdapterSpec:
            return _SPEC

        @classmethod
        def validate_environment(cls) -> tuple[bool, str | None]:
            return True, None

        @classmethod
        def from_client(
            cls,
            client: "SeekContext",
            *,
            scope: str,
            k: int = 20,
            stage: "Stage | None" = None,
        ) -> "SeekContextRetriever":
            return cls(client=client, scope=scope, k=k, stage=stage)

else:

    @dataclass
    class SeekContextRetriever(BaseRetriever):  # type: ignore[no-redef]
        """Retriever adapter with fallback behavior."""

        client: Any
        scope: str
        k: int = 20
        stage: Any = None

        def get_relevant_documents(self, query: str) -> list[Document]:
            return _to_documents(
                client=self.client, scope=self.scope, query=query, k=self.k, stage=self.stage
            )

        @classmethod
        def spec(cls) -> AdapterSpec:
            return _SPEC

        @classmethod
        def validate_environment(cls) -> tuple[bool, str | None]:
            return False, "langchain-core is required for native retriever integration."

        @classmethod
        def from_client(
            cls,
            client: "SeekContext",
            *,
            scope: str,
            k: int = 20,
            stage: "Stage | None" = None,
        ) -> "SeekContextRetriever":
            return cls(client=client, scope=scope, k=k, stage=stage)
