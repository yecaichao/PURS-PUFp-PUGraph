# Release Checklist

## Before tagging a release

For a publishable package, prioritize example-based validation first.

1. Review the top-level README and `examples/README.md`.
2. Run the public standard demo from `examples/opecm_standard_demo/`.
3. If needed, run one focused supplementary workflow slice.
4. Verify the example READMEs match the current commands and file names.
5. Review `environment-core.yml`, `environment-ml.yml`, `environment-graph.yml`, and `environment-all.yml`.
6. Review docs linked from the top-level README.
7. Confirm legacy wrappers still exist if backward compatibility is required.
8. Update citations and changelog if scientific scope changed.

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
