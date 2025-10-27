import contextlib
import re
from typing import Callable, ClassVar, Generator, Union


class Colorer:
    """A color management system for applying ANSI color codes to text strings.
    
    The Colorer class provides a flexible system for applying colors and formatting
    to text output. It supports predefined colors, dynamic color selection, and
    conditional bold formatting based on text content.
    
    Attributes:
        COLOR_MAP: Mapping of color names to ANSI color codes.
        Brush: Type alias for color application functions.
        
    Examples:
        Basic color usage:
        
        >>> colorer = Colorer()
        >>> colored_text = colorer.red("Error message")
        >>> print(colored_text)  # Prints in red
        
        With conditional bold formatting:
        
        >>> def should_bold(text):
        ...     return text.startswith("IMPORTANT")
        >>> colorer = Colorer(bold=should_bold)
        >>> text = colorer.red("IMPORTANT: Critical error")  # Red and bold
        
        Using color brushes:
        
        >>> red_brush = colorer['red']
        >>> colored = red_brush("This is red text")
    """
    
    COLOR_MAP: ClassVar[dict[str, int]] = dict(
        red=91,
        green=32,
        green2=92,
        yellow=93,
        blue=94,
        cyan=96,
        gray=37,
    )
    Brush: ClassVar[type] = Callable[[str], str]

    _boldworthy: Callable[[str], bool]

    def __init__(self, bold: Union[bool, Callable[[str], bool]] = False):
        """Initialize the Colorer with bold formatting configuration.
        
        Args:
            bold: Controls when text should be bold. Can be:
                 - bool: If True, all text is bold; if False, no text is bold
                 - Callable[[str], bool]: Function that takes text and returns
                   whether it should be bold
        
        Examples:
            >>> # No bold formatting
            >>> colorer = Colorer()
            >>> 
            >>> # All text bold
            >>> colorer = Colorer(bold=True)
            >>> 
            >>> # Conditional bold based on text content
            >>> def bold_keywords(text):
            ...     return text in ['class', 'def', 'import']
            >>> colorer = Colorer(bold=bold_keywords)
        """
        if isinstance(bold, bool):
            self._boldworthy = lambda _: bold
        else:
            self._boldworthy = bold

    @contextlib.contextmanager
    def persist(self, *, bold: bool) -> Generator[None, None, None]:
        """Temporarily override the bold formatting behavior within a context.
        
        Args:
            bold: Whether all text should be bold within this context.
        
        Yields:
            None: Context manager that applies the temporary bold setting.
        
        Examples:
            >>> colorer = Colorer(bold=True)  # Normally bold
            >>> with colorer.persist(bold=False):
            ...     text = colorer.red("Not bold")  # Temporarily not bold
            >>> # Bold behavior restored here
        """
        old_worthy = self._boldworthy
        self._boldworthy = lambda _: bold
        yield
        self._boldworthy = old_worthy

    def _apply(self, text: str, color: int, *, modifiers: tuple[int, ...] = ()) -> str:
        """Apply ANSI color codes and modifiers to text.
        
        This internal method constructs the ANSI escape sequence with the specified
        color and modifiers, applying bold and underline formatting if the text
        is deemed "boldworthy" by the current configuration.
        
        Args:
            text: Text to be colored.
            color: ANSI color code number.
            modifiers: Additional ANSI modifier codes to apply.
        
        Returns:
            str: Text wrapped with appropriate ANSI escape sequences.
        """
        if self._boldworthy(text):
            modifiers = (1, 4, *modifiers, color)
        else:
            modifiers = (*modifiers, color)
        return '\033[' + ';'.join(map(str, modifiers)) + 'm' + text + '\033[0m'

    def __getattr__(self, item: str) -> Brush:
        """Get a color brush function by color name.
        
        Args:
            item: Name of the color to get (must be in COLOR_MAP).
        
        Returns:
            Brush: A function that applies the specified color to text.
        
        Raises:
            NotImplementedError: If the color name is not defined in COLOR_MAP.
        
        Examples:
            >>> colorer = Colorer()
            >>> red_brush = colorer.red
            >>> colored_text = red_brush("Error message")
            >>> 
            >>> # Available colors: red, green, green2, yellow, blue, cyan, gray
            >>> blue_text = colorer.blue("Information")
        """
        if item in self.COLOR_MAP:
            def _brush(text: str) -> str:
                return self._apply(text, self.COLOR_MAP[item])
            _brush.color = item
            return _brush
        raise NotImplementedError(
            f'color {item} undefined; defined colors are: {tuple(self.COLOR_MAP.keys())}'
        )

    def __getitem__(self, item: str) -> Brush:
        """Get a color brush function using bracket notation.
        
        Args:
            item: Name of the color to get (must be in COLOR_MAP).
        
        Returns:
            Brush: A function that applies the specified color to text.
        
        Examples:
            >>> colorer = Colorer()
            >>> red_brush = colorer['red']
            >>> colored_text = red_brush("Error message")
        """
        return self.__getattr__(item)

    def by_number(self, number: int, text: str) -> str:
        """Apply color based on a numeric value for dynamic coloring.
        
        This method generates colors based on numeric input, useful for creating
        consistent color schemes based on depth, index, or other numeric properties.
        
        Args:
            number: Numeric value used to determine the color.
            text: Text to be colored.
        
        Returns:
            str: Text with ANSI color codes applied.
        
        Examples:
            >>> colorer = Colorer()
            >>> # Different colors for different depths
            >>> level_0 = colorer.by_number(0, "root")
            >>> level_1 = colorer.by_number(1, "child")
            >>> level_2 = colorer.by_number(2, "grandchild")
        """
        return self._apply(text, number * 10, modifiers=(38, 5))

    @staticmethod
    def uncolor(text: str) -> str:
        """Remove all ANSI color codes from text.
        
        This utility method strips all ANSI escape sequences from text,
        returning the plain text content without any formatting.
        
        Args:
            text: Text that may contain ANSI color codes.
        
        Returns:
            str: Plain text with all ANSI codes removed.
        
        Examples:
            >>> colored_text = "\\033[91mError\\033[0m message"
            >>> plain_text = Colorer.uncolor(colored_text)
            >>> print(plain_text)  # "Error message"
            >>> 
            >>> # Useful for measuring text length without color codes
            >>> text_length = len(Colorer.uncolor(colored_text))
        """
        return re.sub(r'\033\[[0-9;]*m', '', text)
