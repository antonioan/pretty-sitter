import textwrap

import pytest
import tree_sitter_python
from tree_sitter import Language, Node, Parser
from tree_tagger import TreeTagger

from pretty_sitter import PrettySitter
from pretty_sitter.configs import FilterConfig, MarkingConfig


language_name = 'python'
language = Language(tree_sitter_python.language())
parser = Parser(language)
tree_tagger = TreeTagger(language, language_name)


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
def root(code: str) -> Node:
    return parser.parse(bytes(code, 'utf8')).root_node


def test_pprint(root: Node):
    tags = tree_tagger.tag(root, find_usage_definitions=True)
    pretty_sitter = PrettySitter(
        FilterConfig(only_types=['identifier']),
    )
    print()
    pretty_sitter.pprint(
        root,
        MarkingConfig(
            definition_nodes=tags.definition_nodes,
            usage_nodes=tags.defined_usage_nodes,
            undefined_usage_nodes=tags.undefined_usage_nodes,
        ),
    )
