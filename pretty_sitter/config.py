from abc import ABC
from dataclasses import dataclass, field
from typing import Union

from tree_sitter import Node


@dataclass
class Config(ABC):
    """Abstract base class for all pretty-sitter configuration objects.
    
    This class serves as the foundation for all configuration classes in the
    pretty-sitter system. Configuration objects control various aspects of
    the pretty printing behavior including UI appearance, filtering, marking,
    terminal handling, and debugging.
    
    All concrete configuration classes inherit from this base class and can
    be combined when initializing PrettySitter or used with the configure()
    context manager.
    """
    pass


@dataclass
class UIConfig(Config):
    """Configuration for user interface and visual formatting options.
    
    This configuration class controls the visual appearance and layout of the
    pretty-printed parse tree output, including text display, colors, indentation,
    and column formatting.
    
    Attributes:
        with_text (bool): Whether to display the actual text content of nodes
                         alongside the node type. Default: True.
        with_trivial (bool): Whether to include trivial nodes (nodes where the
                           type matches the text content). Default: False.
        close_pars_early (bool): Whether to close parentheses early when possible
                               to reduce visual clutter. Default: True.
        print_with_color (bool): Whether to apply ANSI color codes to the output.
                               Default: True.
        color_legend (bool): Whether to display a color legend before the tree
                           when colors are enabled. Default: True.
        dotted (bool): Whether to use dotted lines for column alignment instead
                      of spaces. Default: False.
        column_width (int): Width of the first column containing node structure
                          before text content. Default: 100.
        indent_size (int): Number of spaces to use for each indentation level.
                         Default: 4.
    
    Examples:
        >>> # Minimal output without text content
        >>> config = UIConfig(with_text=False, with_trivial=False)
        >>> 
        >>> # Compact formatting with smaller indentation
        >>> config = UIConfig(indent_size=2, column_width=50)
        >>> 
        >>> # Plain text output without colors
        >>> config = UIConfig(print_with_color=False, color_legend=False)
    """
    with_text: bool = True
    with_trivial: bool = False
    close_pars_early: bool = True
    print_with_color: bool = True
    color_legend: bool = True
    dotted: bool = False
    column_width: int = 100
    indent_size: int = 4


@dataclass
class FilterConfig(Config):
    """Configuration for filtering which nodes are displayed in the output.
    
    This configuration class provides options to include or exclude specific
    node types from the pretty-printed output, allowing users to focus on
    relevant parts of the parse tree.
    
    Attributes:
        excluded_types (list[str] | None): List of node type names to exclude
                                         from the output. If None, no nodes are
                                         excluded based on type. Default: None.
        only_types (list[str] | None): List of node type names to include in
                                     the output. If specified, only these types
                                     (and their children) will be shown. If None,
                                     all types are included. Default: None.
    
    Examples:
        >>> # Exclude comment and whitespace nodes
        >>> config = FilterConfig(excluded_types=['comment', 'whitespace'])
        >>> 
        >>> # Show only function and class definitions
        >>> config = FilterConfig(only_types=['function_definition', 'class_definition'])
        >>> 
        >>> # Note: excluded_types and only_types can be used together
        >>> # only_types is applied first, then excluded_types filters the result
    
    Note:
        When both excluded_types and only_types are specified, only_types is
        applied first to determine the base set of nodes to include, then
        excluded_types is used to remove specific types from that set.
    """
    excluded_types: Union[list[str], None] = None
    only_types: Union[list[str], None] = None


Mark = tuple[str, str, list[Node]]
"""Type alias for marking configuration.

A Mark is a tuple containing:
- str: Display name for the mark category
- str: Color name to use for highlighting
- list[Node]: List of nodes to mark with this color
"""


@dataclass
class MarkingConfig(Config):
    """Configuration for highlighting specific nodes with colors and labels.
    
    This configuration class allows users to highlight specific nodes in the
    parse tree with custom colors and labels. It's particularly useful for
    semantic analysis, showing definitions, usages, and other relationships
    between nodes.
    
    Attributes:
        marks (list[Mark]): List of mark tuples, each containing a name, color,
                          and list of nodes to highlight. Default: empty list.
        definition_nodes (list[Node] | None): Convenience attribute for nodes
                                            representing definitions. These will
                                            be automatically converted to a red
                                            mark labeled "Definitions". Default: None.
        usage_nodes (list[Node] | None): Convenience attribute for nodes
                                       representing usages. These will be
                                       automatically converted to a green mark
                                       labeled "Usages". Default: None.
        undefined_usage_nodes (list[Node] | None): Convenience attribute for
                                                 nodes representing undefined
                                                 usages. These will be converted
                                                 to a yellow mark labeled
                                                 "Undefined". Default: None.
    
    Examples:
        >>> # Manual marking with custom colors
        >>> config = MarkingConfig(marks=[
        ...     ('Important', 'red', [node1, node2]),
        ...     ('Optional', 'blue', [node3])
        ... ])
        >>> 
        >>> # Using convenience attributes for semantic highlighting
        >>> config = MarkingConfig(
        ...     definition_nodes=[def_node1, def_node2],
        ...     usage_nodes=[use_node1, use_node2],
        ...     undefined_usage_nodes=[undef_node]
        ... )
        >>> 
        >>> # Mixed approach
        >>> config = MarkingConfig(
        ...     marks=[('Custom', 'cyan', [custom_node])],
        ...     definition_nodes=[def_node]
        ... )
    
    Note:
        The convenience attributes (definition_nodes, usage_nodes,
        undefined_usage_nodes) are automatically converted to marks during
        initialization and then cleared to avoid duplication.
    """
    marks: list[Mark] = field(default_factory=list)
    definition_nodes: Union[list[Node], None] = None
    usage_nodes: Union[list[Node], None] = None
    undefined_usage_nodes: Union[list[Node], None] = None

    def __post_init__(self) -> None:
        """Convert convenience attributes to marks after initialization."""
        if self.definition_nodes:
            self.marks.append(('Definitions', 'red', self.definition_nodes))
            self.definition_nodes = None
        if self.usage_nodes:
            self.marks.append(('Usages', 'green2', self.usage_nodes))
            self.usage_nodes = None
        if self.undefined_usage_nodes:
            self.marks.append(('Undefined', 'yellow', self.undefined_usage_nodes))
            self.undefined_usage_nodes = None


@dataclass
class TTYConfig(Config):
    """Configuration for terminal and pager behavior.
    
    This configuration class controls how the output is displayed in terminal
    environments, including pager usage for handling large outputs.
    
    Attributes:
        use_pager (bool): Whether to use a pager (like 'less') for displaying
                        output. When enabled, output is collected and then
                        displayed through the pager, allowing for scrolling
                        and searching in large parse trees. Default: False.
    
    Examples:
        >>> # Enable pager for large outputs
        >>> config = TTYConfig(use_pager=True)
        >>> 
        >>> # Disable pager for direct output
        >>> config = TTYConfig(use_pager=False)
    
    Note:
        The pager functionality requires the 'less' command to be available
        in the system PATH. Warnings will be displayed if pager is enabled
        but the environment is not suitable (e.g., stdout is not a TTY).
    """
    use_pager: bool = False


@dataclass
class DebugConfig(Config):
    """Configuration for debugging and diagnostic output.
    
    This configuration class provides options for enabling debug information
    and diagnostic output to help understand the pretty printing process and
    troubleshoot issues.
    
    Attributes:
        debug (bool): Whether to include debug information in the output.
                     When enabled, shows additional information about node
                     processing, including which nodes are skipped and why.
                     Default: False.
        debug_only (bool): Whether to show only debug output, filtering out
                         all non-debug content. This is useful for focusing
                         on the debugging information without the normal
                         tree output. Default: False.
    
    Examples:
        >>> # Enable debug information alongside normal output
        >>> config = DebugConfig(debug=True)
        >>> 
        >>> # Show only debug information
        >>> config = DebugConfig(debug=True, debug_only=True)
        >>> 
        >>> # Normal operation (no debug output)
        >>> config = DebugConfig()  # Both default to False
    
    Note:
        Debug output includes information about:
        - Nodes that are skipped due to filtering rules
        - Node processing decisions and their reasons
        - Internal state information during tree traversal
    """
    debug: bool = False
    debug_only: bool = False


@dataclass
class _CombinedConfig(UIConfig, FilterConfig, MarkingConfig, TTYConfig, DebugConfig):
    """Internal combined configuration class that merges all config types.
    
    This class is used internally by PrettySitter to combine multiple
    configuration objects into a single configuration instance. It inherits
    from all configuration classes, providing a unified interface to all
    configuration options.
    
    Note:
        This class is for internal use only and should not be instantiated
        directly by users. Use the individual configuration classes instead.
    """
    pass
