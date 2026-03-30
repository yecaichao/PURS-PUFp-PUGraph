# Examples

This directory is the main user-facing entry for the package.

If you want to understand or validate the published software package, start here instead of
starting from `tests/` or internal smoke scripts.

The standard package sample dataset behind the mobility and graph examples is:

- `data/testing/opecm_paper54_tasks.csv`

## Recommended order

1. `basic_recognition/`
   - smallest `PURS` example
   - best first check that the package is installed correctly

2. `pufp_mobility_demo/`
   - small `PUFp + ML` mobility example
   - recommended package-level example for the fingerprint workflow

3. `pugraph_demo/`
   - small graph-input example
   - recommended package-level example for `PUGraph`

These three examples are the public, release-facing example suite.

## Supplementary examples

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
