PYTHON = python3
PIP = pip
MAIN_SCRIPT = a_maze_ing.py
CONFIG_FILE = config.txt

.PHONY: all install run debug clean lint lint-strict build

all: run

install:
	$(PIP) install -r requirements.txt
	
run:
	$(PYTHON) $(MAIN_SCRIPT) $(CONFIG_FILE)

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE)

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache *.egg-info dist build maze.txt venv */.mypy_cache */.pytest_cache */*.egg-info */dist */build

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .
lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy --strict .

build:
	$(PYTHON) -m build
	mv dist/*.whl .
	make clean