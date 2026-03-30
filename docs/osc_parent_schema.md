# OSC Parent Schema

## Purpose

This document defines the shared parent-table schema used to connect the `PUFp` and `PUGraph`
paper reproductions inside the unified repository.

The key design rule is:

- one shared OSC parent table
- shared `PURS` preprocessing
- paper-specific task tables derived from the same parent table

## Parent table

Current generated file:

- `data/testing/opecm_osc_parent.csv`

This is not the exact `678`-sample or `697`-sample paper dataset.
Instead, it is a paper-style canonical OSC table derived from OPECM so the repository can keep one
stable schema and one stable set of regression tests.

## Canonical columns

Identity and structure:

- `source_dataset`
- `source_record_id`
- `sample_id`
- `smiles`

Core OSC properties:

- `ue`
- `uh`
- `homo`
- `lumo`
- `eg`

Auxiliary physical properties:

- `epsilon`
- `alpha`
- `mu`

Quality flags:

- `expected_valid`
- `notes`

Shared derived columns:

- `dominant_carrier`
- `max_mobility`

Paper A derived labels:

- `paper54_carrier_type`
- `paper54_mobility_class3`
- `paper54_mobility_class3_id`
- `paper54_ready`

Paper B derived labels:

- `paper67_ue_class4`
- `paper67_ue_class4_id`
- `paper67_uh_class4`
- `paper67_uh_class4_id`
- `paper67_ready`

## Label rules

### Paper A: PUFp-style labels

Carrier type:

- `n` if `ue > uh`
- `p` if `uh > ue`
- `tie` if `ue == uh`

Mobility class:

- `high` if `max(ue, uh) > 4`
- `medium` if `1 < max(ue, uh) <= 4`
- `low` if `0 <= max(ue, uh) <= 1`

### Paper B: PUGraph-style labels

Four-bin mobility labels are generated separately for `ue` and `uh`:

- `0_to_1`
- `1_to_4`
- `4_to_10`
- `gt_10`

These bins follow the ranges described in the paper body and Table 1 summary.

## Derived task tables

Current generated files:

- `data/testing/opecm_paper54_tasks.csv`
- `data/testing/opecm_paper67_tasks.csv`
- `output/opecm_osc_unified_example/` via `scripts/run_opecm_osc_unified_example.py`

Semantics:

- `opecm_paper54_tasks.csv`
  - valid SMILES
  - both `ue` and `uh` present
  - paper54 labels ready

- `opecm_paper67_tasks.csv`
  - valid SMILES
  - both `ue` and `uh` present
  - `homo` and `lumo` present
  - paper67 labels ready

## Why this matters

This shared schema lets the repository do three things cleanly:

1. maintain one canonical OSC data interface
2. keep paper-style tests reproducible
3. drop in the exact paper-original `678` and `697` datasets later without redesigning downstream code

## Unified example runner

The repository now provides one fixed package-level unified example built from the OPECM-derived OSC
task tables:

```powershell
$env:PYTHONPATH='src'
python scripts/run_opecm_osc_unified_example.py
```

This runner currently does the following:

1. runs paper54-style `PUFp` classification benchmarks on `opecm_paper54_tasks.csv`
2. prepares normalized ML input and target csv files from `opecm_paper54_tasks.csv`
3. prepares normalized graph input csv files for `ue` and `uh` from `opecm_paper67_tasks.csv`
4. runs `PURS -> PUFp`
5. runs `RF / KRR / SVM` quick baselines on `max_mobility`
6. runs `graph build` for both `ue` and `uh`
7. validates `PU-gn-exp` and `PU-MPNN` train-config generation in `command_only` mode

Use `--execute-graphs` only when you explicitly want to run the wrapped graph backends.
