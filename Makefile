# Shell to use with Make
SHELL := /bin/sh

# Set important Paths
PROJECT := web
LOCALPATH := $(CURDIR)/$(PROJECT)
PYTHONPATH := $(LOCALPATH)/
PYTHON_BIN := $(VIRTUAL_ENV)/bin

# Export targets not associated with files
.PHONY: test showenv coverage bootstrap pip virtualenv clean virtual_env_set

# Run the development server
runserver:
	@echo "Not implemented"

# Clean build files
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	-rm -rf htmlcov
	-rm -rf .coverage
	-rm -rf build
	-rm -rf dist
	-rm -rf $(PROJECT)/*.egg-info

# Targets for Django testing
test:
	$(PYTHON_BIN)/nosetests -v
