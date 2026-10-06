# DisclosurePolicy/v1

§41 the declared task-class → tool set mapping (`rules/tool_disclosure.yaml`
shape).

| Field | Meaning |
|---|---|
| `task_classes` | class name → declared tool names |
| `keywords` | class name → deterministic classifier keywords |

Invariant: a class must declare at least one tool — an empty class is a
contract violation.
