# ACS AMI 2023 PUFp Reproduction

Use this directory for publication-scale material related to the PUFp paper:

- curated datasets
- exact preprocessing settings
- experiment scripts
- figure reproduction notes

## Shared starting point

The maintained repository now treats the PUFp paper as one branch of a shared OSC pipeline:

`OSC parent table -> PURS -> PUFp -> ML`

Start from:

- `docs/paper_reproduction_matrix.md`
- `docs/osc_parent_schema.md`
- `data/testing/opecm_osc_parent.csv`
- `data/testing/opecm_paper54_tasks.csv`

## Current task-table semantics

The generated `opecm_paper54_tasks.csv` is a paper-style test table, not yet the exact paper-original
`678`-sample OSC dataset.

It is intended to stabilize:

- `n/p` carrier-type labeling
- `high/medium/low` mobility grouping
- `PURS -> PUFp -> ML` command paths

## Next reproduction goals

1. add paper-style `PUFp vs MACCS vs Morgan` baselines
2. add `KNN`, `Gaussian Process`, and `MLP`
3. freeze the exact paper-original `678` OSC table once it is recovered
