VENV?=.venv
PYTHON=$(VENV)/bin/python3
PYTEST=$(VENV)/bin/pytest
PIP=$(PYTHON) -m pip
FLASK=$(PYTHON) -m flask
SHELL := /bin/bash

help:
	@echo "make [ venv | run | test | deploy ]"

venv:
	@echo "Starting virtual environment..."
	python3 -m venv .venv
	@echo "Installing requirements..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: venv
	$(FLASK) --app src.main run
