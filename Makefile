PYTHON ?= python

.PHONY: install typecheck lint format test package clean

install:
	$(PYTHON) -m pip install -e ".[dev]"

typecheck:
	$(PYTHON) -m mypy src

lint:
	$(PYTHON) -m ruff check src tests

format:
	$(PYTHON) -m ruff format src tests

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

package:
	$(PYTHON) -m build

clean:
	rm -rf build dist
