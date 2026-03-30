# PUFp Mobility Demo

This is the recommended package-level example for the `PUFp + ML` workflow.

Files:

- `input.csv`
  - normalized polymer inputs
  - required columns: `sample_id`, `smiles`
- `target.csv`
  - aligned regression targets
  - required columns: `sample_id`, `target`

Source:

- derived from `data/testing/opecm_paper54_tasks.csv`
- intended as a lightweight slice of the package's standard master sample table

## Recommended workflow

Generate fingerprints:

```bash
purs fingerprint --input-csv examples/pufp_mobility_demo/input.csv --name-column sample_id --smiles-column smiles --output-dir output/pufp_mobility_demo
```

Run a lightweight baseline:

```bash
purs ml rf --feature-csv output/pufp_mobility_demo/number.csv --target-csv examples/pufp_mobility_demo/target.csv --id-column sample_id --target-column target --quick
```

You can replace `rf` with:

- `krr`
- `svm`

## Why this example exists

- it is small enough for package demos
- it uses the same normalized data style as the larger OPECM-derived example suite
- it demonstrates the clean handoff from `PURS` outputs to `PUFp` features and then to ML
