import pytest

from apiforge.context.scopes import validate_scope
from apiforge.contracts.base import ContractError


def test_context_scope_rejects_unknown_scope(tmp_path) -> None:
    with pytest.raises(ContractError) as error:
        validate_scope("task", root=tmp_path)
    assert error.value.code == "AF-CONTEXT-SCOPE-INVALID"
