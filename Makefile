help:
	@echo "make [ venv | run | test | deploy ]"


setup-poetry:
	pip install poetry

venv: setup-poetry
	poetry install
	pip install --upgrade pip
	pip install -e src/

run:
	poetry run flask --app src.main.main run

test:
	poetry run pytest
