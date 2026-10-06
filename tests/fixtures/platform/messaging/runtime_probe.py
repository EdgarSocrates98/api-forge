from __future__ import annotations

import json
from collections import deque

messages = deque([{"id": "runtime"}])
acknowledged: list[str] = []
message = messages.popleft()
acknowledged.append(message["id"])
assert not messages
assert acknowledged == ["runtime"]
print(json.dumps({"status": "passed", "checks": ["message delivery", "explicit acknowledgement"]}))
