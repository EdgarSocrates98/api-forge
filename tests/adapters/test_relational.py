from pathlib import Path

from apiforge.adapters.relational import (
    extract_mysql,
    extract_postgres,
    extract_rds_access,
)


def _write_project(tmp_path: Path) -> Path:
    (tmp_path / "app.py").write_text(
        "import psycopg\n"
        "pool = psycopg.ConnectionPool()\n"
        'rows = pool.execute("SELECT id FROM orders WHERE tenant_id = %s LIMIT 20")\n'
        'pool.execute("UPDATE orders SET status = %s WHERE id = %s")\n',
        encoding="utf-8",
    )
    (tmp_path / "mysql.sql").write_text(
        "SELECT id FROM users LIMIT 10;\n",
        encoding="utf-8",
    )
    return tmp_path


def test_postgres_extracts_queries_pool_and_pagination(tmp_path: Path) -> None:
    inventory = extract_postgres(_write_project(tmp_path))
    queries = [fact for fact in inventory.facts if fact.kind == "data.relational.query"]
    assert any(fact.measures["operation"] == "select" for fact in queries)
    assert any(fact.measures["paginated"] is True for fact in queries)
    assert any(fact.kind == "data.relational.pool" for fact in inventory.facts)


def test_mysql_extracts_sql_files_without_driver_import(tmp_path: Path) -> None:
    inventory = extract_mysql(_write_project(tmp_path))
    assert any(fact.measures["database"] == "mysql" for fact in inventory.facts)


def test_rds_boundary_combines_supported_relational_drivers(tmp_path: Path) -> None:
    inventory = extract_rds_access(_write_project(tmp_path))
    databases = {fact.measures["database"] for fact in inventory.facts}
    assert databases == {"mysql", "postgres"}
