from pathlib import Path

import pytest

from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.adapters.fastapi.models import FastApiInventory
from apiforge.openapi.loader import load_openapi
from apiforge.openapi.models import OpenApiDocument

OPENAPI_FIXTURES = Path("tests/fixtures/openapi")
FLAT_PROJECT = Path("tests/fixtures/fastapi_flat")


@pytest.fixture
def openapi_document() -> OpenApiDocument:
    return load_openapi(OPENAPI_FIXTURES / "orders-v1.yaml")


@pytest.fixture
def fastapi_inventory() -> FastApiInventory:
    return extract_fastapi(FLAT_PROJECT)
