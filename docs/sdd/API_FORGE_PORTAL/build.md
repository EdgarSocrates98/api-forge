---
sdd: 1
feature: API_FORGE_PORTAL
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "177e039e75be54336e3d6172a01bba7e29e1d902459db0333dca0f7b577c4f4d"
tasks:
  - id: T1
    status: done
  - id: T2
    status: done
  - id: T3
    status: done
  - id: T4
    status: done
  - id: T5
    status: done
  - id: T6
    status: done
claims:
  - AC1..AC8 verdes em tests/test_portal_adapter.py (20 testes)
red:
  - cmd: ".venv/Scripts/python -m pytest tests/test_portal_adapter.py::test_bootstrap_workspace_vazio -x -q"
    exit: 1
    note: "health DEGRADED num workspace virgem — doctor 'broken' vencia o ledger vazio; corrigido em _health_state (ledger precede doctor)"
  - cmd: ".venv/Scripts/python -m pytest tests/test_portal_adapter.py::test_task_analyze_real_api -x -q"
    exit: 1
    note: "case_dir/manifest.json ausente — o engine persiste case.json como manifesto; asserção corrigida para o layout real"
  - cmd: ".venv/Scripts/python -m ruff check src/apiforge/portal_adapter.py tests/test_portal_adapter.py"
    exit: 1
    note: "8 erros (F841, S112, RUF059, RUF100) — resolvidos; S112 virou helper _try_view"
green:
  - cmd: ".venv/Scripts/python -m pytest tests/test_portal_adapter.py -x -q"
    exit: 0
    note: "20 passed — inclui análise real de API via portal com case persistido (gate FASE 4)"
  - cmd: ".venv/Scripts/python -m ruff check src/apiforge/portal_adapter.py src/apiforge/cli_portal.py tests/test_portal_adapter.py"
    exit: 0
  - cmd: ".venv/Scripts/python -m pytest tests/test_command_rationale.py -q"
    exit: 0
    note: "verbo portal com why/when; divergence 0 undocumented"
---

# build

Implementado em uma passada; reds reais corrigidos na raiz (semântica de
saúde, layout do case persistido, lint).
