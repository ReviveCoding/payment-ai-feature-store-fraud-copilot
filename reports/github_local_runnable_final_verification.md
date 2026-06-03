# Final Local / GitHub Runnable Verification

This final pass tightened the repository for local and GitHub execution.

## Fixes applied

- Added `pyproject.toml` with build metadata and pytest configuration.
- Updated `Makefile` with `verify` and `dist-clean` targets.
- Updated `clean` to remove Python bytecode caches and `.pytest_cache`.
- Updated GitHub Actions workflow to run `make run-demo`, `make test`, `make reports`, and `make audit`.
- Strengthened `scripts/local_runnable_audit.py` to report cache directories as warning-only and to fail on missing CI workflow checks, large files, secret-like filenames, or missing required files.

## Expected local commands

```bash
make run-demo
make test
make reports
make audit
make verify
```

## Claim boundary

This repository remains local-runnable, AWS-patterned, EMR-compatible, and SageMaker-compatible. It does not claim production AWS execution, proprietary bank data, JPMorgan Chase data, or a production fraud system.

## Final compatibility fix

- Applied a Pandas 3.x compatibility fix in `src/monitoring/data_quality.py` by replacing `np.issubdtype` checks on extension dtypes with `pandas.api.types.is_datetime64_any_dtype`.

- Added a tabulate-free markdown renderer fallback in `src/reporting.py` so `make run-demo` works from minimal dependencies even when pandas optional `tabulate` is absent.
