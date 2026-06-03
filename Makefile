.PHONY: run-demo test reports audit clean smoke verify dist-clean

run-demo:
	python scripts/run_demo.py --sample-mode

test:
	python -m pytest -q

reports:
	python scripts/generate_reports.py

audit:
	python scripts/local_runnable_audit.py

smoke: run-demo test reports audit

verify: clean run-demo test reports audit

clean:
	rm -rf outputs/* data/feature_store_offline/* data/online_store/* data/model_registry/* models/* reports/*.generated.md
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache

dist-clean: clean
	rm -rf .venv .mypy_cache .ruff_cache build dist *.egg-info
