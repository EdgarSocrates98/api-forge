# baseline evidence

Created before implementation. Commands and exact results are appended after
each wave; this file is intentionally not a claim of green verification.

Observed baseline:

- Default `uv run pytest -q --tb=short`: `1 failed, 906 passed, 2 skipped, 800 errors`; host ACL failure at `C:\Users\edgar\AppData\Local\Temp\pytest-of-edgar`.
- Controlled reruns use `--basetemp E:/pytest-apiforge-evo-convergence`.
- `uv run ruff check .` and `uv run ruff format --check .` include intentionally adversarial fixture drift; CI quality scope remains `src tests`.
- `uv run mypy`, release checks, skill validation, capability verification and agent drift checks passed before convergence waves.
- Index build initially hit generated `.pytest-run` symlink recursion; exact ignored artifact moved to `E:\pytest-apiforge-evo-convergence-artifact`, then index build/status passed with `stale=false`.
