from pathlib import Path

from apiforge.migration.adapters.go import GoAdapter
from apiforge.migration.adapters.java import JavaAdapter
from apiforge.migration.adapters.python import PythonAdapter

ROOT = Path("tests/fixtures/migrations")


def test_java_adapter_discovers_maven_manifest() -> None:
    result = JavaAdapter().discover(ROOT / "java" / "spring-java11-to-21", "11", "21")
    assert "pom.xml" in result.files


def test_python_adapter_marks_python_two_as_reviewable_risk() -> None:
    result = PythonAdapter().discover(ROOT / "python" / "python2-to-3", "2", "3")
    assert any(f.rule_id == "AF-MIG-PY-001" and f.blocking for f in result.findings)


def test_go_adapter_discovers_module() -> None:
    result = GoAdapter().discover(ROOT / "go" / "go121-to-124", "1.21", "1.24")
    assert result.files == ("go.mod",)
