PYTHON ?= python

.PHONY: install typecheck lint format test integration-test check package release clean

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

integration-test:
	PYTHONPATH=src $(PYTHON) scripts/integration_test.py

check:
	$(MAKE) lint PYTHON=$(PYTHON)
	$(MAKE) typecheck PYTHON=$(PYTHON)
	$(MAKE) test PYTHON=$(PYTHON)

package: clean
	$(PYTHON) -m build

release:
	$(PYTHON) scripts/release.py --python "$(PYTHON)"

clean:
	rm -rf build dist .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
