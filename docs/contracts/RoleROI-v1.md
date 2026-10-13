# RoleROI/v1

`RoleROI/v1` rows come from `apiforge economy roi --root R`: did each extra
capability change anything compared with the primary artifact?

| Field | Meaning |
|---|---|
| `capability` | Non-primary capability |
| `runs` / `calls` | Runs where it produced an artifact and the calls it used |
| `facts_added` / `unresolved_added` | Evidence ids and unresolved items absent from the primary artifact |
| `outcome_changed` / `outcome_changed_rate` | Runs where its recommendation differed from the primary's |
