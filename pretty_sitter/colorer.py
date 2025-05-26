import contextlib
import re
from typing import Callable, ClassVar, Generator


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

    def _apply(self, text: str, color: int, *, modifiers=()) -> str:
        if self._boldworthy(text):
            modifiers = (1, 4, *modifiers, color)
        else:
            modifiers = (*modifiers, color)
        return '\033[' + ';'.join(map(str, modifiers)) + 'm' + text + '\033[0m'

    def __getattr__(self, item: str) -> Brush:
        if item in self.COLOR_MAP:
            def _brush(text: str) -> str:
                return self._apply(text, self.COLOR_MAP[item])
            _brush.color = item
            return _brush
        raise NotImplementedError(
            f'color {item} undefined; defined colors are: {tuple(self.COLOR_MAP.keys())}'
        )

    def __getitem__(self, item) -> Brush:
        return self.__getattr__(item)

    def by_number(self, number: int, text: str) -> str:
        return self._apply(text, number * 10, modifiers=(38, 5))

    @staticmethod
    def uncolor(text: str) -> str:
        return re.sub(r'\033\[[0-9;]*m', '', text)
