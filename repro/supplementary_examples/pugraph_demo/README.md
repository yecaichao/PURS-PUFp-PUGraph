# PUGraph Demo

This is the recommended package-level example for `PUGraph`.

Use it when you want to:

- convert normalized polymer inputs into graph-ready data
- generate a shared graph manifest
- produce starter configs for `PU-gn-exp` and `PU-MPNN`

Source:

- derived from `data/testing/opecm_paper54_tasks.csv`
- uses the same standard master sample table as the package-level mobility example

## Recommended workflow

Build graph assets:

```bash
purs graph build --input-csv repro/supplementary_examples/pugraph_demo/input.csv --output-dir output/graph_demo
```

Inspect or run a wrapped backend:

```bash
purs graph train --config output/graph_demo/pu_gn_exp_train.yaml
```

## Notes

- `graph build` is the main value of this example
- the generated YAML files are intended as starter configs
- this example is meant to clarify package structure, not to reproduce full publication-scale runs
