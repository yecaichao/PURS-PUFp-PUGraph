# Publish Status

## Ready now

- unified repository layout
- runnable `purs recognize`, `purs classify`, `purs fingerprint`
- runnable `purs ml rf|krr|svm`
- wrapped `purs graph build` and `purs graph train`
- integrated OPECM dataset structure
- explicit skipped-record and run-summary reporting
- lightweight automated regression tests
- split conda environment files
- architecture, schema, stability, graph, and release documentation

## Still worth improving before a broader public release

1. Replace more legacy graph-internal PURS code with unified package modules.
2. Refine citation and authorship sections.
3. Review `pyproject.toml` metadata such as license and authors.
4. Decide whether to keep large dataset files inside the main repository or distribute them separately.
5. Add more regression tests around graph preprocessing and strict-mode behavior.

## Practical assessment

The repository is already strong enough for:

- internal lab use
- shared development with students or collaborators
- controlled early release

For a polished public release, the remaining work is mostly cleanup and presentation, not core architecture.
