"""Small chat-completion wrapper used by the AppWorld ReAct agent."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlparse, urlunparse


def normalize_openai_compatible_base_url(url: str) -> str:
    """If ``base_url`` is only ``scheme://host[:port]`` (or trailing ``/``), append ``/v1``.

    Many gateways serve an HTML SPA at the site root; the OpenAI Python client expects
    ``base_url`` to be the API root (typically ending with ``/v1``) so requests go to
    ``.../v1/chat/completions``.
    """
    u = url.strip().rstrip("/")
    parsed = urlparse(u)
    path = parsed.path or ""
    if path in ("", "/"):
        return urlunparse((parsed.scheme, parsed.netloc, "/v1", "", "", ""))
    return u


def _parse_openai_chat_completion(response: Any) -> tuple[str, int, int]:
    """Extract (text, prompt_tokens, completion_tokens) from chat.completions.create result.

    Some OpenAI-compatible gateways return a JSON string or plain dict instead of the
    SDK ``ChatCompletion`` model; misconfigured URLs may return non-JSON bodies (handled
    with a clear error).
    """
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            snippet = response[:400].replace("\n", " ")
            hint = ""
            low = response.lstrip().lower()
            if low.startswith("<!doctype") or low.startswith("<html"):
                hint = (
                    " Response looks like HTML (often the gateway web UI). "
                    "Use a base URL that points at the OpenAI API root, usually ending with ``/v1``."
                )
            raise TypeError(
                "LLM gateway returned a non-JSON string for chat completions. "
                "Check ``agent.llm_base_url`` (often must end with ``/v1``), the route "
                "``POST .../chat/completions``, and that the server is OpenAI-compatible."
                + hint
                + f" Body prefix: {snippet!r}"
            ) from None

    if not isinstance(response, dict) and hasattr(response, "model_dump"):
        response = response.model_dump()

    if isinstance(response, dict):
        choices = response.get("choices") or []
        if not choices:
            raise ValueError(
                f"No choices in chat completion payload; keys={list(response.keys())!r}"
            )
        message = choices[0].get("message") or {}
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                pieces: list[str] = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        pieces.append(str(part.get("text", "")))
                    elif isinstance(part, dict) and "text" in part:
                        pieces.append(str(part.get("text", "")))
                text = "".join(pieces)
            elif content is None:
                text = ""
            else:
                text = str(content)
        else:
            text = str(message)
        usage = response.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)
        return text, prompt_tokens, completion_tokens

    if hasattr(response, "choices") and response.choices:
        choice = response.choices[0]
        msg = choice.message
        text = (msg.content or "") if msg is not None else ""
        usage = getattr(response, "usage", None)
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
        return text, prompt_tokens, completion_tokens

    raise TypeError(f"Unexpected chat completion type {type(response)!r}")


class LLMClient:
    """Uniform interface for OpenAI-compatible, Azure OpenAI, and Anthropic SDKs."""

    def __init__(self, provider: str, **kwargs: Any) -> None:
        self.provider = provider
        if provider == "anthropic":
            import anthropic

            self._client = anthropic.Anthropic(
                api_key=kwargs["api_key"],
                base_url=kwargs.get("base_url"),
            )
        elif provider == "azure":
            from openai import AzureOpenAI

            self._client = AzureOpenAI(
                api_key=kwargs["api_key"],
                azure_endpoint=kwargs["azure_endpoint"],
                api_version=kwargs.get("azure_api_version", "2025-01-01-preview"),
            )
        else:
            from openai import OpenAI

            client_kwargs: dict[str, Any] = {"api_key": kwargs["api_key"]}
            raw_base = kwargs.get("base_url")
            if raw_base:
                client_kwargs["base_url"] = normalize_openai_compatible_base_url(raw_base)
            self._client = OpenAI(**client_kwargs)

    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
    ) -> tuple[str, int, int]:
        """Return ``(text, prompt_tokens, completion_tokens)``."""
        if self.provider == "anthropic":
            system = ""
            chat_messages: list[dict[str, str]] = []
            for message in messages:
                if message["role"] == "system":
                    system = message["content"]
                else:
                    chat_messages.append(message)
            response = self._client.messages.create(
                model=model,
                max_tokens=4096,
                system=system,
                messages=chat_messages,
                temperature=temperature,
            )
            text = response.content[0].text if response.content else ""
            prompt_tokens = response.usage.input_tokens if response.usage else 0
            completion_tokens = response.usage.output_tokens if response.usage else 0
            return text, prompt_tokens, completion_tokens

        response = self._client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
        )
        return _parse_openai_chat_completion(response)


def detect_provider(
    *,
    llm_provider: str | None,
    llm_base_url: str | None,
    azure_endpoint: str | None,
) -> str:
    """Infer the SDK provider when config does not set one explicitly."""
    if llm_provider:
        return llm_provider
    if azure_endpoint:
        return "azure"
    if llm_base_url and "anthropic" in llm_base_url:
        return "anthropic"
    return "openai"
