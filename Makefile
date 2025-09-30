.PHONY: install run test clean format type-check docs docs-serve docs-build

install:
	poetry install

run:
	poetry run streamlit run app.py

test:
	poetry run pytest tests/

format:
	poetry run black rxflow/ tests/ app.py --line-length 88
	poetry run isort rxflow/ tests/ app.py --profile black

type-check:
	poetry run mypy rxflow/ --ignore-missing-imports --show-error-codes

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	pip install -r requirements-docs.txt
	mkdocs serve

docs-serve:
	mkdocs serve --dev-addr 127.0.0.1:8000

docs-build:
	pip install -r requirements-docs.txt
	mkdocs build
