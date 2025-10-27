# Coding Standards and Guidelines

This document outlines the coding standards, style guidelines, and best practices for contributing to pretty-sitter. Following these guidelines ensures code consistency, maintainability, and quality across the project.

## Code Style and Formatting

### Python Style Guide

pretty-sitter follows [PEP 8](https://pep8.org/) with some project-specific modifications. We use automated tools to enforce consistent formatting and style.

#### Ruff Configuration

The project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting. The configuration is defined in `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # Pyflakes
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "I",    # isort
]
ignore = [
    "E501"  # line too long (handled by formatter)
]
```

#### Key Style Rules

- **Line length**: Maximum 100 characters (not the PEP 8 default of 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use double quotes for strings by default
- **Import sorting**: Imports are automatically sorted by Ruff
- **Trailing commas**: Use trailing commas in multi-line structures

#### Running Code Formatting

```bash
# Check for style issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

### Import Organization

Imports should be organized in the following order:

1. Standard library imports
2. Third-party library imports
3. Local application imports

```python
# Standard library
import os
import sys
from typing import Any, Optional

# Third-party
import tree_sitter
from tree_sitter import Node

# Local
from pretty_sitter.config import Config
from pretty_sitter.colorer import Colorer
```

## Type Hints and Documentation

### Type Annotations

All public functions and methods must include type hints:

```python
def process_node(node: Node, depth: int = 0) -> str:
    """Process a tree-sitter node and return formatted output."""
    return formatted_output

class PrettySitter:
    def __init__(self, *configs: Config) -> None:
        """Initialize with configuration objects."""
        pass
```

### Type Checking

The project supports multiple type checkers configured in `pyproject.toml`:

```bash
# Using mypy
mypy pretty_sitter/

# Using pyright
pyright pretty_sitter/
```

### Docstring Standards

All public classes, methods, and functions must have comprehensive docstrings following the [Google docstring style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings):

```python
def pprint(self, root: Node, *configs: Config) -> None:
    """Pretty print a tree-sitter parse tree node with optional configuration overrides.

    This is the main method for outputting formatted parse trees. It applies any
    temporary configuration overrides, performs environment checks, and renders
    the tree with appropriate formatting and colors.

    Args:
        root: The root Node of the parse tree to print. This can be any Node
             in the tree, not necessarily the actual root.
        *configs: Optional Config objects to temporarily override the current
                 configuration for this print operation only.

    Raises:
        subprocess.SubprocessError: If pager mode is enabled but the pager
                                   command fails to execute.

    Examples:
        Basic usage:

        >>> ps = PrettySitter()
        >>> ps.pprint(tree.root_node)

        With temporary configuration override:

        >>> ps.pprint(node, UIConfig(with_text=False))
    """
```

#### Docstring Requirements

- **Summary line**: One-line summary of what the function does
- **Extended description**: More detailed explanation if needed
- **Args**: Description of all parameters with types
- **Returns**: Description of return value and type
- **Raises**: Any exceptions that may be raised
- **Examples**: Code examples showing usage
- **Note/Warning**: Additional important information

## Code Organization and Architecture

### Class Design Principles

#### Single Responsibility Principle

Each class should have a single, well-defined responsibility:

- `PrettySitter`: Main interface for pretty printing
- `Colorer`: Color management and ANSI code handling
- `Config` classes: Configuration management for specific aspects

#### Composition Over Inheritance

Prefer composition and dependency injection:

```python
class PrettySitter:
    def __init__(self, *configs: Config):
        self._config = _CombinedConfig()
        self._colorer = Colorer(self._boldworthy)  # Composition
```

#### Immutability Where Possible

Use immutable data structures and avoid modifying objects in place:

```python
@dataclass(frozen=True)  # Immutable dataclass
class UIConfig(Config):
    with_text: bool = True
    indent_size: int = 4
```

### Method Design

#### Method Length

Keep methods focused and reasonably short (typically under 50 lines). If a method becomes too long, consider breaking it into smaller, focused methods:

```python
def _print_node(self, node: Node, attr_name: str | None = None, depth: int = 0) -> bool:
    """Print a single node - delegates to helper methods for complex logic."""
    if not self._printworthy(node):
        return self._handle_skipped_node(node, depth)
    
    return self._render_node(node, attr_name, depth)
```

#### Parameter Design

- Use keyword-only arguments for optional parameters when appropriate
- Provide sensible defaults
- Use type unions sparingly and prefer Optional[T] over Union[T, None]

```python
def configure(
    self, 
    *configs: Config,
    temporary: bool = False  # keyword-only
) -> Generator[None, None, None]:
```

## Error Handling

### Exception Handling

- Use specific exception types rather than catching all exceptions
- Provide meaningful error messages
- Document exceptions in docstrings

```python
def _apply_color(self, text: str, color: str) -> str:
    """Apply color to text.
    
    Args:
        text: Text to colorize
        color: Color name from COLOR_MAP
        
    Raises:
        ValueError: If color is not defined in COLOR_MAP
    """
    if color not in self.COLOR_MAP:
        raise ValueError(f"Unknown color '{color}'. Available: {list(self.COLOR_MAP.keys())}")
    
    return self._format_with_ansi(text, self.COLOR_MAP[color])
```

### Input Validation

Validate inputs early and provide clear error messages:

```python
def __init__(self, *configs: Config):
    """Initialize with configuration objects.
    
    Args:
        *configs: Configuration objects to apply
        
    Raises:
        TypeError: If any config is not a Config instance
    """
    for config in configs:
        if not isinstance(config, Config):
            raise TypeError(f"Expected Config instance, got {type(config)}")
```

## Testing Standards

### Test Organization

Tests are organized in the `tests/` directory with a structure that mirrors the source code:

```
tests/
├── test_pretty_sitter.py    # Main functionality tests
├── test_colorer.py          # Color system tests
├── test_config.py           # Configuration tests
└── conftest.py              # Shared fixtures
```

### Test Naming

Use descriptive test names that explain what is being tested:

```python
def test_pprint_with_filter_config_excludes_specified_types():
    """Test that FilterConfig properly excludes specified node types."""
    pass

def test_colorer_applies_bold_formatting_when_boldworthy_returns_true():
    """Test that Colorer applies bold formatting based on boldworthy function."""
    pass
```

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_pretty_sitter_respects_indent_size_configuration():
    # Arrange
    config = UIConfig(indent_size=2)
    ps = PrettySitter(config)
    node = create_test_node()
    
    # Act
    output = capture_output(lambda: ps.pprint(node))
    
    # Assert
    assert "  " in output  # 2-space indentation
    assert "    " not in output  # Not 4-space indentation
```

### Fixtures and Test Data

Use pytest fixtures for reusable test data:

```python
@pytest.fixture
def sample_python_code() -> str:
    return textwrap.dedent("""
    def hello(name: str) -> None:
        print(f"Hello, {name}!")
    """).strip()

@pytest.fixture
def parsed_tree(sample_python_code: str) -> Node:
    return parser.parse(bytes(sample_python_code, "utf8")).root_node
```

### Test Coverage

- Aim for high test coverage (>90%) but focus on meaningful tests
- Test both happy paths and error conditions
- Include integration tests with real tree-sitter parse trees
- Test configuration combinations and edge cases

```bash
# Run tests with coverage
pytest --cov=pretty_sitter --cov-report=html
```

## Performance Considerations

### Efficiency Guidelines

- Avoid unnecessary object creation in hot paths
- Use generator expressions where appropriate
- Cache expensive computations when possible

```python
# Good: Generator expression for memory efficiency
filtered_nodes = (node for node in nodes if self._printworthy(node))

# Good: Caching expensive operations
@functools.lru_cache(maxsize=128)
def _get_color_for_type(self, node_type: str) -> str:
    return self._compute_color(node_type)
```

### Memory Management

- Be mindful of memory usage when processing large parse trees
- Use context managers for resource management
- Avoid holding references to large objects longer than necessary

## Security Considerations

### Input Validation

- Validate all external inputs
- Be careful with string formatting and potential injection
- Use parameterized queries/commands where applicable

### Dependencies

- Keep dependencies minimal and well-maintained
- Regularly update dependencies for security patches
- Use tools like `bandit` for security scanning:

```bash
bandit -r pretty_sitter/
```

## Code Review Guidelines

### Before Submitting

1. **Run all quality checks**:
   ```bash
   ruff check .
   ruff format .
   pytest
   mypy pretty_sitter/
   ```

2. **Update documentation** if your changes affect the API
3. **Add or update tests** for new functionality
4. **Check that examples in docstrings work**

### Review Checklist

When reviewing code, consider:

- [ ] Code follows the established style guidelines
- [ ] All public APIs have comprehensive docstrings
- [ ] Tests cover the new functionality adequately
- [ ] Error handling is appropriate and informative
- [ ] Performance implications are considered
- [ ] Security implications are considered
- [ ] Documentation is updated if needed

### Review Process

1. **Automated checks** must pass before human review
2. **At least one maintainer** must approve changes
3. **All conversations** must be resolved before merging
4. **Squash and merge** is preferred for clean history

## Continuous Integration

### GitHub Actions

The project uses GitHub Actions for CI/CD with the following checks:

- **Linting and formatting** with Ruff
- **Type checking** with mypy
- **Testing** with pytest across multiple Python versions
- **Security scanning** with bandit
- **Documentation building** to ensure docs remain buildable

### Pre-commit Hooks

Consider setting up pre-commit hooks to catch issues early:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Documentation Standards

### Code Comments

- Use comments sparingly - prefer self-documenting code
- Explain *why* something is done, not *what* is done
- Update comments when code changes

```python
# Good: Explains why
# We need to sleep briefly to ensure the pager has time to start
# before we send it input, otherwise it may not display correctly
sleep(1)

# Bad: Explains what (obvious from code)
# Sleep for 1 second
sleep(1)
```

### API Documentation

- All public APIs must be documented
- Include examples in docstrings
- Keep documentation up to date with code changes
- Use type hints consistently

## Version Control

### Commit Messages

Use clear, descriptive commit messages following conventional commits:

```
feat: add support for custom color schemes
fix: resolve issue with pager not working on Windows
docs: update installation instructions for Python 3.11
test: add integration tests for FilterConfig
refactor: simplify color application logic
```

### Branch Naming

Use descriptive branch names:

- `feature/custom-color-schemes`
- `fix/pager-windows-issue`
- `docs/update-installation-guide`

## Deprecation Policy

When deprecating features:

1. **Add deprecation warnings** using Python's `warnings` module
2. **Update documentation** to mark features as deprecated
3. **Provide migration path** in the warning message
4. **Keep deprecated features** for at least one major version
5. **Remove deprecated features** in the next major version

```python
import warnings

def old_method(self):
    warnings.warn(
        "old_method is deprecated and will be removed in v2.0. "
        "Use new_method instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()
```

## Getting Help

If you have questions about the coding standards:

1. Check existing code for examples
2. Ask in the [GitHub discussions](https://github.com/antonioan/pretty-sitter/discussions)
3. Create an issue for clarification on specific guidelines
4. Reach out to maintainers for guidance

Remember: These guidelines exist to maintain code quality and consistency. When in doubt, prioritize readability and maintainability over strict adherence to rules.