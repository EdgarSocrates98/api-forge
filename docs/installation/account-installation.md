# Account-scoped installation

Run `install.sh` (POSIX) or `install.ps1` (Windows) from this checkout. Installer performs `pip install -e .` into an isolated account runtime under `~/.forge/installs/api-forge/.venv`. It does not create a virtual environment inside a project workspace.

Published variables use prefix `API_FORGE`: `HOME`, `INSTALL_ROOT`, `VENV`, `PYTHON`, `CLI`, and `LAUNCHER`. Names use underscores because POSIX shells reject hyphens. Windows also receives compatibility aliases such as `API-FORGE-HOME`, without administrator permission.

POSIX installer writes `~/.config/forjas/env.sh`; open a new shell or run `source ~/.config/forjas/env.sh`. Windows processes opened after installation receive HKCU variables.

`setup.sh`/`setup.ps1` remains compatibility mode for wheel-style installation. The Forge doctor and Portal validate these paths without exposing secrets.
