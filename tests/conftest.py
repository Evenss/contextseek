"""Shared pytest configuration."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "langchain: LangChain agent middleware stack (optional extra)",
    )
