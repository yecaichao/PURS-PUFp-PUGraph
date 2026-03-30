# Data Schema Notes

## Goal

This document records the column conventions used across the unified repository.

The package should accept legacy column names when practical, but internal normalization should be consistent.

## Core input columns

### Preferred canonical names

- `sample_id`: preferred generic sample identifier
- `name`: acceptable alternative sample identifier for simple demos
- `smiles`: preferred canonical SMILES column

### Legacy names currently supported in detection

For sample identifiers:

- `name`
- `Name`
- `No.`
- `No`
- `ID`
- `Compound ID`

For SMILES:

- `smiles`
- `SMILES`
- `n(SMILES)`
- `p(SMILES)`

## Graph workflow normalized columns

`purs graph build` writes a normalized graph input table with:

- `Compound ID`
- `smiles`
- optionally `PCE_max`

This mirrors the expectations of the current `PU-gn-exp` workflow.

## ML workflow columns

The ML layer expects:

- a feature table whose row index is the sample id
- a target table containing:
  - one ID column
  - one target column

Examples:

- `sample_id` + `target`
- `No.` + `PCE_max(%)`

## Testing parent datasets

- `data/testing/common_polymer_cases.csv`
  - stores `regression_target` / `graph_target` from OPECM `Eg/eV`
  - includes metadata columns such as `target_name`, `target_unit`, and `target_source_column`
- `data/testing/opecm_pce_cases.csv`
  - stores `regression_target` / `graph_target` from OPECM `PCE/%`
  - should be preferred for OPV-style ML and graph demos
- `data/testing/opecm_ue_cases.csv`
  - stores `regression_target` / `graph_target` from OPECM `ue`
  - should be preferred for unified single-SMILES ML and graph testing
- `data/testing/opecm_uh_cases.csv`
  - stores `regression_target` / `graph_target` from OPECM `uh`
  - is available for hole-mobility-specific testing

## Stability rule

Column names may vary in external datasets, but the package should:

1. detect common legacy names
2. report the resolved columns in CLI output and run summaries
3. avoid silently changing meanings of identifiers or targets
