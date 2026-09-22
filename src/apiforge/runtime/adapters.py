"""Model adapter boundary and deterministic fake provider."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from apiforge.contracts.base import ContractError


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    invocation_id: str
    agent: str
    capability: str
    prompt: str
    input_refs: tuple[str, ...] = ()
    tool_names: tuple[str, ...] = ()
    output_contract: str


class AgentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    output: Mapping[str, object]
    adapter: str
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    duration_ms: int | None = None
    tool_calls: tuple[str, ...] = ()


class ModelAdapter(Protocol):
    name: str

    async def invoke(self, request: AgentRequest) -> AgentResponse: ...


class FakeModelAdapter:
    """Deterministic adapter used by local CI and replay tests."""

    name = "fake"

    def __init__(self, responses: Mapping[str, Mapping[str, object]] | None = None) -> None:
        self.responses = dict(responses or {})
        self.calls: list[AgentRequest] = []

    async def invoke(self, request: AgentRequest) -> AgentResponse:
        self.calls.append(request)
        await asyncio.sleep(0)
        response = self.responses.get(request.capability)
        if response is None:
            response = {
                "facts": [f"fact:fake:{request.capability}"],
                "assumptions": [],
                "risks": [],
                "unresolved": [],
                "recommendation": f"review {request.capability}",
                "confidence": 0.85,
            }
        if response.get("__error__"):
            raise ContractError("AF-RUNTIME-ADAPTER", str(response["__error__"]))
        return AgentResponse(
            output=dict(response),
            adapter=self.name,
            model="fake-v1",
            input_tokens=len(request.prompt.split()),
            output_tokens=len(str(response).split()),
            duration_ms=0,
        )
