from pathlib import Path

from apiforge.adapters.analytical import build_analytical_ir, extract_opensearch, extract_redshift


def test_opensearch_extracts_search_and_pagination(tmp_path: Path) -> None:
    (tmp_path / "search.py").write_text(
        "from opensearchpy import OpenSearch\n"
        "client.search(index='orders', body={'query': {'match': {'status': 'open'}}, 'size': 20})\n",
        encoding="utf-8",
    )
    ir = build_analytical_ir(extract_opensearch(tmp_path), engine="opensearch")
    assert "orders" in ir.indexes_or_tables
    assert "search" in ir.operations
    assert "pagination" in ir.query_signals


def test_redshift_extracts_aggregation_and_partition_signal(tmp_path: Path) -> None:
    (tmp_path / "query.sql").write_text(
        "SELECT customer_id, count(*) FROM orders GROUP BY customer_id;\n"
        "-- distkey customer_id sortkey created_at\n",
        encoding="utf-8",
    )
    ir = build_analytical_ir(extract_redshift(tmp_path), engine="redshift")
    assert "aggregate" in ir.operations
    assert "partition" in ir.query_signals
