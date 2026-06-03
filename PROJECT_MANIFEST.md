# Project Manifest

## Core runnable commands

```bash
make run-demo
make test
make reports
make audit
```

## Evidence artifacts to review first

1. `reports/feature_store_validation_report.md`
2. `reports/baseline_vs_specialty_ablation_report.md`
3. `reports/model_selection_report.md`
4. `reports/stress_test_report.md`
5. `reports/validation_memo.md`
6. `reports/release_decision.md`
7. `reports/data_quality_and_backfill_report.md`
8. `reports/model_monitoring_baseline_report.md`
9. `reports/explainability_report.md`
10. `reports/batch_scoring_contract_report.md`
11. `reports/local_github_runnable_audit.md`

## Claim boundaries

The repository is a local-runnable, AWS-patterned reference framework. It does not claim proprietary bank data, JPMorgan Chase data, production fraud deployment, or actual AWS EMR/SageMaker execution unless those runs are performed separately and logs are added.

- `reports/github_local_runnable_final_verification.md`: final local/GitHub runnable verification notes.
- `pyproject.toml`: Python project metadata and pytest configuration.
- `.github/workflows/local-ci.yml`: CI scaffold running demo, tests, reports, and audit.
