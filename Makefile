.PHONY: all clean activate test lint build install

VENV 	= /venv
PYTHON	= $(VENV)/bin/python

INSTDIR	= /usr/local/bin/monkey

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

build:
	python pyinstaller.py

install: build
	sudo mkdir -p $(INSTDIR)
	sudo cp ./dist/monkey $(INSTDIR)
	sudo chmod +x $(INSTDIR)/monkey

test:
	pytest

fmt:
	isort .
	black .
	flake8 .
	mypy .
	
build:
	.$(PYTHON) pyinstaller.py
