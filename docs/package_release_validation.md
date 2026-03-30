# Package Release Validation

This document records a practical package-level validation pass for the unified
`PURS-PUFp-PUGraph` repository.

The goal is not full paper reproduction.
The goal is to confirm that the packaged examples and the main wrapped workflows are runnable and
coherent before release.

## Validation environment

- Python executable:
  - `C:\miniconda\envs\purs-review-py39\python.exe`
- Working tree:
  - `PURS-PUFp-PUGraph`

## Recommended release-facing examples

1. `examples/opecm_standard_demo/`

This is the intended public package entry point.
Internal `tests/` and smoke scripts are retained for maintenance, but they are not the main
release story.

## Validated package paths

### 1. PUFp example path

Validated through:

- `PUFp + Features + Descriptors` baseline runs on OPECM-derived OSC subsets
- paper54-style classification benchmark
- package-level standard sample table `data/testing/opecm_paper54_tasks.csv`
- release-facing `repro/supplementary_examples/pufp_mobility_demo/` run

Key result files:

- `output/feature_fusion_ue/summary.json`
- `output/feature_fusion_uh/summary.json`
- `output/paper54_classification_baseline/summary.json`
- `output/paper54_classification_baseline/carrier_type_model_comparison.csv`
- `output/paper54_classification_baseline/mobility_class3_model_comparison.csv`
- `output/release_final_pufp/run_summary.json`

### 2. PUGraph example path

Validated on:

- `repro/supplementary_examples/pugraph_demo/input.csv`
- data derived from the standard master sample table `data/testing/opecm_paper54_tasks.csv`

Executed commands:

```powershell
$env:PYTHONPATH='src'
python -m purs.cli graph build --input-csv repro/supplementary_examples/pugraph_demo/input.csv --output-dir output/release_graph_demo
python -m purs.cli graph train --config output/release_graph_demo/pu_gn_exp_train.yaml
python -m purs.cli graph train --config output/release_graph_demo/pu_mpnn_train.yaml
python -m purs.cli graph train --config output/release_graph_demo/pu_gn_exp_train_execute.yaml
python -m purs.cli graph train --config output/release_graph_demo/pu_mpnn_train_execute.yaml
```

Observed results:

- `graph build` completed
- `PU-gn-exp` completed in `command_only`
- `PU-MPNN` completed in `command_only`
- `PU-gn-exp` completed in `execute`
- `PU-MPNN` completed in `execute`

Key result files:

- `output/release_graph_demo/graph_input.csv`
- `output/release_graph_demo/graph_dataset_manifest.json`
- `output/release_graph_demo/graph_build_manifest.json`
- `output/release_graph_demo/pu_gn_exp_train.yaml`
- `output/release_graph_demo/pu_mpnn_train.yaml`
- `output/release_graph_demo/runs/pu_gn_exp/metrics_summary.json`
- `output/release_graph_demo/runs/pu_gn_exp/val_predictions.csv`
- `output/release_graph_demo/runs/pu_gn_exp/model.latest.pt`
- `output/release_graph_demo/pu_mpnn/genwl3.pkl`
- `output/release_graph_demo/pu_mpnn/release_check.csv`
- `output/release_final_graph/graph_input.csv`
- `output/release_final_graph/runs/pu_gn_exp/metrics_summary.json`
- `output/release_final_graph/pu_mpnn/genwl3.pkl`

### 3. Unified example runner

The repository also keeps a unified package example runner:

```powershell
$env:PYTHONPATH='src'
python scripts/run_opecm_osc_unified_example.py --output-dir output/opecm_osc_unified_example
```

This runner is helpful for maintainers because it combines:

- paper54-style classification summary
- PUFp regression quick baselines
- graph build checks for `ue` and `uh`
- wrapped graph config validation
- one shared standard sample table as the input source

Key result file:

- `output/opecm_osc_unified_example/summary.json`

### 4. Current release-facing sample run

The current release-facing example pass is centered on
`examples/opecm_standard_demo/`, using `data/testing/opecm_paper54_tasks.csv` as the single public
sample source.

Observed results:

- unified standard-demo runner completed from the master table
- focused workflow slices were also rerun successfully during release preparation:
  - `basic_recognition`
  - `pufp_mobility_demo`
  - `pugraph_demo`

Key result files:

- `output/opecm_osc_unified_example_master/summary.json`
- `output/release_final_basic/run_summary.json`
- `output/release_final_pufp/run_summary.json`
- `output/release_final_graph/graph_build_manifest.json`
- `output/release_final_graph/runs/pu_gn_exp/metrics_summary.json`
- `output/release_final_graph/pu_mpnn/release_check.csv`

### 5. Current automated validation

The full unit test suite has also been rerun in the prepared review environment:

- command:
  - `C:\miniconda\envs\purs-review-py39\python.exe -m unittest discover -s tests -p "test_*.py"`
- result:
  - `31/31` tests passed

## Practical conclusion

At the package level, the repository is currently validated for release in this sense:

- examples are present and documented
- `PUFp` example workflows run
- `PUGraph` example workflows run
- wrapped graph backends can be exercised through both `command_only` and `execute`

This is sufficient for a release whose primary goal is:

- a clear unified package structure
- coherent sample datasets
- documented runnable examples

It is not presented as an exact numerical reproduction of the source papers.
