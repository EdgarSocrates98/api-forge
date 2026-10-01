from __future__ import annotations

import json
from pathlib import Path

import hcl2

with Path("main.tf").open(encoding="utf-8") as source:
    document = hcl2.load(source)
assert document.get("resource")
assert any("google_cloud_run_v2_service" in resource for resource in document["resource"])
print(
    json.dumps(
        {
            "status": "passed",
            "checks": ["Terraform HCL parse", "declared Cloud Run resource"],
            "limitations": ["no cloud apply or remote posture read"],
        }
    )
)
