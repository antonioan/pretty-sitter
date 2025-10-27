# Configuration Guide

Pretty-sitter provides a flexible configuration system that allows you to customize every aspect of the pretty printing output. This guide covers all available configuration classes, their options, and how to combine them effectively.

## Overview

Pretty-sitter uses a modular configuration system with five main configuration classes:

- **UIConfig**: Controls visual appearance and formatting
- **FilterConfig**: Determines which nodes to include or exclude
- **MarkingConfig**: Highlights specific nodes with colors and labels
- **TTYConfig**: Manages terminal and pager behavior
- **DebugConfig**: Enables debugging and diagnostic output

All configuration classes inherit from the base `Config` class and can be combined when initializing PrettySitter or used with the `configure()` context manager.

## UIConfig - Visual Formatting

The `UIConfig` class controls the visual appearance and layout of the pretty-printed parse tree output.

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `with_text` | bool | True | Display actual text content alongside node types |
| `with_trivial` | bool | False | Include trivial nodes (where type matches text) |
| `close_pars_early` | bool | True | Close parentheses early to reduce visual clutter |
| `print_with_color` | bool | True | Apply ANSI color codes to output |
| `color_legend` | bool | True | Display color legend when colors are enabled |
| `dotted` | bool | False | Use dotted lines for column alignment |
| `column_width` | int | 100 | Width of first column before text content |
| `indent_size` | int | 4 | Number of spaces per indentation level |

### Examples

#### Minimal Output Configuration
```python
from pretty_sitter import PrettySitter
from pretty_sitter.config import UIConfig

# Create minimal output without text content
config = UIConfig(
    with_text=False,
    with_trivial=False,
    color_legend=False
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Shows only the tree structure with node types, no text content or color legend.

#### Compact Formatting
```python
# Compact formatting with smaller indentation and column width
config = UIConfig(
    indent_size=2,
    column_width=50,
    close_pars_early=True
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Creates a more compact tree with less horizontal space usage.

#### Plain Text Output
```python
# Plain text output without colors for logging or documentation
config = UIConfig(
    print_with_color=False,
    color_legend=False
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Produces clean, uncolored output suitable for logs or text files.

#### Dotted Column Alignment
```python
# Use dotted lines for better column alignment visibility
config = UIConfig(
    dotted=True,
    column_width=80
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Adds dotted lines between the tree structure and text content for clearer visual separation.

## FilterConfig - Node Filtering

The `FilterConfig` class provides options to include or exclude specific node types from the output.

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `excluded_types` | list[str] \| None | None | Node types to exclude from output |
| `only_types` | list[str] \| None | None | Only include these node types (and children) |

### Filtering Logic

When both `excluded_types` and `only_types` are specified:
1. `only_types` is applied first to determine the base set of nodes
2. `excluded_types` then removes specific types from that set

### Examples

#### Exclude Comments and Whitespace
```python
from pretty_sitter.config import FilterConfig

# Hide noise from the output
config = FilterConfig(
    excluded_types=['comment', 'whitespace', 'newline']
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Cleaner output focusing on structural elements.

#### Focus on Definitions Only
```python
# Show only function and class definitions
config = FilterConfig(
    only_types=['function_definition', 'class_definition', 'method_definition']
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Highlights only the most important structural elements.

#### Combined Filtering
```python
# Show functions but exclude their docstrings
config = FilterConfig(
    only_types=['function_definition', 'identifier', 'parameters'],
    excluded_types=['string']  # Excludes docstrings
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Shows function signatures without implementation details.

## MarkingConfig - Node Highlighting

The `MarkingConfig` class allows you to highlight specific nodes with custom colors and labels.

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `marks` | list[Mark] | [] | List of (name, color, nodes) tuples |
| `definition_nodes` | list[Node] \| None | None | Nodes representing definitions (red) |
| `usage_nodes` | list[Node] \| None | None | Nodes representing usages (green) |
| `undefined_usage_nodes` | list[Node] \| None | None | Undefined usage nodes (yellow) |

### Mark Tuple Structure

A `Mark` is a tuple containing:
- `str`: Display name for the mark category
- `str`: Color name ('red', 'green', 'green2', 'yellow', 'blue', 'cyan', 'gray')
- `list[Node]`: List of nodes to highlight

### Examples

#### Manual Marking with Custom Colors
```python
from pretty_sitter.config import MarkingConfig

# Highlight specific nodes with custom categories
config = MarkingConfig(marks=[
    ('Important Functions', 'red', [func_node1, func_node2]),
    ('Helper Methods', 'blue', [helper_node1, helper_node2]),
    ('Constants', 'cyan', [const_node1, const_node2])
])

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Different categories of nodes are highlighted in different colors with a legend.

#### Semantic Highlighting with Convenience Attributes
```python
# Use convenience attributes for common semantic highlighting
config = MarkingConfig(
    definition_nodes=[def_node1, def_node2],      # Red "Definitions"
    usage_nodes=[use_node1, use_node2],           # Green "Usages"
    undefined_usage_nodes=[undef_node]            # Yellow "Undefined"
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Standard semantic highlighting with predefined colors and labels.

#### Mixed Approach
```python
# Combine manual marks with convenience attributes
config = MarkingConfig(
    marks=[('Custom Category', 'cyan', [custom_node])],
    definition_nodes=[def_node],
    usage_nodes=[use_node]
)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Flexible highlighting combining custom and standard categories.

## TTYConfig - Terminal Behavior

The `TTYConfig` class controls how output is displayed in terminal environments.

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `use_pager` | bool | False | Use pager (like 'less') for large outputs |

### Examples

#### Enable Pager for Large Outputs
```python
from pretty_sitter.config import TTYConfig

# Use pager for scrollable output
config = TTYConfig(use_pager=True)

ps = PrettySitter(config)
ps.pprint(tree.root_node)  # Output displayed in 'less'
```

**Visual Impact**: Large parse trees are displayed in a scrollable pager interface.

### Pager Requirements

- Requires 'less' command in system PATH
- Works best when stdout is a TTY
- Warnings displayed if environment is not suitable

## DebugConfig - Debugging Output

The `DebugConfig` class provides debugging and diagnostic information.

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug` | bool | False | Include debug information in output |
| `debug_only` | bool | False | Show only debug output, filter normal content |

### Examples

#### Enable Debug Information
```python
from pretty_sitter.config import DebugConfig

# Show debug info alongside normal output
config = DebugConfig(debug=True)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Adds debug messages showing which nodes are processed or skipped.

#### Debug-Only Mode
```python
# Show only debug information
config = DebugConfig(debug=True, debug_only=True)

ps = PrettySitter(config)
ps.pprint(tree.root_node)
```

**Visual Impact**: Shows only debug messages, hiding the normal tree output.

### Debug Information Includes

- Nodes skipped due to filtering rules
- Node processing decisions and reasons
- Internal state during tree traversal
- Node metadata (type, text, depth, position)

## Configuration Inheritance and Combination

### Multiple Configuration Objects

You can combine multiple configuration objects when initializing PrettySitter:

```python
from pretty_sitter import PrettySitter
from pretty_sitter.config import UIConfig, FilterConfig, MarkingConfig

ps = PrettySitter(
    UIConfig(with_text=False, indent_size=2),
    FilterConfig(excluded_types=['comment']),
    MarkingConfig(definition_nodes=[def_node])
)
```

### Configuration Override Rules

When multiple configuration objects are provided:
- Later configurations override earlier ones for conflicting settings
- Non-conflicting settings are merged
- Each configuration class maintains its own namespace

### Temporary Configuration with Context Manager

Use the `configure()` context manager for temporary overrides:

```python
ps = PrettySitter(UIConfig(with_text=True))

# Temporarily disable text for this operation
with ps.configure(UIConfig(with_text=False)):
    ps.pprint(node)  # Prints without text

# Original configuration restored automatically
ps.pprint(node)  # Prints with text again
```

### Configuration Precedence Example

```python
# Base configuration
base_ui = UIConfig(with_text=True, indent_size=4, print_with_color=True)

# Override configuration
override_ui = UIConfig(with_text=False, indent_size=2)

ps = PrettySitter(base_ui, override_ui)

# Resulting configuration:
# - with_text: False (overridden)
# - indent_size: 2 (overridden)  
# - print_with_color: True (inherited from base)
```

## Common Configuration Patterns

### Code Review Configuration
```python
# Highlight definitions and usages for code review
review_config = [
    UIConfig(column_width=120, indent_size=2),
    FilterConfig(excluded_types=['comment', 'whitespace']),
    MarkingConfig(
        definition_nodes=definitions,
        usage_nodes=usages,
        undefined_usage_nodes=undefined
    )
]

ps = PrettySitter(*review_config)
```

### Documentation Generation
```python
# Clean output for documentation
doc_config = [
    UIConfig(
        print_with_color=False,
        color_legend=False,
        with_trivial=False,
        column_width=80
    ),
    FilterConfig(excluded_types=['comment'])
]

ps = PrettySitter(*doc_config)
```

### Interactive Debugging
```python
# Full debug information with pager
debug_config = [
    UIConfig(with_text=True, color_legend=True),
    TTYConfig(use_pager=True),
    DebugConfig(debug=True)
]

ps = PrettySitter(*debug_config)
```

### Performance Analysis
```python
# Focus on specific node types for performance analysis
perf_config = [
    UIConfig(with_text=False, indent_size=1),
    FilterConfig(only_types=['function_definition', 'call_expression']),
    MarkingConfig(marks=[('Hot Paths', 'red', hot_path_nodes)])
]

ps = PrettySitter(*perf_config)
```

## Best Practices

### Choosing Configuration Options

1. **Start Simple**: Begin with default configuration and add customizations as needed
2. **Consider Your Audience**: Use colors for interactive use, plain text for logs
3. **Filter Appropriately**: Remove noise but keep essential context
4. **Use Semantic Marking**: Leverage `MarkingConfig` for meaningful highlighting
5. **Test with Real Data**: Verify configurations work with your actual parse trees

### Performance Considerations

- **Filtering**: Use `FilterConfig` to reduce output size for better performance
- **Pager**: Enable `use_pager` for large trees to avoid terminal scrollback issues
- **Colors**: Disable colors in non-interactive environments to improve performance
- **Debug Mode**: Only enable debug output when actively troubleshooting

### Environment Compatibility

- **Terminal Support**: Check TERM environment variable for color compatibility
- **Pager Availability**: Ensure 'less' is available when using `use_pager=True`
- **TTY Detection**: Be aware of TTY vs non-TTY environments for optimal output

This configuration guide provides comprehensive coverage of all pretty-sitter configuration options. Experiment with different combinations to find the setup that works best for your specific use case.