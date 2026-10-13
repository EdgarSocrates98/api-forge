# ExpertisePack/v1

`ExpertisePack/v1` describes validated local domain knowledge that a capability
may require. It is metadata, not a remote updater or a host synchronization
instruction.

| Field | Meaning |
|---|---|
| `pack_id` | Stable local pack identifier |
| `domain` | Knowledge domain represented by the pack |
| `pack_version` | Version observed by the local loader |
| `freshness` | `fresh`, `stale`, `unresolved` or `unknown` |
| `source_refs` | Read-only source/receipt references |
| `limitations` | Claims the pack cannot support |
| `evidence_level` | Declared evidence level for the metadata |

Routing compares required packs with locally available pack identifiers. A
missing pack returns `AF-CAPABILITY-ELIGIBILITY` with
`field=capability.expertise_packs`. Remote refresh, symlink installation and
automatic host-file overwrite remain deferred.
