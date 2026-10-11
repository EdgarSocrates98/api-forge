---
sdd: 1
feature: API_FORGE_PORTAL
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "f07eaf1aab49a48ff841853cef9b4b28c01952e02670208eb9caa32511c6a06d"
tasks:
  - id: T1
    desc: vendor _forge_portal.py + portal/assets via forge-portal/scripts/vendor.py --repo api-forge
    covers: [assets-clone-e-wheel]
    test: sdd/API_FORGE_PORTAL/evidence/portal-tests.txt
    risk: low
    rollback: remover os arquivos vendored
    status: done
  - id: T2
    desc: portal_adapter.py — operações bootstrap/health/install/profiles/hosts/mcp/skills/agents/tasks/graphs/docs
    covers: [portal-http-surface, named-refusals]
    test: sdd/API_FORGE_PORTAL/evidence/portal-tests.txt
    risk: low
    rollback: remover src/apiforge/portal_adapter.py
    status: done
  - id: T3
    desc: cli_portal.py register(app) + verbo portal com --no-browser/--port/--root
    covers: [portal-http-surface]
    test: sdd/API_FORGE_PORTAL/evidence/portal-tests.txt
    risk: low
    rollback: remover cli_portal.py e o register no cli.py
    status: done
  - id: T4
    desc: pyproject force-include portal/assets → apiforge/portal_assets; ignores ruff/mypy do vendored
    covers: [assets-clone-e-wheel]
    test: sdd/API_FORGE_PORTAL/evidence/portal-tests.txt
    risk: low
    rollback: reverter o bloco force-include
    status: done
  - id: T5
    desc: install lifecycle via plan_token+confirm + analyze task com sandbox de workspace e case persistido (gate FASE 4)
    covers: [install-plan-confirm-apply, analyze-real-via-portal, named-refusals]
    test: sdd/API_FORGE_PORTAL/evidence/portal-tests.txt
    risk: medium
    rollback: remover ops /installation/* e o verbo analyze
    status: done
  - id: T6
    desc: rationale command-rationale.json + recipe docs/learn/recipes/portal.md + index
    covers: [portal-http-surface]
    test: sdd/API_FORGE_PORTAL/evidence/rationale.txt
    risk: low
    rollback: reverter os arquivos de doc
    status: done
---

# plan

Seis tarefas sequenciais: vendoring → adapter → CLI → packaging →
lifecycle+analyze gate → docs. Cada uma com teste dedicado.
