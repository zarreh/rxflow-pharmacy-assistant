.PHONY: install run test clean

install:
	poetry install

run:
	poetry run streamlit run app.py

test:
	poetry run pytest tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
