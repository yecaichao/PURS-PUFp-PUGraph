# Data Layout

This directory is the unified home for curated datasets used by the package.

For release-facing package examples, the current standard sample table is:

- `data/testing/opecm_paper54_tasks.csv`

## Principles

- `data/external/`: external or source datasets kept close to their published form
- `data/processed/`: cleaned, transformed, or package-aligned datasets
- `examples/`: tiny demo subsets for user-facing quick starts
- `tests/fixtures/`: minimal files for automated validation
- `repro/`: publication-specific workflows and exact reproduction material

Do not mix these roles.

## OPECM placement

Recommended placement for the [`OPECM-Dataset`](https://github.com/yecaichao/OPECM-Dataset) repository:

- `data/external/opecm/1_raw_data.csv`
- `data/external/opecm/OPECM_dataset.xlsx`
- `data/processed/opecm/2_PU_data.csv`
- `data/processed/opecm/3_Descriptors.csv`

This keeps the original database separated from lightweight demos and test fixtures.
