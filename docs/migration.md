# Migration Guide

## Goal

Move the legacy repositories into one package without losing compatibility or publication traceability.

## Recommended order

1. Move shared recognition code into `src/purs/core/`.
2. Move PUFp and baseline ML scripts into `src/purs/fingerprint/` and `src/purs/ml/`.
3. Move graph workflows into `src/purs/graph/`.
4. Convert legacy scripts into thin wrappers.
5. Move full paper workflows into `repro/`.

## Mapping from legacy repositories

### `Python-based-polymer-unit-recognition-script-PURS-for-PUFp`

- `get-polymer-unit.py` -> `purs.core.recognize`
- `polymer-unit-classify.py` -> `purs.core.classify`
- `structure_identity_tool.py` -> `purs.core` support modules

### `PUFp-for-OPV-materials`

- `RF.py` -> `purs.ml.rf`
- `KRR.py` -> `purs.ml.krr`
- `SVM.py` -> `purs.ml.svm`
- `ml_common.py` -> `purs.ml.common`

### `PURS-for-PU-graph`

- `PURS.py` shared logic -> `purs.core`
- `pu-gn-exp` -> `purs.graph.pu_gn_exp`
- `pu-mpnn` -> `purs.graph.pu_mpnn`

## Compatibility policy

During transition:

- keep old script names as wrappers
- keep output file names stable
- document any changed parameter names
