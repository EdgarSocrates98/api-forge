from __future__ import annotations

import json
import sqlite3
from pathlib import Path

connection = sqlite3.connect(":memory:")
connection.executescript(Path("schema.sql").read_text(encoding="utf-8"))
connection.execute("INSERT INTO orders VALUES (?, ?, ?)", ("runtime", "customer", "2026-01-01"))
row = connection.execute("SELECT order_id FROM orders WHERE order_id = ?", ("runtime",)).fetchone()
assert row == ("runtime",)
print(json.dumps({"status": "passed", "checks": ["SQLite schema", "bounded parameterized lookup"]}))
