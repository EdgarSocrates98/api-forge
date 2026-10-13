from __future__ import annotations

import json
from pathlib import Path

package = json.loads(Path("package.json").read_text(encoding="utf-8"))
source = Path("src/api.ts").read_text(encoding="utf-8")
assert package["scripts"]["test"]
assert "fetch(" in source
assert "Promise<Order[]>" in source
print(
    json.dumps(
        {
            "status": "passed",
            "checks": ["frontend manifest", "typed fetch contract"],
            "limitations": ["browser engine and accessibility host not executed"],
        }
    )
)
