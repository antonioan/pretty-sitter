from abc import ABC
from dataclasses import dataclass, field

from tree_sitter import Node


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


Mark = tuple[str, str, list[Node]]


@dataclass
class MarkingConfig(Config):
    marks: list[Mark] = field(default_factory=list)
    definition_nodes: list[Node] | None = None
    usage_nodes: list[Node] | None = None
    undefined_usage_nodes: list[Node] | None = None

    def __post_init__(self):
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
    use_pager: bool = False


@dataclass
class DebugConfig(Config):
    debug: bool = False
    debug_only: bool = False


@dataclass
class _CombinedConfig(UIConfig, FilterConfig, MarkingConfig, TTYConfig, DebugConfig):
    pass
