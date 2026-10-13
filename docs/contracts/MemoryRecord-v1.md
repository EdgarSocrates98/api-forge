# MemoryRecord/v1

`MemoryRecord/v1` is an immutable, provenance-bound data item. `scope` keeps
working/case/task memory separate from episodic, institutional and semantic
memory. `origin`, `trust_level`, `taint`, `provenance`, `evidence_refs` and the
environment fingerprint prevent data from silently becoming instruction or
being reused in the wrong runtime.

`runtime_requirements`, `runtime_constraints` and `policy_version` bind record
applicability to explicit runtime evidence. `freshness=stale` remains stale
even when `expires_at` absent. `MemoryTrust.taint` remains data-only metadata;
tainted rows stay outside default context admission.

Persistence is a separate operation. Institutional and semantic records need
evidence; model-generated content is never promoted automatically. Invalidation
appends an event and leaves the original bytes available for audit.

Canonical schema: `apiforge contract show MemoryRecord/v1`.
