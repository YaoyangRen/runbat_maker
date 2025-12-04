# Runbat Maker – AI Coding Guide

## Core Purpose
- This repo ships a single utility (`runbat_maker.py`) that scans user-selected folders or files for MCNP decks (`*.i` / `*.inp`) and emits a runnable `run.bat` invoking `mcnp6.exe` with absolute paths.
- The PyInstaller build (`runbat_maker.spec`) produces the distributable EXE consumed by PowerShell installers and Explorer context-menu hooks; keep the binary self-contained (stdlib only).

## Code Layout & Data Flow
- `runbat_maker.py` now exposes an `argparse` CLI. Maintenance operations (registry writes, shell/startup registration) run first; if no `--dir/--input` is provided the script exits after maintenance.
- `generate_bat_file()` still writes absolute `mcnp6.exe i=<abs>.i o=<abs>.o tasks 93`, `del runtp*`, `del src*`, then `pause`; order and absolute paths must remain unchanged (mirror `test/run.bat`).
- Context-menu commands call the EXE with `--dir "%V"` or `--input "%1"`; `--silent` skips the interactive prompt so Explorer calls do not hang.
- MCNP6 integration uses registry helpers (`HKCU\Software\RunbatMaker`, value `MCNP6Path`). Keep registry access isolated in helper functions for PyInstaller compatibility.

## Build & Packaging Workflow
- PyInstaller specs live at repo root. `runbat_maker.spec` is authoritative; `main.spec` is legacy. Build via `pyinstaller runbat_maker.spec` at repo root and distribute `dist/runbat_maker/runbat_maker.exe`.
- `scripts/install.ps1` copies the EXE into `%LOCALAPPDATA%\RunbatMaker`, prompts for the MCNP6 path, and executes `--set-mcnp-path --register-shell --register-startup`. `scripts/uninstall.ps1` performs the reverse plus registry cleanup.
- Never edit `build/` artifacts; regenerate by rerunning PyInstaller.

## Testing & Validation
- Manual regression: drop representative decks under a temp folder (samples in `test/`), run `python runbat_maker.py --dir <folder>`, and diff the generated `run.bat` against `test/run.bat`.
- For MCNP6 integration, set a sandbox path via `--set-mcnp-path` and run `--run-mcnp` to confirm copying/execution semantics without touching production installs.
- After changing registry/startup logic, run `scripts/install.ps1` then inspect `HKCU\Software\RunbatMaker`, `HKCU\Software\Classes\...\RunbatMaker_*`, and `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` entries; uninstall with `scripts/uninstall.ps1` to ensure cleanup.

## Conventions & Gotchas
- Always emit absolute paths and preserve the command order (`mcnp6.exe ...`, `del runtp*`, `del src*`, `pause`).
- `generate_bat_file()` writes using `locale.getpreferredencoding(False)` so non-ASCII deck names remain readable to `cmd.exe`; avoid forcing UTF-8 unless you also update MCNP6 launch requirements.
- Input/output paths must be wrapped in double quotes in `run.bat` so MCNP6 handles spaces or localized characters; keep that quoting logic when refactoring.
- CLI flags must work both in CPython and PyInstaller contexts; avoid environment-dependent defaults. Keep bilingual prompts for interactive flows and suppress them via `--silent` when wiring automation.
- Registry writes must stay under HKCU; provide guardrails when paths are invalid. Use the existing helper to fetch `winreg` so non-Windows environments fail gracefully.
- Input enumeration purposely stays shallow (single directory). Add recursion only behind opt-in flags and update docs/tests accordingly.
- Explorer verbs cover folder icons (`Directory`), folder backgrounds (`Directory\Background`), and individual files (`*`). Update every entry inside `SHELL_DEFINITIONS` plus the install/uninstall scripts together when adding/removing verbs.

## When Adding Features
- Follow the current procedural style; helper functions should remain in `runbat_maker.py` unless the module grows significantly.
- Update `README.md` and `.github/copilot-instructions.md` whenever CLI flags, registry keys, or installer steps change; keep `scripts/install.ps1` / `scripts/uninstall.ps1` in sync.
- For user-facing changes, validate both the raw script (`python runbat_maker.py`) and the packaged EXE, especially when modifying `set_working_directory()` or context-menu arguments.
- Maintain the final interactive pause for manual runs; wrap new automation paths with `--silent` checks.
