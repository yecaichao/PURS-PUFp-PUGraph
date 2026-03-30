# OPECM Standard Demo

This is the single public example recommended for the package.

It uses one standard sample table:

- `data/testing/opecm_paper54_tasks.csv`

This table already includes:

- normalized `smiles`
- mobility targets such as `ue`, `uh`, and `max_mobility`
- package-ready classification labels
- graph-task labels

## Recommended command

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo
```

This unified demo runs:

- paper54-style classification summary
- `PUFp` regression quick baselines
- graph build checks for `ue` and `uh`
- wrapped graph config validation

## Optional graph execution

```bash
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_standard_demo --execute-graphs
```

## Direct core check

```bash
purs recognize --input-csv data/testing/opecm_paper54_tasks.csv --name-column sample_id --smiles-column smiles --output-dir output/opecm_standard_demo/recognize
```
