# PURS-PUFp-PUGraph

Unified Python package for:

- `PURS`: polymer-unit recognition from polymer SMILES
- `PUFp`: polymer-unit fingerprint generation and lightweight ML workflows
- `PUGraph`: polymer-unit graph construction and wrapped graph-learning workflows

The package is organized around one shared pipeline:

`polymer SMILES -> PURS core -> PUFp / PUGraph -> downstream tasks`

## Start Here

This release keeps one public example:

- `examples/opecm_standard_demo/`

It is backed by one standard sample table:

- `data/testing/opecm_paper54_tasks.csv`

Recommended command:

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo
```

Optional graph execution:

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo --execute-graphs
```

## Installation

Basic install:

```bash
pip install -e .
```

Full workflow install:

```bash
pip install -e .[all]
```

Conda environments are also provided in `environments/`.

## Minimal Repository Structure

```text
PURS-PUFp-PUGraph/
  src/purs/                    package source code
  examples/opecm_standard_demo single public example
  data/testing/                standard sample table
  docs/                        minimal package docs
  scripts/                     runnable helper scripts
  tests/                       internal regression checks
```

## Documentation

- `examples/README.md`
- `docs/package_quickstart_zh.md`
- `docs/package_architecture_zh.md`

## License

This project is released under the MIT License. See `LICENSE`.
