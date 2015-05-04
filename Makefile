# Shell to use with Make
SHELL := /bin/sh

# Set important Paths
PROJECT := elmr
LOCALPATH := $(CURDIR)/$(PROJECT)
PYTHONPATH := $(LOCALPATH)/
PYTHON_BIN := $(VIRTUAL_ENV)/bin

# Export targets not associated with files
.PHONY: test showenv coverage bootstrap pip virtualenv clean ingest

# Run the development server
runserver:
	$(PYTHON_BIN)/python $(CURDIR)/bin/elmr-admin.py runserver

# Ingest data from BLS
ingest:
	$(PYTHON_BIN)/python $(CURDIR)/bin/elmr-admin.py ingest

# Clean build files
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	-rm -rf htmlcov
	-rm -rf .coverage
	-rm -rf build
	-rm -rf dist
	-rm -rf $(PROJECT)/*.egg-info

# Targets for testing the app
test:
	ELMR_SETTINGS=testing $(PYTHON_BIN)/nosetests -v --with-coverage --cover-package=$(PROJECT) --cover-inclusive --cover-erase tests
