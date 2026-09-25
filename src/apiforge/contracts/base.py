"""Shared base for canonical contracts: frozen, closed, versioned."""

from __future__ import annotations

import warnings
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# The wire contract intentionally keeps the public ``schema`` field. Pydantic
# warns because that name shadows its legacy ``BaseModel.schema`` helper; the
# narrow filter preserves the stable payload without hiding unrelated warnings.
warnings.filterwarnings(
    "ignore",
    message=r'^Field name "schema" in ".*" shadows an attribute in parent "VersionedContract"$',
    category=UserWarning,
)


class VersionedContract(BaseModel):
    """Closed immutable model carrying a contract version.

    ``version`` is a ``Literal`` — v2 lands as a sibling class, never as an
    in-place change, so old payloads keep validating against v1.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: Literal[1] = Field(default=1)


class ContractError(ValueError):
    """A refused contract operation; ``str()`` begins with the AF code."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")
