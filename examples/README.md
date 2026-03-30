# Examples

This directory is the main user-facing entry for the package.

If you want to understand or validate the published software package, start here instead of
starting from `tests/` or internal smoke scripts.

The standard package sample dataset behind the public example is:

- `data/testing/opecm_paper54_tasks.csv`

## Public example

1. `opecm_standard_demo/`
   - single release-facing package example
   - uses one standard master sample table
   - covers `PURS`, `PUFp`, and `PUGraph` through one coherent workflow

## Supplementary examples

Supplementary workflow slices are now stored under:

- `repro/supplementary_examples/`

- `basic_recognition/`
  - smallest direct `PURS` check
  - kept for maintenance and focused demonstration

- `pufp_mobility_demo/`
  - small `PUFp + ML` mobility example
  - kept as a focused workflow slice

- `pugraph_demo/`
  - small graph-input example
  - kept as a focused workflow slice

- `opecm_demo/`
  - small real-data subset derived from OPECM
  - kept as supplementary reference material

- `pufp_opv_demo/`
  - legacy OPV-style example layout
  - kept for compatibility and method mapping

## Design rules

- examples should stay lightweight
- each example should have its own README and runnable command
- examples are intended for package understanding and release demos
- large maintenance checks belong in `tests/` or internal scripts, not here
