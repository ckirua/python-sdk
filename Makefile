PYTHON := python
PIP := pip
PACKAGES := sdk
TEST_DIR := tests
.DEFAULT_GOAL := help

.PHONY: build clean


help:
	@echo "Welcome to the SDK Makefile"
	@echo "Available commands:"
	@echo "  help       - Show this help message"
	@echo "  build      - Build the package"
	@echo "  clean      - Clean the build and dist directories"
	@echo "  install    - Install the package"
install:
	@$(PIP) install -e .

build:
	@$(PYTHON) setup.py build_ext --inplace

clean:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@find . -type f -name "*.so" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +

test:
	@$(PYTHON) -m unittest discover -s $(TEST_DIR) -p "test_*.py" -v