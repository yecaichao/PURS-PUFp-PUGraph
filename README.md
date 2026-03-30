# PURS-PUFp-PUGraph

Unified Python package for:

- `PURS`
  - polymer-unit recognition from polymer SMILES
- `PUFp`
  - polymer-unit fingerprint generation and traditional ML workflows
- `PUGraph`
  - polymer-unit graph construction and wrapped graph-learning workflows

The package is organized around one shared core pipeline:

`polymer SMILES -> PURS core -> PUFp / PUGraph -> downstream tasks`

## Start Here

For package use, start from:

1. [examples/README.md](examples/README.md)
2. [Chinese package quickstart](docs/package_quickstart_zh.md)
3. [Chinese package architecture](docs/package_architecture_zh.md)

The main user-facing entry is `examples/`, not `tests/` or internal smoke scripts.

## Standard Sample Dataset

The package-level standard sample table is:

- `data/testing/opecm_paper54_tasks.csv`

It is the recommended unified example dataset because it already includes:

- normalized `smiles`
- mobility targets such as `ue`, `uh`, and `max_mobility`
- package-ready classification labels
- graph-task labels for wrapped graph workflows

## Installation

Basic install:

```bash
pip install -e .
```

Full workflow install:

```bash
pip install -e .[all]
```

Conda environment files are provided in `environments/`:

- `environment-core.yml`
- `environment-ml.yml`
- `environment-graph.yml`
- `environment-all.yml`

## Main Package Commands

### PURS

```bash
purs recognize --input-csv examples/basic_recognition/input.csv --output-dir output/basic
```

### PUFp

```bash
purs fingerprint --input-csv examples/pufp_mobility_demo/input.csv --name-column sample_id --smiles-column smiles --output-dir output/pufp_mobility_demo
```

### Traditional ML

```bash
purs ml rf --feature-csv output/pufp_mobility_demo/number.csv --target-csv examples/pufp_mobility_demo/target.csv --id-column sample_id --target-column target --quick
```

### PUGraph

```bash
purs graph build --input-csv examples/pugraph_demo/input.csv --output-dir output/graph_demo
purs graph train --config output/graph_demo/pu_gn_exp_train.yaml
```

## Recommended Example Order

Keep the public example set small and general:

1. `examples/basic_recognition/`
   - smallest core example
2. `examples/pufp_mobility_demo/`
   - recommended `PUFp + ML` example
3. `examples/pugraph_demo/`
   - recommended graph example

Other example folders are retained as supplementary reference material, not as primary package entry points.

## Repository Structure

```text
PURS-PUFp-PUGraph/
  src/purs/            package source code
  examples/            user-facing runnable examples
  docs/                package documentation
  data/                external, processed, and testing datasets
  environments/        conda environment files
  scripts/             helper and wrapper scripts
  tests/               internal regression tests
  repro/               method mapping and paper-reference material
```

## Documentation

Core docs:

- [Examples index](examples/README.md)
- [Chinese package quickstart](docs/package_quickstart_zh.md)
- [Chinese package architecture](docs/package_architecture_zh.md)
- [Package release validation](docs/package_release_validation.md)
- [Release checklist](docs/release_checklist.md)
- [Graph workflow notes](docs/graph_workflow.md)
- [Testing dataset strategy](docs/testing_datasets.md)

Additional docs:

- [Architecture](docs/architecture.md)
- [Dataset registry](docs/dataset_registry.md)
- [Schema](docs/schema.md)
- [Publish status](docs/publish_status.md)
- [Paper reproduction matrix](docs/paper_reproduction_matrix.md)

## Release Notes

This repository is intended to be:

- a unified package with a clear structure
- a package with coherent sample datasets
- a package with documented runnable examples

It is not presented primarily as an exact numerical reproduction of the source papers.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).

## Citation

Please cite the relevant PURS, PUFp, PUGraph, and OPECM papers when using the associated workflows.
