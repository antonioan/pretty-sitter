import contextlib
import os
import re
import subprocess
import sys
from functools import reduce
from time import sleep
from typing import Callable, ClassVar, Generator

from tree_sitter import Node

from pretty_sitter.colorer import Colorer
from pretty_sitter.configs import Config, _CombinedConfig


class PrettySitter:
    def __init__(
            self,
            *configs: Config,
    ):
        self._config = _CombinedConfig()
        self._configure(*configs)
        self._colorer = Colorer(self._boldworthy)

    def _configure(self, *configs: Config):
        combined_dict = reduce(dict.__or__, [c.__dict__ for c in configs], self._config.__dict__)
        self._config = _CombinedConfig(**combined_dict)

    @contextlib.contextmanager
    def configure(self, *configs: Config) -> Generator[None, None, None]:
        old_config = self._config
        self._configure(*configs)
        yield
        self._config = old_config

    @staticmethod
    def _text(n: Node) -> str:
        node_text = n.text.decode('utf8')
        node_text = node_text.replace('\n', r'\n')
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
        return not any((
            self._excluded(n),
            not self._included(n),
            not self._config.with_trivial and not self._nontrivial(n),
        ))

    def _boldworthy(self, node_type: str) -> bool:
        return self._config.only_types is not None and node_type in self._config.only_types

    def _leaf(self, n: Node) -> bool:
        if len(n.children) == 0:
            return True
        return not self._config.with_trivial and not any(self._nontrivial(c) for c in n.children)

    def _column(self, text: str) -> str:
        # Note: we cannot use print(f'{text:<width}') because color codes count as characters
        if self._config.dotted:
            return text + ' ' + Colorer.gray('.' * (self._config.column_width - len(self._colorer.uncolor(text)) + 2)) + ' '
        return text + ' ' * (self._config.column_width - len(self._colorer.uncolor(text)))

    def _print(self, text: str):
        uncolored = self._colorer.uncolor(text)
        if self._config.debug_only and not uncolored.startswith('DEBUG:'):
            return
        text_to_print = text if self._config.print_with_color else uncolored
        if self._config.use_pager:
            if not hasattr(self._print, 'pager_lines'):
                self._print.pager_lines = []
            self._print.pager_lines.append(text_to_print)
        else:
            print(text_to_print)

    def _find_mark(self, n: Node) -> Colorer.Brush | None:
        return next((brush for name, brush, nodes in self._config.marks if n in nodes), None)

    def _color_legend(self) -> list[str]:
        with self._colorer.persist(bold=False):
            legend = [self._colorer[color](name) for name, color, _ in self._config.marks]
            legend.append(self._colorer.cyan('Leaves'))
        return legend

    def _obtain_first_color(self, n: Node) -> Colorer.Brush:
        if color := self._find_mark(n):
            return self._colorer[color]
        if self._nontrivial(n):
            return self._colorer.blue
        return self._colorer.gray

    def _obtain_second_color(self, n: Node) -> Colorer.Brush:
        if color := self._find_mark(n):
            return self._colorer[color]
        if self._leaf(n):
            return self._colorer.cyan
        return self._colorer.gray

    def _indent(self, depth: int, text: str) -> str:
        indent = ' ' * self._config.indent_size * depth
        return indent + text

    def _print_node(self, n: Node, attr_name_in_parent: str | None = None, depth=0, end='') -> bool:
        attr_name_in_parent = attr_name_in_parent + ': ' if attr_name_in_parent is not None else ''
        node_text = self._text(n)
        node_type = n.type
        node_line = n.start_point[0]
        node_name = node_type if n.is_named else '"' + node_type.replace('"', r'\"') + '"'

        if not self._printworthy(n):
            if self._config.debug:
                text_quoted = node_text.replace("'", r"\'")
                text_truncated = text_quoted[:12] + '...' if len(text_quoted) > 15 else text_quoted
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
            text_truncated = text_quoted[:12] + '...' if len(text_quoted) > 15 else text_quoted
            self._print(
                self._colorer.gray(f"DEBUG: 🟢 entered node_name=")
                + node_name_colored
                + self._colorer.gray(f", text='{text_truncated}'")
                + self._colorer.gray(f", {depth=}, end='")
                + end
                + self._colorer.gray("'")
            )

        open_par = self._colorer.by_number(depth, '(')
        closed_par = self._colorer.by_number(depth, ')')

        first_part = self._indent(depth, f'{attr_name_in_parent}{open_par}{node_name_colored}')
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
                    child, n.field_name_for_child(i), depth + 1,
                    end=(end if self._config.close_pars_early and child == last_printworthy_child else ''),
                )

            if not self._config.close_pars_early:
                self._print(self._indent(depth, self._colorer.by_number(depth, ')')))
        else:  # effectively a leaf
            first_part += end
            if not self._config.with_text:
                self._print(first_part)
            else:
                self._print(self._column(first_part) + second_part)
        return True

    def pprint(self, root: Node, *configs: Config):
        with self.configure(*configs):
            if (
                    self._config.print_with_color
                    and os.environ.get('TERM') not in (terminals := ('xterm-256color', 'screen-256color', 'linux'))
            ):
                print(f'WARNING: color might not appear properly, since env var TERM is not one of: {terminals}',
                      file=sys.stderr)

            if self._config.use_pager and not sys.stdout.isatty():
                print(f'WARNING: paging might not work, since stdout was not detected as a TTY',
                      file=sys.stderr)

            if not self._config.use_pager and sys.stdout.isatty():
                print(f'WARNING: word wrapping might drive you crazy, either set `use_pager` or do not use a TTY',
                      file=sys.stderr)

            if self._config.print_with_color and self._config.color_legend:
                print('Color legend:', ', '.join(self._color_legend()))

            self._print_node(root)

            if self._config.use_pager and hasattr(self._print, 'pager_lines'):
                sleep(1)
                subprocess.run(['less', '-RS'], input='\n'.join(self._print.pager_lines), text=True)
