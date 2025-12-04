# Runbat Maker – AI Coding Guide

## Core Purpose
- This repo ships a single utility (`runbat_maker.py`) that scans the working folder for MCNP input decks (`*.i` / `*.inp`) and emits a runnable `run.bat` script for `mcnp6.exe`.
- The script is packaged into a standalone EXE via PyInstaller (`runbat_maker.spec`); design decisions (e.g., `set_working_directory()`) exist to keep the packaged binary self-contained.

## Code Layout & Data Flow
- `runbat_maker.py` drives everything: `main()` → `set_working_directory()` (pins CWD to the executable dir) → `os.listdir` scan → `generate_bat_file()` writes absolute `mcnp6.exe` invocations and cleanup commands.
- `generate_bat_file()` expands each input into `mcnp6.exe i=<abs>.i o=<abs>.o tasks 93`, then appends `del runtp*`, `del src*`, and a trailing `pause`. Maintain this sequencing because downstream workflows expect those cleanup steps between runs (see `test/run.bat`).
- User prompts like `"按 Enter 键继续..."` are part of the UX; keep bilingual messaging consistent when extending CLI interactions.

## Build & Packaging Workflow
- PyInstaller specs live at repo root. `runbat_maker.spec` produces the shipping binary; build with `pyinstaller runbat_maker.spec` from `d:\ryy\code\runbat_maker`.
- `main.spec` references `main.py`, which is not present—treat it as legacy; update or remove only if you also adjust CI/build docs.
- Generated artifacts land under `build/` and `dist/` (dist is gitignored). Do not hand-edit files under `build/`; re-run PyInstaller instead.

## Testing & Validation
- Manual regression: drop representative `.i`/`.inp` samples into the repo root (examples live under `test/`), run `python runbat_maker.py`, inspect the emitted `run.bat`, and compare against `test/run.bat` for structure.
- When adjusting path logic, re-run the packaged EXE (after PyInstaller build) to ensure `set_working_directory()` still resolves input files correctly when launched via Explorer.

## Conventions & Gotchas
- Always write absolute paths into `run.bat`. Downstream MCNP tooling is sensitive to relative paths when `run.bat` is executed from other directories.
- Keep the `tasks 93` token unless requirements change; consumers rely on this default parallelism setting.
- Respect the simple dependency footprint—stdlib only. If you must add packages, update the PyInstaller spec and document why.
- Input enumeration is intentionally shallow (current directory only); if you need recursion or filtering, gate it behind explicit flags to avoid surprising existing users.

## When Adding Features
- Mirror the existing procedural style; if you introduce helpers, keep them in `runbat_maker.py` unless a broader module split is justified.
- Provide sample output updates in `README.md` and, if behavior changes, refresh `test/run.bat` so others can diff expected automation.
- Confirm that interactive pauses remain at the end of the run to support double-click execution.
