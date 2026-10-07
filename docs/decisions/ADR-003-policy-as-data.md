# ADR-003: policy as data

## Status

Accepted — 2026-09-21.

## Context

An agentic platform must refuse dangerous actions deterministically. If the
allow/deny logic lived in code scattered across commands, every new verb would
need a code change to be governed, and audits would require reading source.

## Decision

The autonomy policy is a closed-schema YAML document (`apiforge.policy`
package data by default) evaluated by the pure function `decide`. Six classes
(`read_only` … `irreversible`), deny rules evaluated first-match, gate
requirements satisfied only by caller-supplied `detail` fields, ambiguity
denied.

## Consequences

- New verbs are governed by adding data, not code.
- The receipt pins `policy_sha256`, so a release proves which policy decided.
- Ambiguity is a refusal, not an inference — an undeclared class denies.
- Gates can never be satisfied by the engine itself; they name the fields the
  operator must supply.
