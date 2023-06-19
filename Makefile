help:
	@echo "make [ setup-poetry | venv | run | test | coverage ]"


setup-poetry:
	python3 -m pip install poetry

venv: setup-poetry
	poetry install
	poetry run pip install --upgrade pip
	poetry run pip install -e src/

run:
	poetry run flask --app src.main.main run

test:
	poetry run pytest

coverage:
	poetry run pytest --cov=src tests/ --cov-report html
