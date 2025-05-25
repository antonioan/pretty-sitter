import textwrap

import pytest
import tree_sitter_python
from tree_sitter import Language, Node, Parser

from pretty_sitter import PrettySitter
from pretty_sitter.pretty_sitter import Config, FilterConfig


@pytest.fixture(scope='session')
def parser() -> Parser:
    return Parser(Language(tree_sitter_python.language()))


@pytest.fixture
def code() -> str:
    return textwrap.dedent('''
    import os
    from pathlib import Path
    
    def print_hello(name: str) -> None:
        print(f'Hello, {name}!')
        print(f'We are currently in {str(Path(os.getcwd()))}')
    ''').lstrip()


@pytest.fixture
def node(code: str, parser: Parser) -> Node:
    return parser.parse(bytes(code, 'utf8')).root_node


@pytest.fixture
def configs() -> list[Config]:
    return [
        FilterConfig(only_types=['identifier']),
    ]


@pytest.fixture
def pretty_sitter(node: Node, configs: list[Config]) -> PrettySitter:
    return PrettySitter(node, *configs)


def test_pprint(pretty_sitter: PrettySitter):
    print()
    pretty_sitter.pprint()
