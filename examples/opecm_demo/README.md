# OPECM Demo

This example is a lightweight subset extracted from the full OPECM database.

Purpose:

- provide a realistic input source for `purs recognize`
- test the unified package on real polymer records
- avoid using the full database for every quick-start run

Files:

- `input.csv`: small subset with normalized columns `sample_id` and `smiles`

Recommended next use:

```bash
purs recognize --input-csv examples/opecm_demo/input.csv --name-column sample_id --smiles-column smiles --output-dir output/opecm_demo
```
