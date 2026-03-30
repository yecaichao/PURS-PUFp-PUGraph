# Architecture

## Core idea

The package is organized around one shared scientific core and two downstream branches:

`polymer SMILES -> PURS core -> PUFp / PUGraph -> downstream learning`

## Layer boundaries

### `purs.core`

Owns:

- data loading
- name and column normalization
- SMILES cleanup
- polymer-unit recognition
- polymer-unit classification
- standardized outputs

### `purs.fingerprint`

Owns:

- PUFp feature creation
- feature-table level transformations

### `purs.ml`

Owns:

- traditional machine learning baselines
- shared feature/target alignment
- plotting and metrics helpers

### `purs.graph`

Owns:

- graph dataset construction
- graph model integration
- graph-specific preprocessing and configs

## Data separation

- `examples/`: user demos
- `tests/fixtures/`: automated validation data
- `repro/`: publication-scale workflows

These should not be mixed.

## Migration rule

If code is duplicated across legacy repositories, it should be moved into `purs.core` unless it is clearly specific to ML or graph workflows.
