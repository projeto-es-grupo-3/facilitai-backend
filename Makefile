VENV?=.venv
PYTHON=$(VENV)/bin/python3
PYTEST=$(VENV)/bin/pytest
PIP=$(PYTHON) -m pip
FLASK=$(PYTHON) -m flask

help:
	@echo "make [ venv | run | test | deploy ]"

venv:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Starting virtual environment..."
	. $(VENV)/bin/activate

run: venv
	$(FLASK) --app src.main run
