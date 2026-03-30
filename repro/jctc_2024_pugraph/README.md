# JCTC 2024 PUGraph Reproduction

Use this directory for publication-scale graph workflows and exact settings used in the PUGraph paper.

For the maintained unified workflow, start from:

- `docs/reproduction_zh.md`
- `docs/graph_workflow.md`
- `docs/paper_reproduction_matrix.md`
- `docs/osc_parent_schema.md`
- `data/testing/opecm_osc_parent.csv`
- `data/testing/opecm_paper67_tasks.csv`

Use this `repro/` folder for paper-specific settings, frozen configs, and final publication-oriented runs,
not for the general package smoke tests.

## Shared starting point

The maintained repository now treats the PUGraph paper as one branch of a shared OSC pipeline:

`OSC parent table -> PURS -> Polymer-Unit Graph -> GNN`

## Current task-table semantics

The generated `opecm_paper67_tasks.csv` is a paper-style test table, not yet the exact paper-original
`697`-sample OSC dataset.

It is intended to stabilize:

- hole/electron mobility four-bin label generation
- Polymer-Unit Graph construction inputs
- `PU-gn-exp` and `PU-MPNN` command paths

## Next reproduction goals

1. freeze explicit paper-style `PU-gn-exp` classification labels and configs
2. formalize `MACCS166` and `GenWL280` node-feature builders
3. add a `PU-MPNN vs mol-MPNN` runtime/MSE benchmark harness
