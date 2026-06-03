# Hardening Loop Report

## Loop 1: Operating-model selection

Weakness: the earlier version selected a model mainly by PR-AUC, which can underrepresent fraud-review operations.

Improvement: added a champion/challenger selection rule that balances PR-AUC, Precision@review capacity, fraud-loss capture, and calibration. Downstream specialty modules now start from the operating champion.

## Loop 2: Reliability and drift evidence

Weakness: drift and robustness checks existed conceptually but were not first-class generated evidence.

Improvement: added temporal PSI drift monitoring and small-data stress tests for amount shocks, score compression drift, and envelope-pruning contribution.

## Loop 3: Data quality, backfill, and monitoring hardening

Weakness: the previous version validated point-in-time features and parity, but it did not create a first-class data-quality baseline or idempotent backfill evidence.

Improvement: added `reports/data_quality_and_backfill_report.md`, `outputs/data_quality_baseline.json`, and `outputs/backfill_idempotence.json` to verify null rates, duplicates, source coverage, amount sanity, and deterministic reruns.

## Loop 4: Explainability and batch-scoring contract

Weakness: the model registry recorded metrics and lineage, but model-review evidence was still thin around feature attribution and downstream scoring contracts.

Improvement: added local permutation-importance diagnostics, a Model-Monitor-style baseline, and a batch scoring sample with approve/review/escalate decision mapping.

## Loop 5: Local/GitHub runnable hygiene

Weakness: runnable claims needed an explicit audit artifact.

Improvement: added `scripts/local_runnable_audit.py`, `reports/local_github_runnable_audit.md`, and GitHub Actions workflow scaffolding.

## Stop condition

Remaining improvements are either environment-dependent, such as actual AWS EMR/SageMaker execution, or data-dependent, such as full public benchmark runs. Further changes without those external resources would be minor relative to the current local-runnable scope.
