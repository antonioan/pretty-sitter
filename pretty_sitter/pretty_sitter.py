import contextlib
import os
import re
import subprocess
import sys
from abc import ABC
from dataclasses import asdict, dataclass
from functools import reduce
from time import sleep
from typing import Callable, ClassVar, Generator

from tree_sitter import Node


color_regex = re.compile(r'\033\[[0-9;]*m')


@dataclass
class Config(ABC):
    pass


@dataclass
class UIConfig(Config):
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
    excluded_types: list[str] | None = None
    only_types: list[str] | None = None


@dataclass
class MarkingConfig(Config):
    definition_nodes: list[Node] | None = None
    usage_nodes: list[Node] | None = None
    undefined_usage_nodes: list[Node] | None = None


@dataclass
class TTYConfig(Config):
    use_pager: bool = False


@dataclass
class DebugConfig(Config):
    debug: bool = False
    debug_only: bool = False


@dataclass
class _CombinedConfig(UIConfig, FilterConfig, MarkingConfig, TTYConfig, DebugConfig):
    pass


class Colorer:
    COLOR_MAP: ClassVar[dict[str, int]] = dict(
        red=91,
        green=32,
        green2=92,
        yellow=93,
        blue=94,
        cyan=96,
        gray=37,
    )
    Brush: ClassVar[type] = Callable[[str], str] | Callable[[str, bool | None], str]

    _boldworthy: Callable[[str], bool]

    def __init__(self, bold: bool | Callable[[str], bool] = False):
        if isinstance(bold, bool):
            self._boldworthy = lambda _: bold
        else:
            self._boldworthy = bold

    @contextlib.contextmanager
    def persist(self, *, bold: bool) -> Generator[None, None, None]:
        old_worthy = self._boldworthy
        self._boldworthy = lambda _: bold
        yield
        self._boldworthy = old_worthy

    def _apply(self, text: str, color: int, *, modifiers=(), bold: bool | None = None) -> str:
        if bold is None:
            bold = self._boldworthy(text)
        if bold:
            modifiers = (1, 4, *modifiers, color)
        else:
            modifiers = (*modifiers, color)
        return '\033[' + ';'.join(map(str, modifiers)) + 'm' + text + '\033[0m'

    def __getattr__(self, item: str) -> Brush:
        if item in self.COLOR_MAP:
            def _brush(text: str, *, bold: bool | None = None) -> str:
                return self._apply(text, self.COLOR_MAP[item], bold=bold)
            return _brush
        raise NotImplementedError(
            f'color {item} undefined; defined colors are: {tuple(self.COLOR_MAP.keys())}'
        )

    def by_number(self, number: int, text: str, *, bold: bool | None = None) -> str:
        return self._apply(text, number * 10, modifiers=(38, 5), bold=bold)


class PrettySitter:
    def __init__(
            self,
            root: Node,
            /,
            *configs: Config,
    ):
        self._root = root
        self._config = _CombinedConfig()
        self.configure(*configs)
        self._colorer = Colorer(self._boldworthy)

    def configure(self, *configs: Config):
        combined_dict = reduce(dict.__or__, [c.__dict__ for c in configs], self._config.__dict__)
        self._config = _CombinedConfig(**combined_dict)

    @staticmethod
    def _text(n: Node, code: bytes) -> str:
        node_text = code[n.start_byte:n.end_byte].decode('utf-8')
        node_text = node_text.replace('\n', r'\n')
        return node_text

    def _trivial(self, n: Node, code: bytes) -> bool:
        return n.type == self._text(n, code)

    def _excluded(self, n: Node) -> bool:
        return self._config.excluded_types is not None and n.type in self._config.excluded_types

    def _included(self, n: Node) -> bool:
        if self._config.only_types is None:
            return True
        if len(n.children) == 0:
            return n.type in self._config.only_types
        return any(self._included(c) for c in n.children)

    def _printworthy(self, n: Node, code: bytes) -> bool:
        return not any((
            self._excluded(n),
            not self._included(n),
            not self._config.with_trivial and self._trivial(n, code),
        ))

    def _boldworthy(self, node_type: str) -> bool:
        return self._config.only_types is not None and node_type in self._config.only_types

    def _leaf(self, n: Node, code: bytes) -> bool:
        return len(n.children) == 0 or (not self._config.with_trivial and all(self._trivial(c, code) for c in n.children))

    def _is_definition(self, n: Node) -> bool:
        return self._config.definition_nodes is not None and n in self._config.definition_nodes

    def _is_usage(self, n: Node) -> bool:
        return self._config.usage_nodes is not None and n in self._config.usage_nodes

    def _is_undefined_usage(self, n: Node) -> bool:
        return self._config.undefined_usage_nodes is not None and n in self._config.undefined_usage_nodes

    @staticmethod
    def _uncolor(text: str):
        return color_regex.sub('', text)

    def _column(self, text: str) -> str:
        # Note: we cannot use print(f'{text:<width}') because color codes count as characters
        if self._config.dotted:
            return text + ' ' + Colorer.gray('.' * (self._config.column_width - len(self._uncolor(text)) + 2)) + ' '
        return text + ' ' * (self._config.column_width - len(self._uncolor(text)))

    def _print(self, text: str):
        if self._config.debug_only and not re.match(rf'^(?:{color_regex.pattern})?DEBUG:', text):
            return
        text_to_print = text if self._config.print_with_color else self._uncolor(text)
        if self._config.use_pager:
            if not hasattr(self._print, 'pager_lines'):
                self._print.pager_lines = []
            self._print.pager_lines.append(text_to_print)
        else:
            print(text_to_print)

    def _obtain_first_color(self, n: Node, code: bytes) -> Colorer.Brush:
        return (
            self._colorer.red if self._is_definition(n)
            else self._colorer.green2 if self._is_usage(n)
            else self._colorer.yellow if self._is_undefined_usage(n)
            else self._colorer.blue if not self._trivial(n, code)
            else self._colorer.gray
        )

    def _obtain_second_color(self, n: Node, code: bytes) -> Colorer.Brush:
        return (
            self._colorer.red if self._is_definition(n)
            else self._colorer.green2 if self._is_usage(n)
            else self._colorer.yellow if self._is_undefined_usage(n)
            else self._colorer.cyan if self._leaf(n, code)
            else self._colorer.gray
        )

    def _indent(self, depth: int, text: str) -> str:
        indent = ' ' * self._config.indent_size * depth
        return indent + text

    def _print_node(self, n: Node, code: bytes, attr_name_in_parent: str | None = None, depth=0, end='') -> bool:
        attr_name_in_parent = attr_name_in_parent + ': ' if attr_name_in_parent is not None else ''
        node_text = self._text(n, code)
        node_type = n.type
        node_line = n.start_point[0]
        node_name = node_type if n.is_named else '"' + node_type.replace('"', r'\"') + '"'

        if not self._printworthy(n, code):
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

        first_color = self._obtain_first_color(n, code)
        second_color = self._obtain_second_color(n, code)

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
            last_printworthy_child = next(c for c in reversed(n.children) if self._printworthy(c, code))
        except StopIteration:
            last_printworthy_child = None

        if last_printworthy_child is not None:  # i.e. there is at least one child to be printed
            if not self._config.with_text:
                self._print(first_part)
            else:
                self._print(self._column(first_part) + second_part)

            for i, child in enumerate(n.children):
                self._print_node(
                    child, code, n.field_name_for_child(i), depth + 1,
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

    def pprint(self):
        if self._config.print_with_color and os.environ.get('TERM') not in (terminals := ('xterm-256color', 'screen-256color', 'linux')):
            print(f'WARNING: color might not appear properly, since env var TERM is not one of: {terminals}',
                  file=sys.stderr)

        if self._config.use_pager and not sys.stdout.isatty():
            print(f'WARNING: paging might not work, since stdout was not detected as a TTY',
                  file=sys.stderr)

        if not self._config.use_pager and sys.stdout.isatty():
            print(f'WARNING: word wrapping might drive you crazy, either set `use_pager` or do not use a TTY',
                  file=sys.stderr)

        if self._config.print_with_color and self._config.color_legend:
            with self._colorer.persist(bold=False):
                legend = []
                if self._config.definition_nodes is not None:
                    legend.append(self._colorer.red('Definitions'))
                if self._config.usage_nodes is not None:
                    legend.append(self._colorer.green('Usages'))
                if self._config.undefined_usage_nodes is not None:
                    legend.append(self._colorer.yellow('Undefined'))
                legend.append(self._colorer.cyan('Leaves'))
                print('Color legend:', ', '.join(legend))

        self._print_node(self._root, self._root.text)

        if self._config.use_pager and hasattr(self._print, 'pager_lines'):
            sleep(1)
            subprocess.run(['less', '-RS'], input='\n'.join(self._print.pager_lines), text=True)
