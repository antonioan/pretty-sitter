# Pretty Sitter Documentation Makefile

.PHONY: help docs-install docs-serve docs-build docs-clean docs-validate docs-lint docs-check-examples

help:
	@echo "Available commands:"
	@echo "  docs-install       Install documentation dependencies"
	@echo "  docs-serve         Serve documentation locally for development"
	@echo "  docs-build         Build documentation for production"
	@echo "  docs-clean         Clean built documentation"
	@echo "  docs-validate      Validate documentation structure and configuration"
	@echo "  docs-lint          Run comprehensive documentation linting"
	@echo "  docs-check-examples Validate code examples in documentation"

docs-install:
	pip install -e .[docs]

docs-serve:
	python scripts/serve-docs.py

docs-build:
	mkdocs build --strict

docs-clean:
	rm -rf site/docs-val
idate:
	python scripts/validate-docs.py

docs-lint:
	python scripts/lint-docs.py --verbose

docs-check-examples:
	python scripts/validate-code-examples.py --verbose --fail-on-error

docs-lint-ci:
	python scripts/lint-docs.py --fail-on-error --output lint-results.json