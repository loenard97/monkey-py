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

lint:
	flake8
	mypy pymonkey tests

build:
	.$(PYTHON) -m setup build
	pip install -e .
