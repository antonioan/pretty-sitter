# Documentation Scripts

This directory contains scripts for managing and validating the pretty-sitter documentation.

## Available Scripts

### Documentation Serving and Building

- **`serve-docs.py`** - Serve documentation locally for development
- **`validate-docs.py`** - Validate documentation structure and MkDocs configuration

### Quality Assurance Scripts

- **`validate-code-examples.py`** - Extract and validate Python code examples from documentation
- **`lint-docs.py`** - Comprehensive documentation linting (combines all validation tools)
- **`install-lint-tools.py`** - Install required Node.js linting tools

## Usage

### Quick Start

```bash
# Install linting tools (one-time setup)
python scripts/install-lint-tools.py

# Run comprehensive documentation linting
python scripts/lint-docs.py --verbose

# Or use Make targets
make docs-lint
make docs-validate
make docs-check-examples
```

### Individual Tools

#### Code Example Validation

```bash
# Validate all code examples
python scripts/validate-code-examples.py --verbose

# Fail on errors (useful for CI)
python scripts/validate-code-examples.py --fail-on-error

# Validate specific directory
python scripts/validate-code-examples.py --docs-dir docs/guides
```

#### Comprehensive Linting

```bash
# Run all checks
python scripts/lint-docs.py --verbose

# Skip specific tools
python scripts/lint-docs.py --skip spelling links

# Save results to file
python scripts/lint-docs.py --output results.json

# Fail on any errors (for CI)
python scripts/lint-docs.py --fail-on-error
```

#### Documentation Structure Validation

```bash
# Validate docs structure and MkDocs config
python scripts/validate-docs.py
```

#### Serve Documentation Locally

```bash
# Start development server
python scripts/serve-docs.py

# Or use MkDocs directly
mkdocs serve
```

## Linting Tools

The documentation quality assurance system uses several tools:

### Python Tools (included)

- **Code Example Validation** - Custom script to extract and validate Python code from markdown
- **Documentation Structure** - Validates directory structure and MkDocs configuration

### Node.js Tools (require installation)

- **markdownlint** - Markdown style and formatting validation
- **cspell** - Spell checking for documentation
- **markdown-link-check** - Link validation

### Installation

Install Node.js tools automatically:

```bash
python scripts/install-lint-tools.py
```

Or install manually:

```bash
npm install -g markdownlint-cli cspell markdown-link-check
```

## Configuration Files

The linting system uses several configuration files:

- **`.markdownlint.json`** - Markdown linting rules
- **`.cspell.json`** - Spell checking configuration and word list
- **`.pre-commit-config.yaml`** - Pre-commit hooks for automatic validation

## CI/CD Integration

### GitHub Actions

The `.github/workflows/validate-docs.yml` workflow runs documentation validation on:

- Push to main/develop branches
- Pull requests affecting documentation
- Changes to validation scripts or configuration

### Pre-commit Hooks

Install pre-commit hooks to validate documentation before commits:

```bash
pip install pre-commit
pre-commit install
```

### Make Targets

Use Make targets for common tasks:

```bash
make docs-lint          # Comprehensive linting
make docs-validate      # Structure validation
make docs-check-examples # Code example validation
make docs-serve         # Serve locally
make docs-build         # Build documentation
```

## Troubleshooting

### Common Issues

1. **Node.js tools not found**

   ```bash
   python scripts/install-lint-tools.py
   ```

2. **Code examples failing validation**

   - Check that examples are valid Python syntax
   - Ensure required imports are available
   - Use `--verbose` flag to see detailed error messages

3. **Spell check failures**

   - Add new technical terms to `.cspell.json` words list
   - Use `ignoreRegExpList` for patterns that should be ignored

4. **Markdown linting failures**
   - Check `.markdownlint.json` for rule configuration
   - Common issues: line length, heading styles, list formatting

### Getting Help

- Run scripts with `--help` flag for detailed usage information
- Check the GitHub Actions logs for CI failures
- Review configuration files for customization options

## Development

### Adding New Validation Rules

1. **Code Examples**: Modify `validate-code-examples.py`

   - Update `_is_non_python_content()` to filter out non-Python content
   - Add new validation checks in `CodeExampleValidator`

2. **Markdown Linting**: Update `.markdownlint.json`

   - See [markdownlint rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)

3. **Spell Checking**: Update `.cspell.json`
   - Add words to the `words` array
   - Add patterns to `ignoreRegExpList`

### Testing Changes

```bash
# Test individual components
python scripts/validate-code-examples.py --verbose
python scripts/validate-docs.py

# Test comprehensive linting
python scripts/lint-docs.py --verbose

# Test with specific files
python scripts/validate-code-examples.py --docs-dir docs/guides
```
