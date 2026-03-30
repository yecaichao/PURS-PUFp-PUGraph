# OPECM Standard Demo

This is the single public example recommended for the released package.

It uses the package-level standard master sample table:

- `data/testing/opecm_paper54_tasks.csv`

That table already includes:

- normalized `smiles`
- mobility targets such as `ue`, `uh`, and `max_mobility`
- classification labels
- graph-task labels

So one dataset can drive the main package workflows without exposing many separate example datasets.

## Recommended command

Run the unified standard demo:

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo
```

This will run:

- paper54-style classification summary
- `PUFp` regression quick baselines
- graph build checks for `ue` and `uh`
- wrapped graph config validation

## Optional graph execution

If you also want to execute the wrapped graph backends:

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo --execute-graphs
```

## Direct core check

If you only want the smallest direct `PURS` check on the same standard table:

```bash
purs recognize --input-csv data/testing/opecm_paper54_tasks.csv --name-column sample_id --smiles-column smiles --output-dir output/opecm_standard_demo/recognize
```

## Why this example exists

- one public sample table is easier to explain
- one demo is easier to publish than several parallel examples
- it still covers `PURS`, `PUFp`, and `PUGraph` through one coherent source
