from __future__ import annotations

import json
from pathlib import Path

import yaml

pipeline = yaml.safe_load(Path("pipeline.yaml").read_text(encoding="utf-8"))
steps = pipeline.get("steps", [])
assert [step["name"] for step in steps] == ["test", "verify"]
assert all(isinstance(step.get("command"), str) and step["command"] for step in steps)
print(json.dumps({"status": "passed", "checks": ["pipeline parse", "test step", "verify step"]}))
