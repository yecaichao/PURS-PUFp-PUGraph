# Stability Notes

## Current policy

The unified repository should prefer explicit failure reporting over silent skipping.

For `purs recognize`, the current behavior is:

- invalid or unreadable input SMILES are skipped instead of crashing the whole run
- skipped rows are written to `skipped_records.csv`
- run-level counts are written to `run_summary.json`
- CLI output reports total rows, processed rows, and skipped rows
- `--strict` can be used to fail immediately when any rows are skipped

## Why this matters

Legacy PURS scripts could skip problematic rows without leaving a structured record.
In a unified package, that makes debugging datasets and reproducing results much harder.

## Current output files

After `purs recognize`, users should expect:

- `ring_total_list.csv`
- `one_hot.csv`
- `number.csv`
- `adjacent_matrix.csv`
- `node_matrix.csv`
- `index_data.csv`
- `skipped_records.csv`
- `run_summary.json`

## Recommended next stability upgrades

1. Add a package-level schema note for common ID and SMILES columns.
2. Record whether a skip came from missing values, RDKit parse failure, or downstream unit canonicalization failure.
3. Add tests for invalid SMILES and duplicate-name inputs.
4. Normalize or map problematic legacy columns such as `No.` and `No` in one shared layer.
5. Extend reporting to downstream canonicalization failures, not only top-level parse failures.
