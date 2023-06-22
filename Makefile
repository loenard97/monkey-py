.PHONY: all clean activate test lint build

VENV 	= /venv
PYTHON	= $(VENV)/bin/python

all:
	@echo "Possible make options:"
	@echo "clean    remove build files"
	@echo "build    build and install package"
	@echo "test     run all tests"
	@echo "lint     run all linters"

clean:
	rm -rf build/
	rm -rf pytest_cache/
	rm -rf pymonkey.egg-info/

activate:
	source $(VENV)/bin/activate

test:
	pytest

fmt:
	isort pymonkey/ tests/ *.py --multi-line 3 --profile black
	black pymonkey/ tests/ *.py
	flake8 --config .flake8
	mypy pymonkey/ tests/ *.py
	

lint:
	flake8
	mypy pymonkey tests

build:
	.$(PYTHON) -m setup build
	pip install -e .
