.PHONY: lint test pipeline sql dashboard dbt-seed dbt-run dbt-test dbt-docs generate-scale clean

# ── Quality ──────────────────────────────────────────────────────
lint:
	ruff check . --config pyproject.toml

test:
	pytest tests/ -v --tb=short

# ── Pipelines ────────────────────────────────────────────────────
pipeline:
	python pipeline.py

sql:
	python sql/run_sql_pipeline.py

dashboard:
	streamlit run dashboard.py

# ── dbt ──────────────────────────────────────────────────────────
dbt-seed:
	python dbt/load_source.py

dbt-run: dbt-seed
	cd dbt && dbt run --profiles-dir .

dbt-test:
	cd dbt && dbt test --profiles-dir .

dbt-docs:
	cd dbt && dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .

# ── Scale Testing ────────────────────────────────────────────────
generate-scale:
	python scripts/generate_scale_data.py

# ── Housekeeping ─────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf data/marts/*.csv data/processed/*.csv
