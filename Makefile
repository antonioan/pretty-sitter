# Pretty Sitter Documentation Makefile

.PHONY: help docs-install docs-serve docs-build docs-clean

help:
	@echo "Available commands:"
	@echo "  docs-install  Install documentation dependencies"
	@echo "  docs-serve    Serve documentation locally for development"
	@echo "  docs-build    Build documentation for production"
	@echo "  docs-clean    Clean built documentation"

docs-install:
	pip install -e .[docs]

docs-serve:
	python scripts/serve-docs.py

docs-build:
	mkdocs build --strict

docs-clean:
	rm -rf site/