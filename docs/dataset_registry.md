# Dataset Registry

## Purpose

This file defines the role of each dataset in the unified `PURS-PUFp-PUGraph` repository.

The main goal is to keep one clear public sample source for the package while preserving
supporting datasets for maintenance and method mapping.

## Dataset roles

### 1. Core external databases

These are authoritative or published datasets that should be preserved in near-original form.

#### OPECM Dataset

Source:

- GitHub: [OPECM-Dataset](https://github.com/yecaichao/OPECM-Dataset)

Recommended placement:

- `data/external/opecm/1_raw_data.csv`
- `data/external/opecm/OPECM_dataset.xlsx`
- `data/processed/opecm/2_PU_data.csv`
- `data/processed/opecm/3_Descriptors.csv`

Recommended role:

- `1_raw_data.csv`: canonical external raw dataset for unified ingestion
- `2_PU_data.csv`: processed polymer-unit-level dataset
- `3_Descriptors.csv`: descriptor table for downstream ML workflows
- `OPECM_dataset.xlsx`: archival and manual inspection version

### 2. Standard package sample table

This is the main release-facing dataset for examples and package-level validation.

#### Standard master table

Placement:

- `data/testing/opecm_paper54_tasks.csv`

Role:

- provides one unified package sample table
- supports `PURS`, `PUFp`, classification, regression, and graph preparation
- keeps precomputed labels in the same table as the normalized sample records

Important columns include:

- `sample_id`
- `smiles`
- `ue`
- `uh`
- `homo`
- `lumo`
- `eg`
- `dominant_carrier`
- `max_mobility`
- `paper54_carrier_type`
- `paper54_mobility_class3`
- `paper67_ue_class4`
- `paper67_uh_class4`

### 3. Supporting parent datasets

These remain useful for focused checks and maintenance, but they are not the preferred public
entry point.

Placement:

- `data/testing/common_polymer_cases.csv`
- `data/testing/opecm_pce_cases.csv`
- `data/testing/opecm_ue_cases.csv`
- `data/testing/opecm_uh_cases.csv`
- `data/testing/opecm_paper67_tasks.csv`
- `data/testing/opecm_osc_parent.csv`

Role:

- target-specific comparisons
- rawer intermediate tables
- method mapping support
- maintenance scripts

### 4. Software examples

These datasets should be small and quick to run.

#### Basic recognition example

Placement:

- `examples/basic_recognition/input.csv`

Role:

- validates the `recognize` and `classify` flow

#### PUFp mobility demo

Placement:

- `examples/pufp_mobility_demo/input.csv`
- `examples/pufp_mobility_demo/target.csv`

Role:

- demonstrates `PURS -> PUFp -> ML`
- derives from `data/testing/opecm_paper54_tasks.csv`

#### PUGraph demo

Placement:

- `examples/pugraph_demo/input.csv`

Role:

- demonstrates graph-data preparation and config-driven graph workflow entry points
- derives from `data/testing/opecm_paper54_tasks.csv`
- still writes the legacy `PCE_max` graph column name internally because the current wrapped graph
  backends expect that field name

#### Supplementary demos

Placement:

- `examples/opecm_demo/input.csv`
- `examples/pufp_opv_demo/input.csv`
- `examples/pufp_opv_demo/target.csv`

Role:

- supplementary reference material
- compatibility and method mapping

### 5. Test fixtures

These files exist only for correctness checks and should stay minimal.

Placement:

- `tests/fixtures/tiny_polymers.csv`
- `tests/fixtures/duplicate_names.csv`
- `tests/fixtures/invalid_smiles.csv`
- `tests/fixtures/opv_tiny.csv`
- `tests/fixtures/mobility_tiny.csv`

Role:

- smoke tests
- edge-case tests
- regression protection

## Naming rules

- Prefer stable ASCII file names.
- Prefer explicit stage labels such as `raw`, `processed`, `demo`, and `tiny`.
- Keep a shared ID column whenever possible.
- Treat `opecm_paper54_tasks.csv` as the package-level master sample table unless and until a more
  release-neutral replacement name is introduced.
