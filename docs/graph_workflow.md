# Graph Workflow Notes

## What is wired now

The unified repository now supports a lightweight graph workflow wrapper:

- `purs graph build`
  - runs the shared PURS recognition core
  - writes core outputs into `output_dir/core`
  - creates a normalized `graph_input.csv`
  - excludes records already reported as skipped by the shared PURS core
  - writes `graph_dataset_manifest.json`
  - writes `graph_build_manifest.json`
  - writes executable starter configs for `PU-gn-exp` and `PU-MPNN`

- `purs graph train`
  - reads a graph config yaml
  - validates backend, mode, and required file paths before returning a command
  - supports `pu_gn_exp` in `command_only` or `execute` mode
  - supports `pu_mpnn` in `command_only` or `execute` mode
  - for `pu_mpnn`, now returns a fully parameterized preprocessing command based on `data_csv` and `output_pkl`

## Current scope

This is intentionally a wrapper-first integration.

The goal of the current stage is to:

- unify file layout
- standardize data handoff
- keep legacy graph assets inside the same repository
- provide one command surface for future cleanup

## Legacy assets now included

- `src/purs/graph/pu_gn_exp/polymer_unit/`
- `src/purs/graph/pu_mpnn/legacy/`

These folders are preserved so later refactoring can happen inside one repository.

## Current cleanup status

The active `PU-gn-exp` dataset execution path has been partially cleaned up.

It now routes legacy PURS-style graph feature construction through:

- `src/purs/graph/legacy_purs_adapter.py`

This improves the current state by:

- removing multiple direct PURS imports from the active `PU-gn-exp` dataset path
- centralizing the legacy graph feature-building dependency in one adapter
- making future replacement with unified `purs.core` / `purs.graph` code easier

The wrapped `PU-gn-exp` training path now treats `PCE_max` as a continuous regression target at the
wrapper level. Legacy internals still remain, but the active training loss/reporting path no longer
casts target values into classification labels.

For the default unified demo/testing path, the graph input now comes from OPECM `ue`
single-SMILES cases and is normalized into the legacy `PCE_max` column name only because the
wrapped graph backends still expect that field name.

The old legacy files are still present, but they are no longer the preferred import path for the active `PU-gn-exp` dataset loader.

For `PU-MPNN`, the active preprocessing guidance now points to:

- `src/purs/graph/legacy_mpnn_adapter.py`
- `src/purs/graph/pu_mpnn/prepare.py`

This means the recommended preprocessing route no longer needs to import `legacy/API.py` directly from user-facing wrapper code.
The wrapper also accepts explicit CLI arguments so generated graph configs can feed the preprocessing step directly.

## What still needs deeper refactoring

1. Remove duplicate PURS logic embedded inside legacy graph modules.
2. Standardize graph preprocessing so it uses the unified `purs.core` outputs directly.
3. Replace notebook-dependent preprocessing with scripted commands.
4. Extend graph config validation to cover more backend-specific fields once training schemas are finalized.
5. Add execute-mode smoke tests for `pu_gn_exp` and a deeper `pu_mpnn` preparation fixture once graph dependencies are standardized.
