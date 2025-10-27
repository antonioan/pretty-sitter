# Configuration Options Reference

This page provides a comprehensive reference for all configuration options available in pretty-sitter. Configuration objects control various aspects of the pretty printing behavior and can be combined when initializing PrettySitter or used with the `configure()` context manager.

## Configuration System Overview

Pretty-sitter uses a modular configuration system where different aspects of behavior are controlled by separate configuration classes:

- **UIConfig**: Controls visual appearance and formatting
- **FilterConfig**: Controls which nodes are displayed
- **MarkingConfig**: Controls node highlighting and coloring
- **TTYConfig**: Controls terminal and pager behavior
- **DebugConfig**: Controls debugging and diagnostic output

All configuration classes inherit from the abstract `Config` base class and can be combined in any order. When multiple configurations specify the same option, later configurations override earlier ones.

## UIConfig - User Interface Options

Controls the visual appearance and layout of the pretty-printed parse tree output.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `with_text` | `bool` | `True` | Whether to display the actual text content of nodes alongside the node type |
| `with_trivial` | `bool` | `False` | Whether to include trivial nodes (nodes where the type matches the text content) |
| `close_pars_early` | `bool` | `True` | Whether to close parentheses early when possible to reduce visual clutter |
| `print_with_color` | `bool` | `True` | Whether to apply ANSI color codes to the output |
| `color_legend` | `bool` | `True` | Whether to display a color legend before the tree when colors are enabled |
| `dotted` | `bool` | `False` | Whether to use dotted lines for column alignment instead of spaces |
| `column_width` | `int` | `100` | Width of the first column containing node structure before text content |
| `indent_size` | `int` | `4` | Number of spaces to use for each indentation level |

### Examples

```python
from pretty_sitter.config import UIConfig

# Minimal output without text content
config = UIConfig(with_text=False, with_trivial=False)

# Compact formatting with smaller indentation
config = UIConfig(indent_size=2, column_width=50)

# Plain text output without colors
config = UIConfig(print_with_color=False, color_legend=False)
```

## FilterConfig - Node Filtering Options

Provides options to include or exclude specific node types from the pretty-printed output.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `excluded_types` | `list[str] \| None` | `None` | List of node type names to exclude from the output. If None, no nodes are excluded based on type |
| `only_types` | `list[str] \| None` | `None` | List of node type names to include in the output. If specified, only these types (and their children) will be shown. If None, all types are included |

### Filter Processing Order

When both `excluded_types` and `only_types` are specified:
1. `only_types` is applied first to determine the base set of nodes to include
2. `excluded_types` is then used to remove specific types from that set

### Examples

```python
from pretty_sitter.config import FilterConfig

# Exclude comment and whitespace nodes
config = FilterConfig(excluded_types=['comment', 'whitespace'])

# Show only function and class definitions
config = FilterConfig(only_types=['function_definition', 'class_definition'])

# Combined filtering: show only functions but exclude comments within them
config = FilterConfig(
    only_types=['function_definition'],
    excluded_types=['comment']
)
```

## MarkingConfig - Node Highlighting Options

Allows highlighting specific nodes in the parse tree with custom colors and labels.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `marks` | `list[Mark]` | `[]` | List of mark tuples, each containing a name, color, and list of nodes to highlight |
| `definition_nodes` | `list[Node] \| None` | `None` | Convenience attribute for nodes representing definitions (converted to red "Definitions" mark) |
| `usage_nodes` | `list[Node] \| None` | `None` | Convenience attribute for nodes representing usages (converted to green "Usages" mark) |
| `undefined_usage_nodes` | `list[Node] \| None` | `None` | Convenience attribute for undefined usages (converted to yellow "Undefined" mark) |

### Mark Type Definition

A `Mark` is a tuple containing:
- `str`: Display name for the mark category
- `str`: Color name to use for highlighting (must be a valid color from Colorer.COLOR_MAP)
- `list[Node]`: List of nodes to mark with this color

### Available Colors

- `red` (91)
- `green` (32) 
- `green2` (92)
- `yellow` (93)
- `blue` (94)
- `cyan` (96)
- `gray` (37)

### Examples

```python
from pretty_sitter.config import MarkingConfig

# Manual marking with custom colors
config = MarkingConfig(marks=[
    ('Important', 'red', [node1, node2]),
    ('Optional', 'blue', [node3])
])

# Using convenience attributes for semantic highlighting
config = MarkingConfig(
    definition_nodes=[def_node1, def_node2],
    usage_nodes=[use_node1, use_node2],
    undefined_usage_nodes=[undef_node]
)

# Mixed approach
config = MarkingConfig(
    marks=[('Custom', 'cyan', [custom_node])],
    definition_nodes=[def_node]
)
```

## TTYConfig - Terminal Behavior Options

Controls how the output is displayed in terminal environments.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `use_pager` | `bool` | `False` | Whether to use a pager (like 'less') for displaying output. When enabled, output is collected and displayed through the pager |

### Pager Requirements

- Requires the `less` command to be available in the system PATH
- Works best when stdout is a TTY
- Warnings are displayed if the environment is not suitable for pager usage

### Examples

```python
from pretty_sitter.config import TTYConfig

# Enable pager for large outputs
config = TTYConfig(use_pager=True)

# Disable pager for direct output (default)
config = TTYConfig(use_pager=False)
```

## DebugConfig - Debugging Options

Provides options for enabling debug information and diagnostic output.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug` | `bool` | `False` | Whether to include debug information in the output showing node processing details |
| `debug_only` | `bool` | `False` | Whether to show only debug output, filtering out all non-debug content |

### Debug Information Includes

- Nodes that are skipped due to filtering rules
- Node processing decisions and their reasons  
- Internal state information during tree traversal
- Node names, text content, depth, and processing status

### Examples

```python
from pretty_sitter.config import DebugConfig

# Enable debug information alongside normal output
config = DebugConfig(debug=True)

# Show only debug information
config = DebugConfig(debug=True, debug_only=True)

# Normal operation (no debug output) - default
config = DebugConfig()
```

## Configuration Combination

Multiple configuration objects can be combined when initializing PrettySitter or using the `configure()` context manager. Later configurations override earlier ones for conflicting settings.

### Examples

```python
from pretty_sitter import PrettySitter
from pretty_sitter.config import UIConfig, FilterConfig, DebugConfig

# Combine multiple configurations at initialization
ps = PrettySitter(
    UIConfig(with_text=False, indent_size=2),
    FilterConfig(only_types=['function_definition']),
    DebugConfig(debug=True)
)

# Temporarily override configuration
with ps.configure(UIConfig(print_with_color=False)):
    ps.pprint(node)  # Prints without colors
# Original configuration restored here

# Configuration override order matters
ps = PrettySitter(
    UIConfig(indent_size=2),      # Sets indent to 2
    UIConfig(indent_size=4)       # Overrides to 4
)
```

## Environment Considerations

### Color Output

Pretty-sitter checks the `TERM` environment variable and warns if it's not one of the supported terminals:
- `xterm-256color`
- `screen-256color` 
- `linux`

### TTY Detection

The system automatically detects TTY environments and provides warnings for:
- Pager enabled but stdout is not a TTY
- Pager disabled but stdout is a TTY (may cause wrapping issues)

### Terminal Compatibility

Color output uses ANSI escape sequences and works best with modern terminal emulators that support 256-color mode.