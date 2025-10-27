# Development Setup Guide

This guide will help you set up a local development environment for contributing to pretty-sitter. Follow these steps to get your development environment ready for making changes, running tests, and contributing to the project.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.11 or higher** - pretty-sitter requires Python 3.11+
- **Git** - For version control and cloning the repository
- **pip** - Python package installer (usually comes with Python)

You can verify your Python version with:

```bash
python --version
# or
python3 --version
```

## Getting the Source Code

1. **Fork the repository** on GitHub (if you plan to contribute)
2. **Clone your fork** (or the main repository):

```bash
# If you forked the repository
git clone https://github.com/YOUR_USERNAME/pretty-sitter.git

# Or clone the main repository directly
git clone https://github.com/antonioan/pretty-sitter.git
```

3. **Navigate to the project directory**:

```bash
cd pretty-sitter
```

## Setting Up the Development Environment

### Option 1: Using Virtual Environment (Recommended)

Create and activate a virtual environment to isolate your development dependencies:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Option 2: Using conda

If you prefer conda for environment management:

```bash
# Create a new conda environment
conda create -n pretty-sitter python=3.11

# Activate the environment
conda activate pretty-sitter
```

## Installing Dependencies

Once your environment is activated, install the project in development mode with all dependencies:

```bash
# Install the package in editable mode with development dependencies
pip install -e .[dev]

# Install documentation dependencies (optional, for building docs)
pip install -e .[docs]
```

This will install:
- The pretty-sitter package in editable mode
- All runtime dependencies (tree-sitter)
- Development dependencies (pytest, tree-sitter-python, tree-tagger)
- Documentation dependencies (mkdocs, mkdocs-material, etc.)

## Verifying Your Installation

Test that everything is working correctly:

```bash
# Run the test suite
pytest

# Test importing the package
python -c "from pretty_sitter import PrettySitter; print('Installation successful!')"
```

## Development Workflow

### Running Tests

pretty-sitter uses pytest for testing. Run tests with:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_pretty_sitter.py

# Run tests with coverage report
pytest --cov=pretty_sitter
```

### Code Quality Tools

The project uses several tools to maintain code quality:

#### Ruff (Linting and Formatting)

Ruff is configured in `pyproject.toml` and handles both linting and code formatting:

```bash
# Check for linting issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

#### Type Checking

The project supports multiple type checkers:

```bash
# Using mypy
mypy pretty_sitter/

# Using pyright (if installed)
pyright pretty_sitter/
```

#### Security Scanning

Use bandit for security analysis:

```bash
# Install bandit if not already installed
pip install bandit

# Run security scan
bandit -r pretty_sitter/
```

### Building Documentation

To build and serve the documentation locally:

```bash
# Install documentation dependencies
make docs-install

# Serve documentation locally (with auto-reload)
make docs-serve

# Build documentation for production
make docs-build

# Clean built documentation
make docs-clean
```

The documentation will be available at `http://localhost:8000` when serving locally.

## Project Structure

Understanding the project structure will help you navigate the codebase:

```
pretty-sitter/
├── pretty_sitter/           # Main package source code
│   ├── __init__.py         # Package initialization
│   ├── pretty_sitter.py    # Main PrettySitter class
│   ├── colorer.py          # Color management system
│   └── config.py           # Configuration classes
├── tests/                  # Test suite
│   └── test_pretty_sitter.py
├── docs/                   # Documentation source
│   ├── getting-started/    # User guides
│   ├── guides/            # Advanced guides
│   ├── reference/         # API reference
│   ├── troubleshooting/   # Help and FAQ
│   └── contributing/      # Contribution guides
├── scripts/               # Utility scripts
│   ├── serve-docs.py      # Documentation server
│   └── validate-docs.py   # Documentation validation
├── pyproject.toml         # Project configuration
├── Makefile              # Build automation
└── README.md             # Project overview
```

## Making Changes

### Before You Start

1. **Create a new branch** for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

2. **Make sure tests pass** before making changes:

```bash
pytest
```

### Development Process

1. **Make your changes** to the source code
2. **Add or update tests** as needed
3. **Run the test suite** to ensure nothing is broken:

```bash
pytest
```

4. **Run code quality checks**:

```bash
ruff check .
ruff format .
```

5. **Update documentation** if your changes affect the API or user experience

6. **Commit your changes** with a descriptive message:

```bash
git add .
git commit -m "Add feature: description of your changes"
```

### Testing Your Changes

#### Unit Tests

Write unit tests for new functionality in the `tests/` directory. Follow the existing test patterns:

```python
import pytest
from pretty_sitter import PrettySitter
from pretty_sitter.config import UIConfig

def test_your_feature():
    ps = PrettySitter()
    # Your test code here
    assert expected_result == actual_result
```

#### Integration Tests

Test your changes with real tree-sitter parse trees:

```python
def test_integration_with_real_code():
    # Use the existing fixtures or create new ones
    code = "def hello(): pass"
    tree = parser.parse(bytes(code, "utf8"))
    ps = PrettySitter()
    # Test that your changes work with real parse trees
```

#### Manual Testing

Test your changes manually with different configurations:

```python
from pretty_sitter import PrettySitter
from pretty_sitter.config import UIConfig, FilterConfig

# Test with various configurations
ps = PrettySitter(
    UIConfig(with_text=False),
    FilterConfig(only_types=['function_definition'])
)
```

## Troubleshooting

### Common Issues

#### Import Errors

If you get import errors, make sure you've installed the package in editable mode:

```bash
pip install -e .[dev]
```

#### Tree-sitter Language Issues

If you encounter issues with tree-sitter languages:

```bash
# Make sure tree-sitter-python is installed
pip install tree-sitter-python
```

#### Test Failures

If tests fail after your changes:

1. Check that you haven't broken existing functionality
2. Update tests if you've changed the API
3. Add new tests for new functionality

#### Documentation Build Issues

If documentation fails to build:

```bash
# Install documentation dependencies
pip install -e .[docs]

# Check for syntax errors in markdown files
make docs-build
```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting documentation](../troubleshooting/common-issues.md)
2. Search existing [GitHub issues](https://github.com/antonioan/pretty-sitter/issues)
3. Create a new issue with detailed information about your problem
4. Join the [discussions](https://github.com/antonioan/pretty-sitter/discussions) for community support

## Next Steps

Once your development environment is set up:

1. Read the [coding standards](coding-standards.md) to understand the project's style guidelines
2. Review the [architecture documentation](architecture.md) to understand the system design
3. Check out the [open issues](https://github.com/antonioan/pretty-sitter/issues) to find something to work on
4. Read the [pull request guidelines](../contributing/pull-request-guidelines.md) before submitting your first contribution

Happy coding! 🚀