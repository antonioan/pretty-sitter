import os
import re
import subprocess
import sys
from time import sleep

from tree_sitter import Node


# TODO: What advantage does this have over: https://tree-sitter.github.io/tree-sitter/7-playground.html
def pprint_with_text(
        root_node: Node,
        # UI
        with_text=True,
        with_trivial=False,
        close_pars_early=True,
        print_with_color=True,
        color_legend=True,
        column_width=100,
        dotted=False,
        indent_size=4,
        # Filter
        excluded_types: list | None = None,
        only_types: list | None = None,
        # Node marking
        definition_nodes: list[Node] | None = None,
        usage_nodes: list[Node] | None = None,
        undefined_usage_nodes: list[None] | None = None,
        # TTY related
        use_pager=False,
        # Debug
        debug=False,
        breakpoint_on_line: int | None = None,
        debug_only=False,
):
    color_regex = re.compile(r'\033\[[0-9;]*m')
    py_debugging = (gettrace := getattr(sys, 'gettrace')) and gettrace()

    if breakpoint_on_line:
        if not py_debugging:
            print('INFO: python was not run in debug mode, so `breakpoint_on_line` will be ignored')
            breakpoint_on_line = None
        elif not debug:
            print('INFO: `debug` was not set to True, so `breakpoint_on_line` will be ignored')
            breakpoint_on_line = None

    if print_with_color and os.environ.get('TERM') not in (terminals := ('xterm-256color', 'screen-256color', 'linux')):
        print(f'WARNING: color might not appear properly, since env var TERM is not one of: {terminals}',
              file=sys.stderr)

    if use_pager and not sys.stdout.isatty():
        print(f'WARNING: paging might not work, since stdout was not detected as a TTY',
              file=sys.stderr)

    if not use_pager and sys.stdout.isatty():
        print(f'WARNING: word wrapping might drive you crazy, either set `use_pager` or do not use a TTY',
              file=sys.stderr)

    def _text(n: Node, code: bytes) -> str:
        node_text = code[n.start_byte:n.end_byte].decode('utf-8')
        node_text = node_text.replace('\n', r'\n')
        return node_text

    def _trivial(n: Node, code: bytes) -> bool:
        return n.type == _text(n, code)

    def _excluded(n: Node) -> bool:
        return excluded_types is not None and n.type in excluded_types

    def _included(n: Node) -> bool:
        if only_types is None:
            return True
        if len(n.children) == 0:
            return n.type in only_types
        return any(_included(c) for c in n.children)

    def _printworthy(n: Node, code: bytes) -> bool:
        return not any((
            _excluded(n),
            not _included(n),
            not with_trivial and _trivial(n, code),
        ))

    def _boldworthy(node_type: str) -> bool:
        return only_types is not None and node_type in only_types

    def _leaf(n: Node, code: bytes) -> bool:
        return len(n.children) == 0 or (not with_trivial and all(_trivial(c, code) for c in n.children))

    def _gray(text: str) -> str:
        return '\033[37m' + text + '\033[0m'

    def _green(text: str) -> str:
        return '\033[32m' + text + '\033[0m'

    def _cyan(text: str) -> str:
        return '\033[96m' + text + '\033[0m'

    def _red(text: str) -> str:
        return f'\033[91m' + text + '\033[0m'

    def _yellow(text: str) -> str:
        return f'\033[93m' + text + '\033[0m'

    def _b_blue(node_type: str) -> str:
        return f'\033[{"1;4;" if _boldworthy(node_type) else ""}94m' + node_type + '\033[0m'

    def _b_red(node_type: str) -> str:
        return f'\033[{"1;4;" if _boldworthy(node_type) else ""}91m' + node_type + '\033[0m'

    def _b_green(node_type: str) -> str:
        return f'\033[{"1;4;" if _boldworthy(node_type) else ""}92m' + node_type + '\033[0m'

    def _b_yellow(node_type: str) -> str:
        return f'\033[{"1;4;" if _boldworthy(node_type) else ""}93m' + node_type + '\033[0m'

    def _is_definition(n: Node) -> bool:
        return definition_nodes is not None and n in definition_nodes

    def _is_usage(n: Node) -> bool:
        return usage_nodes is not None and n in usage_nodes

    def _is_undefined_usage(n: Node) -> bool:
        return undefined_usage_nodes is not None and n in undefined_usage_nodes

    def _colored_par(depth: int, closed=False) -> str:
        return f'\033[38;5;{depth * 10}m' + (')' if closed else '(') + f'\033[0m'

    def _uncolor(text: str):
        return color_regex.sub('', text)

    def _column(text: str) -> str:
        # Note: we cannot use print(f'{text:<width}') because color codes count as characters
        if dotted:
            return text + ' ' + _gray('.' * (column_width - len(_uncolor(text)) + 2)) + ' '
        return text + ' ' * (column_width - len(_uncolor(text)))

    def _print(text: str):
        if debug_only and not re.match(rf'^(?:{color_regex.pattern})?DEBUG:', text):
            return
        text_to_print = text if print_with_color else _uncolor(text)
        if use_pager:
            if not hasattr(_print, 'pager_lines'):
                _print.pager_lines = []
            _print.pager_lines.append(text_to_print)
        else:
            print(text_to_print)

    def print_node(n: Node, code: bytes, attr_name_in_parent: str | None = None, depth=0, end='') -> bool:
        attr_name_in_parent = attr_name_in_parent + ': ' if attr_name_in_parent is not None else ''
        indent = ' ' * indent_size * depth
        node_text = _text(n, code)
        node_type = n.type
        node_line = n.start_point[0]
        node_name = node_type if n.is_named else '"' + node_type.replace('"', r'\"') + '"'

        if debug and breakpoint_on_line == node_line:
            breakpoint()

        if not _printworthy(n, code):
            if debug:
                _print(_gray(f"DEBUG: skipped {print_node.__name__} with node_name=") + node_name
                       + _gray(f", {depth=}, end='") + end + _gray("'"))
            return False

        first_color = (_b_red if _is_definition(n)
                       else _b_green if _is_usage(n)
                       else _b_yellow if _is_undefined_usage(n)
                       else _b_blue if not _trivial(n, code)
                       else _gray)
        second_color = (_red if _is_definition(n)
                        else _b_green if _is_usage(n)
                        else _b_yellow if _is_undefined_usage(n)
                        else _cyan if _leaf(n, code)
                        else _gray)

        node_name_colored = first_color(node_name)
        node_text_colored = second_color(node_text)

        if debug:
            _print(_gray(f"DEBUG: entered {print_node.__name__} with node_name=") + node_name_colored
                   + _gray(f", {depth=}, end='") + end + _gray("'"))

        open_par, closed_par = _colored_par(depth), _colored_par(depth, closed=True)

        first_part = f'{indent}{attr_name_in_parent}{open_par}{node_name_colored}'
        second_part = f'''{_gray(f"{node_line:>3}: ")}{node_text_colored}'''

        end = closed_par + end
        try:
            last_printworthy_child = next(c for c in reversed(n.children) if _printworthy(c, code))
        except StopIteration:
            last_printworthy_child = None

        if last_printworthy_child is not None:  # i.e. there is at least one child to be printed
            if not with_text:
                _print(first_part)
            else:
                _print(_column(first_part) + second_part)

            for i, child in enumerate(n.children):
                print_node(
                    child, code, n.field_name_for_child(i), depth + 1,
                    end=(end if close_pars_early and child == last_printworthy_child else ''),
                )

            if not close_pars_early:
                _print(f'{indent}{_colored_par(depth, closed=True)}')
        else:  # effectively a leaf
            first_part += end
            if not with_text:
                _print(first_part)
            else:
                _print(_column(first_part) + second_part)
        return True

    if print_with_color and color_legend:
        print(f"{_red('Definitions')}, {_green('Usages')}, {_yellow('Undefined')}, {_cyan('Leaves')}")

    print_node(root_node, root_node.text)

    if use_pager and hasattr(_print, 'pager_lines'):
        sleep(1)
        subprocess.run(['less', '-RS'], input='\n'.join(_print.pager_lines), text=True)
