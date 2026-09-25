import pytest

from apiforge.context.scopes import validate_scope
from apiforge.contracts.base import ContractError


def test_target_scope_requires_target(tmp_path):
    with pytest.raises(ContractError):
        validate_scope("target", root=tmp_path)
