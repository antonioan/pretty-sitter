import contextlib
import os
import subprocess
import sys
from functools import reduce
from time import sleep
from typing import Generator, Any

from tree_sitter import Node

from pretty_sitter.colorer import Colorer
from pretty_sitter.config import Config, _CombinedConfig


class PrettySitter:
    """A pretty printer for tree-sitter parse trees with configurable formatting and coloring.

    PrettySitter provides a flexible way to visualize tree-sitter parse trees with customizable
    formatting, filtering, and color schemes. It supports various configuration options to control
    the output appearance and content.

    Examples:
        Basic usage with default configuration:

        >>> from pretty_sitter import PrettySitter
        >>> from tree_sitter import Language, Parser
        >>>
        >>> # Assuming you have a tree-sitter language library
        >>> language = Language(library_path, 'python')
        >>> parser = Parser()
        >>> parser.set_language(language)
        >>> tree = parser.parse(b'def hello(): pass')
        >>>
        >>> ps = PrettySitter()
        >>> ps.pprint(tree.root_node)

        Using custom configuration:

        >>> from pretty_sitter.config import UIConfig, FilterConfig
        >>> ps = PrettySitter(
        ...     UIConfig(with_text=False, indent_size=2),
        ...     FilterConfig(excluded_types=['comment'])
        ... )
        >>> ps.pprint(tree.root_node)

    Attributes:
        _config: Combined configuration object containing all settings.
        _colorer: Colorer instance for applying colors to output.
    """

    def __init__(
        self,
        *configs: Config,
    ):
        """Initialize PrettySitter with optional configuration objects.

        Args:
            *configs: Variable number of Config objects that will be combined to
                     configure the pretty printer behavior. Later configs override
                     earlier ones for conflicting settings.

        Examples:
            >>> ps = PrettySitter()  # Use default configuration
            >>>
            >>> # With custom configurations
            >>> from pretty_sitter.config import UIConfig, FilterConfig
            >>> ps = PrettySitter(
            ...     UIConfig(with_text=False),
            ...     FilterConfig(only_types=['function_definition'])
            ... )
        """
        self._config = _CombinedConfig()
        self._configure(*configs)
        self._colorer = Colorer(self._boldworthy)

    def _configure(self, *configs: Config) -> None:
        """Configure the pretty printer by combining multiple config objects."""
        combined_dict = reduce(dict.__or__, [c.__dict__ for c in configs], self._config.__dict__)
        self._config = _CombinedConfig(**combined_dict)

    @contextlib.contextmanager
    def configure(self, *configs: Config) -> Generator[None, None, None]:
        """Temporarily apply configuration changes within a context manager.

        This method allows you to temporarily override the current configuration
        for a specific operation, automatically restoring the original configuration
        when exiting the context.

        Args:
            *configs: Variable number of Config objects to temporarily apply.

        Yields:
            None: Context manager that applies the temporary configuration.

        Examples:
            >>> ps = PrettySitter()
            >>> with ps.configure(UIConfig(with_text=False)):
            ...     ps.pprint(node)  # Prints without text content
            >>> # Original configuration is restored here
        """
        old_config = self._config
        self._configure(*configs)
        yield
        self._config = old_config

    @staticmethod
    def _text(n: Node) -> str:
        node_text = n.text.decode("utf8")
        node_text = node_text.replace("\n", r"\n")
        return node_text

    def _nontrivial(self, n: Node) -> bool:
        return n.type != self._text(n)

    def _excluded(self, n: Node) -> bool:
        return self._config.excluded_types is not None and n.type in self._config.excluded_types

    def _included(self, n: Node) -> bool:
        if self._config.only_types is None:
            return True
        if len(n.children) == 0:
            return n.type in self._config.only_types
        return any(self._included(c) for c in n.children)

    def _printworthy(self, n: Node) -> bool:
        return not any(
            (
                self._excluded(n),
                not self._included(n),
                not self._config.with_trivial and not self._nontrivial(n),
            )
        )

    def _boldworthy(self, node_type: str) -> bool:
        return self._config.only_types is not None and node_type in self._config.only_types

    def _leaf(self, n: Node) -> bool:
        if len(n.children) == 0:
            return True
        return not self._config.with_trivial and not any(self._nontrivial(c) for c in n.children)

    def _column(self, text: str) -> str:
        """Format text for column display with proper width accounting for color codes."""
        # Note: we cannot use print(f'{text:<width}') because color codes count as characters
        if self._config.dotted:
            return (
                text
                + " "
                + Colorer.gray(
                    "." * (self._config.column_width - len(self._colorer.uncolor(text)) + 2)
                )
                + " "
            )
        return text + " " * (self._config.column_width - len(self._colorer.uncolor(text)))

    def _print(self, text: str) -> None:
        """Print text with appropriate filtering and pager handling."""
        uncolored = self._colorer.uncolor(text)
        if self._config.debug_only and not uncolored.startswith("DEBUG:"):
            return
        text_to_print = text if self._config.print_with_color else uncolored
        if self._config.use_pager:
            if not hasattr(self._print, "pager_lines"):
                self._print.pager_lines = []
            self._print.pager_lines.append(text_to_print)
        else:
            print(text_to_print)

    def _find_mark(self, n: Node) -> Colorer.Brush | None:
        """Find the color name for a marked node, if any."""
        return next((brush for name, brush, nodes in self._config.marks if n in nodes), None)

    def _color_legend(self) -> list[str]:
        """Generate a color legend showing mark categories and their colors."""
        with self._colorer.persist(bold=False):
            legend = [self._colorer[color](name) for name, color, _ in self._config.marks]
            legend.append(self._colorer.cyan("Leaves"))
        return legend

    def _obtain_first_color(self, n: Node) -> Colorer.Brush:
        """Get the color brush for the node type display."""
        if color := self._find_mark(n):
            return self._colorer[color]
        if self._nontrivial(n):
            return self._colorer.blue
        return self._colorer.gray

    def _obtain_second_color(self, n: Node) -> Colorer.Brush:
        """Get the color brush for the node text display."""
        if color := self._find_mark(n):
            return self._colorer[color]
        if self._leaf(n):
            return self._colorer.cyan
        return self._colorer.gray

    def _indent(self, depth: int, text: str) -> str:
        """Add indentation to text based on depth level."""
        indent = " " * self._config.indent_size * depth
        return indent + text

    def _print_node(
        self, n: Node, attr_name_in_parent: str | None = None, depth: int = 0, end: str = ""
    ) -> bool:
        """Recursively print a node and its children with proper formatting.

        Args:
            n: The node to print.
            attr_name_in_parent: The field name of this node in its parent.
            depth: Current indentation depth.
            end: String to append at the end of this node's output.

        Returns:
            bool: True if the node was printed, False if it was skipped.
        """
        attr_name_in_parent = attr_name_in_parent + ": " if attr_name_in_parent is not None else ""
        node_text = self._text(n)
        node_type = n.type
        node_line = n.start_point[0]
        node_name = node_type if n.is_named else '"' + node_type.replace('"', r"\"") + '"'

        if not self._printworthy(n):
            if self._config.debug:
                text_quoted = node_text.replace("'", r"\'")
                text_truncated = text_quoted[:12] + "..." if len(text_quoted) > 15 else text_quoted
                self._print(
                    self._colorer.gray(f"DEBUG: 🔴 skipped node_name=")
                    + node_name
                    + self._colorer.gray(f", text='{text_truncated}'")
                    + self._colorer.gray(f", {depth=}, end='")
                    + end
                    + self._colorer.gray("'")
                )
            return False

        first_color = self._obtain_first_color(n)
        second_color = self._obtain_second_color(n)

        node_name_colored = first_color(node_name)
        node_text_colored = second_color(node_text)

        if self._config.debug:
            text_quoted = node_text.replace("'", r"\'")
            text_truncated = text_quoted[:12] + "..." if len(text_quoted) > 15 else text_quoted
            self._print(
                self._colorer.gray(f"DEBUG: 🟢 entered node_name=")
                + node_name_colored
                + self._colorer.gray(f", text='{text_truncated}'")
                + self._colorer.gray(f", {depth=}, end='")
                + end
                + self._colorer.gray("'")
            )

        open_par = self._colorer.by_number(depth, "(")
        closed_par = self._colorer.by_number(depth, ")")

        first_part = self._indent(depth, f"{attr_name_in_parent}{open_par}{node_name_colored}")
        second_part = self._colorer.gray(f"{node_line:>3}: ") + node_text_colored

        end = closed_par + end
        try:
            last_printworthy_child = next(c for c in reversed(n.children) if self._printworthy(c))
        except StopIteration:
            last_printworthy_child = None

        if last_printworthy_child is not None:  # i.e. there is at least one child to be printed
            if not self._config.with_text:
                self._print(first_part)
            else:
                self._print(self._column(first_part) + second_part)

            for i, child in enumerate(n.children):
                self._print_node(
                    child,
                    n.field_name_for_child(i),
                    depth + 1,
                    end=(
                        end
                        if self._config.close_pars_early and child == last_printworthy_child
                        else ""
                    ),
                )

            if not self._config.close_pars_early:
                self._print(self._indent(depth, self._colorer.by_number(depth, ")")))
        else:  # effectively a leaf
            first_part += end
            if not self._config.with_text:
                self._print(first_part)
            else:
                self._print(self._column(first_part) + second_part)
        return True

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

            Print only specific node types:

            >>> ps.pprint(
            ...     node,
            ...     FilterConfig(only_types=['function_definition', 'class_definition'])
            ... )

        Note:
            This method will print warnings to stderr if:
            - Color output is enabled but terminal doesn't support it properly
            - Pager is enabled but stdout is not a TTY
            - Pager is disabled but stdout is a TTY (may cause wrapping issues)
        """
        with self.configure(*configs):
            if self._config.print_with_color and os.environ.get("TERM") not in (
                terminals := ("xterm-256color", "screen-256color", "linux")
            ):
                print(
                    f"WARNING: color might not appear properly, since env var TERM is not one of: {terminals}",
                    file=sys.stderr,
                )

            if self._config.use_pager and not sys.stdout.isatty():
                print(
                    f"WARNING: paging might not work, since stdout was not detected as a TTY",
                    file=sys.stderr,
                )

            if not self._config.use_pager and sys.stdout.isatty():
                print(
                    f"WARNING: word wrapping might drive you crazy, either set `use_pager` or do not use a TTY",
                    file=sys.stderr,
                )

            if self._config.print_with_color and self._config.color_legend:
                print("Color legend:", ", ".join(self._color_legend()))

            self._print_node(root)

            if self._config.use_pager and hasattr(self._print, "pager_lines"):
                sleep(1)
                subprocess.run(["less", "-RS"], input="\n".join(self._print.pager_lines), text=True)
