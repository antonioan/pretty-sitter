# API Reference

Complete reference documentation for all Pretty Sitter classes, methods, and configuration options.

## Core API

- **[PrettySitter](api/pretty-sitter.md)** - Main class for pretty printing parse trees
- **[Colorer](api/colorer.md)** - Color system and brush management
- **[Config](api/config.md)** - Configuration classes and options

## Configuration Reference

- **[Configuration Options](configuration-options.md)** - Comprehensive guide to all configuration parameters

## Quick Reference

### Essential Classes

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `PrettySitter` | Main pretty printing interface | `pprint()`, `configure()` |
| `Colorer` | Color and styling management | `color()`, `uncolor()` |
| `UIConfig` | User interface configuration | Display and formatting options |
| `FilterConfig` | Node filtering configuration | Include/exclude patterns |
| `MarkingConfig` | Node marking configuration | Highlighting and emphasis |

### Common Configuration Patterns

```python
# Basic configuration
config = UIConfig(show_line_numbers=True, indent_size=2)

# Color configuration  
colorer = Colorer(theme="dark")

# Filtering configuration
filter_config = FilterConfig(include_types=["function_definition"])
```

## Type Hints and Annotations

All public APIs include complete type hints for better IDE support and type checking. See individual class documentation for detailed type information.

## Version Compatibility

This documentation covers Pretty Sitter version 0.0.1. For information about API changes between versions, see the project's changelog.