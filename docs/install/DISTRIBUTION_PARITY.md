# Distribution parity — API Forge

Install-2.0 §8.5 parity matrix for `apiforge-af` (dist `apiforge-af`,
Hatchling). Three columns: **Checkout** (source tree / `pip install -e .`),
**Wheel local** (wheel built from this branch, installed into a clean venv,
run outside the checkout), **PyPI publicado** (latest released wheel —
`0.1.6`, fetched with `pip download --no-deps apiforge-af==0.1.6`; it
predates this branch's `forge.json`/`forge.agentic.json` packaging).

Legend: ✅ works · ⚠️ works with documented degradation · ❌ broken ·
— not applicable.

| Surface | Checkout | Wheel local | PyPI publicado (0.1.6) |
|---|---|---|---|
| CLI (`apiforge`, `apiforge-mcp`, `apiforge-tui`) | ✅ | ✅ console scripts present in clean venv (runtime deps resolved from the index); `install`, `knowledge list`, `rules lookup`, `install doctor`, `install verify`, `doctor`, `install repair`, `install uninstall` all run from a consumer dir | ✅ same entry points |
| Skills | ✅ | ✅ `.agents/skills` → `apiforge/host_assets/skills`; install renders host mirrors | ✅ present in published wheel |
| Agents | ✅ | ✅ `agents/` → `apiforge/host_assets/agents` (31 entries); `AGENT_PROTOCOL.md` bundled | ✅ present |
| MCP | ✅ | ✅ `install doctor` `mcp-config` PASS + `.mcp.json` written; `install verify` performs the real JSON-RPC handshake (mcp extra not installed in the bare venv — honest BLOCKED/refuse, never a traceback) | ✅ `apiforge-mcp` entry point exists |
| Knowledge | ✅ | ✅ `knowledge list` enumerates packaged `apiforge/_data/knowledge` packs under the wheel | ✅ `_data/knowledge` present |
| Rules | ✅ | ✅ `rules lookup AF-BREAK-001` returns the packaged rule | ✅ packaged rule catalog |
| Protocols | ✅ | ⚠️ `install` writes `AGENT_PROTOCOL.md`; `forge/context/v1` + `forge/context-registry/v1` produced and schema-valid — **but** `_context_manifest` still reads `_REPO_DIR/forge*.json` (= `site-packages/` under wheel), so `integrity.files` digests and agentic-derived fields stay empty until lf-0037's reader wiring lands; `apiforge/_data/forge*.json` are now packaged so only the reader remains | ⚠️ same degradation, and the published wheel lacks `_data/forge*.json` entirely |
| Evals | ✅ | ✅ `_data/evals` packaged (349 entries incl. fixtures at `_data/tests/fixtures`) | ✅ `_data/evals` present |
| Install | ✅ | ✅ `install --root <consumer> --yes` → `forge/InstallReceipt/v1` `status: completed`; `.apiforge/install/install-ledger.json` ledger + `.mcp.json` + host mirrors + `.forge/context/` written | ⚠️ applies, but capability manifest degraded (Protocols row) |
| Repair | ✅ | ✅ delete `.mcp.json` → `install repair --root` restores it | ⚠️ same path exists; not re-verified on published wheel |
| Uninstall | ✅ | ✅ `install uninstall --root` removes managed assets + `.forge/context` capability; `install` reinstalls cleanly | ⚠️ same path exists; not re-verified on published wheel |

## Documented degradations under the wheel

- **Context-manifest integrity fields** (lf-0037 wiring gap, tracked):
  `install/service.py::_context_manifest` reads `forge.json`/
  `forge.agentic.json` only via `_REPO_DIR` (`_PKG_DIR.parent.parent` — the
  checkout root; under `pip install` that is `site-packages`). This branch
  ships `apiforge/_data/forge*.json`; the reader switch to the bundled
  `_data` path (the same cand-list pattern `_group` already uses at
  `service.py:412`) belongs to the install/service wiring owned by lf-0037
  on `cycle/install-context` — recorded here per the ownership boundary.
- `install doctor`'s `mcp-handshake` reports **BLOCKED** when the `mcp`
  extra is not installed in the target interpreter — dependency state,
  not install corruption. `ledger` + `mcp-config` must be PASS.
- `install verify` is a real JSON-RPC handshake; in a bare venv without the
  `mcp` extra it refuses honestly (no traceback) — asserted for safety,
  not for success.

## Deliberately not packaged

The sdist ships the full tree (default Hatchling sdist — no `include`
narrowing): `forge.json`, `forge.agentic.json`, `manifest.json`,
`parity.yaml`, docs, tests and scripts all ship there for
wheel-from-sdist rebuilds and downstream verification tooling; the wheel
carries only runtime resources (no dev gates, no checkout tooling).

## Evidence

- Wheel isolation test: `tests/test_wheel_isolation.py`
  (`test_wheel_install_lifecycle_outside_checkout`, marker `slow`) —
  builds the wheel, installs into a clean venv (runtime deps resolved from
  the index; skips honestly when offline), proves `apiforge` imports from
  `site-packages`, then runs install → registry/contract →
  `knowledge list` → `rules lookup` → `install verify` →
  `install doctor` → `doctor` → repair → uninstall → reinstall from a
  consumer dir outside the checkout. Passing locally (~240s with
  `tests/test_artifact_contents.py`).
- `tests/test_artifact_contents.py::TestWheelCarriesDataLayer::
  test_forge_manifests` asserts `_data/forge.json` +
  `_data/forge.agentic.json` ride every future wheel.
- Wheel contents verified after this branch's packaging fix (1679 entries):
  `apiforge/_data/{forge.json,forge.agentic.json,knowledge,evals,
  tests/fixtures}`, `apiforge/host_assets/{skills,agents,
  AGENT_PROTOCOL.md}`, `apiforge/portal_assets` all present.
- Published `apiforge_af-0.1.6-py3-none-any.whl` (1676 entries) inspected:
  every resource group present **except** `_data/forge.json` and
  `_data/forge.agentic.json` — the gap this branch closes.

## Planned (lf-0037)

`discovery.ops` verbs over `.forge/context/` (`knowledge.search`,
`rules.search`, `capabilities.list`, …) are in flight on
`cycle/install-context`. When merged, extend the wheel test to exercise
them and promote the corresponding cells.
