# Smoke Test

## Purpose

This repository includes a lightweight release-style smoke test that exercises the main command surfaces end to end.

## Command

```powershell
python scripts/run_smoke_release.py
```

Run this after activating an environment that already contains the workflow dependencies.
On Windows, launching the script from an activated environment is more reliable than wrapping it
with `conda run` when the repository lives under a non-ASCII path.

## Current coverage

The smoke script checks:

- `purs fingerprint`
- `purs ml rf --quick`
- `purs graph build`
- `purs graph train` for `PU-gn-exp` in `command_only` and `execute` mode
- `purs graph train` for `PU-MPNN` in `command_only` and `execute` mode
- `purs recognize --strict` on invalid input as an expected-failure case

## Output

Results are written under:

- `output/smoke_release/`

The main summary file is:

- `output/smoke_release/smoke_summary.json`
