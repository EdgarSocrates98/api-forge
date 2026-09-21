# ADR-006: tree-sitter for language adapters

## Status

Accepted — 2026-09-21.

## Context

Java/Spring Boot and Go/Chi route extraction must be static, offline, and
must not require the target project's toolchain. Options: a tree-sitter
Python binding with per-language grammars, or native parsers invoked as
subprocesses (`javac`-based tooling, `go/parser` via a helper binary).

## Decision

Adopt **tree-sitter**. One mechanism serves every current and future
language adapter; extraction needs no JDK/Maven/Gradle/Go toolchain and never
executes project code — the same reason `ast.parse` anchors the FastAPI
adapter. Grammars resolve by pinned wheels (`tree-sitter`, `tree-sitter-java`,
later `tree-sitter-go`).

## Consequences

- Native wheel dependency — the first compiled dependency in the platform;
  pinned versions at least 7 days old.
- The AST is less typed than a language-native one: annotation arguments are
  matched structurally, and anything not a literal resolves to `unresolved`
  diagnostics, never inference.
- `apiforge.adapters.spring` is the only module allowed to import
  `tree_sitter`; the release gate enforces the boundary.
- The adapter emits the shared `CodeInventory` contract, so the judge, diff,
  sandbox and case layers remain language-agnostic.
