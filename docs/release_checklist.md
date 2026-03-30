# Release Checklist

## Before tagging a release

For a publishable package, prioritize example-based validation first.

1. Review the top-level README and `examples/README.md`.
2. Run one `PURS` example from `examples/basic_recognition/` or `examples/opecm_demo/`.
3. Run one `PUFp + ML` example from `examples/pufp_mobility_demo/`.
4. Run one `PUGraph` example from `examples/pugraph_demo/`.
5. Verify the example READMEs match the current commands and file names.
6. Review `environment-core.yml`, `environment-ml.yml`, `environment-graph.yml`, and `environment-all.yml`.
7. Review docs linked from the top-level README.
8. Confirm legacy wrappers still exist if backward compatibility is required.
9. Update citations and changelog if scientific scope changed.

## Optional internal validation

Internal regression tests can still be run before a release if desired.

If `pytest` is not installed, use:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py"
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p "test_*.py"
```

## Optional smoke command

```powershell
python scripts/run_smoke_release.py
```

This smoke path is mainly for maintainers. It is not required as the primary package entry point.
