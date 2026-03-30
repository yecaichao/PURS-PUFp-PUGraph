# Testing Dataset Strategy

## Goal

The repository should keep one release-facing standard sample table instead of scattering package
examples across unrelated CSV files.

Small example files and tiny fixtures should be derived from that standard table whenever practical.

## Current standard sample table

Primary release-facing dataset:

- `data/testing/opecm_paper54_tasks.csv`

This is the recommended unified package sample table because it already includes:

- normalized `smiles`
- scalar properties such as `ue`, `uh`, `homo`, `lumo`, and `eg`
- derived fields such as `dominant_carrier` and `max_mobility`
- package-ready classification labels such as `paper54_carrier_type`
- graph-task labels such as `paper67_ue_class4` and `paper67_uh_class4`

It is therefore suitable as a single source for:

- package examples
- package-level validation
- PUFp classification and regression demonstrations
- PUGraph input preparation demonstrations

## Supporting parent datasets

The following datasets are still useful, but they are now supporting tables rather than the main
release-facing sample source:

- `data/testing/common_polymer_cases.csv`
- `data/testing/opecm_pce_cases.csv`
- `data/testing/opecm_ue_cases.csv`
- `data/testing/opecm_uh_cases.csv`

Recommended semantics:

- `opecm_paper54_tasks.csv`: standard master sample table for published package examples
- `common_polymer_cases.csv`: broad OPECM-derived table using `Eg/eV` as a shared target
- `opecm_pce_cases.csv`: OPECM PCE-only subset for OPV-style checks
- `opecm_ue_cases.csv`: target-specific `ue` subset for focused comparisons
- `opecm_uh_cases.csv`: target-specific `uh` subset for focused comparisons

## Donor/acceptor note

Manual inspection of `data/external/opecm/OPECM_dataset.xlsx` shows:

- `1-raw data`
- `2-PU data`
- `3-Descriptors`

The workbook does not expose explicit donor/acceptor structure columns such as `donor_smiles`,
`acceptor_smiles`, `n(SMILES)`, or `p(SMILES)` at the sheet-header level.

That means OPECM can support single-SMILES property testing directly, but it should not be treated
as a donor/acceptor-pair benchmark unless an upstream paired source is added later.

## Current generation scripts

The package-level OPECM task tables can be rebuilt with:

```powershell
$env:PYTHONPATH='src'
python scripts/build_osc_paper_tables.py
```

The lightweight example files and fixtures can be refreshed with:

```powershell
$env:PYTHONPATH='src'
python scripts/refresh_demo_datasets.py
```

## Why this is better

- the package has one clear release-facing standard sample source
- examples and fixtures no longer drift independently in meaning
- classification and graph labels live in the same table as the sample records
- target-specific subsets remain available without becoming the public default

## Future recommendation

If the repository keeps growing, consider adding explicit usage flags to the standard table, such as:

- `use_basic`
- `use_ml`
- `use_graph`
- `use_fixture`

That would make example and fixture generation even more explicit.
