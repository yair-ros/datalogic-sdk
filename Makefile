PYTHON ?= python

.PHONY: install typecheck lint format test package release clean

install:
	$(PYTHON) -m pip install -e ".[dev]"

typecheck:
	$(PYTHON) -m mypy src scripts

lint:
	$(PYTHON) -m ruff check src tests scripts

format:
	$(PYTHON) -m ruff format src tests scripts

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

package:
	$(PYTHON) -m build

release:
	$(PYTHON) scripts/release.py --python "$(PYTHON)"

clean:
	rm -rf build dist
