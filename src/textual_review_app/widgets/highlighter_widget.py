import re
import sys

from rich._palettes import EIGHT_BIT_PALETTE, STANDARD_PALETTE, WINDOWS_PALETTE
from rich.color import ANSI_COLOR_NAMES
from rich.style import Style
from textual.widgets import Static, TextArea

from textual_review_app.color import COLOR_TO_TEXT_COLOR, COLOR_TO_BG_COLOR, COLOR_NAMES

IS_WINDOWS = sys.platform == 'win32'


def style_from_color(color, bold=True):
    return Style(bgcolor=f'{COLOR_TO_BG_COLOR[color]}',
                 color=f'{COLOR_TO_TEXT_COLOR[color]}',
                 bold=bold)


class HighlightTextArea(TextArea):
    """Adapted from https://github.com/Textualize/textual/discussions/5336"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lines = self.text.splitlines(keepends=True)
        rich_colors = sorted((v, k) for k, v in ANSI_COLOR_NAMES.items() if k in COLOR_NAMES)

        for color_number, name in rich_colors:
            palette = (
                WINDOWS_PALETTE
                if IS_WINDOWS and color_number < 16
                else STANDARD_PALETTE
                if color_number < 16
                else EIGHT_BIT_PALETTE
            )
            color = palette[color_number]
            self._theme.syntax_styles[name] = style_from_color(name)
        self._theme.syntax_styles['target'] = Style(bgcolor='red', bold=True, underline=True, reverse=True)

    def stylize_by_row(self, color: str, row: int, start_column: int, end_column: int) -> None:
        self._highlights[row].append((start_column, end_column, color))

    def stylize(self, color: str, start: int, end: int) -> None:
        """Stylize by index in text"""
        line_start = 0
        for row, line in enumerate(self.lines):
            line_end = line_start + len(line)
            if start > line_end:
                pass  # need to increment
            elif end > line_end:  # across two lines
                self.stylize_by_row(color, row, start - line_start, line_end)
                start = line_end  # set for next line
            else:
                self.stylize_by_row(color, row, start - line_start, end - line_start)
                break
            line_start = line_end

    def get_char_offset(self, row: int, row_index: int):
        curr_chars = 0
        if row >= len(self.lines):
            raise ValueError(f'Requested row is too large!')
        for _row, line in enumerate(self.lines):
            if _row == row:
                return curr_chars + row_index
            curr_chars += len(line)



class HighlighterWidget(Static):
    def __init__(self, precontext, match, postcontext, patterns: list[dict], marks: list[dict], mark_colors: dict,
                 **kwargs):
        super().__init__(**kwargs)
        self.precontext = precontext
        self.match = match
        self.postcontext = postcontext
        self.patterns = patterns
        self.marks = marks
        self.mark_colors = mark_colors
        self.text = f'{self.precontext}{self.match}{self.postcontext}'
        self.textbox: HighlightTextArea = None

    @property
    def selection_start(self):
        return self.textbox.get_char_offset(*self.textbox.selection.start) - len(self.precontext)

    @property
    def selection_end(self):
        return self.textbox.get_char_offset(*self.textbox.selection.end) - len(self.precontext)

    @property
    def selection(self):
        return self.textbox.get_text_range(self.textbox.selection.start, self.textbox.selection.end)

    def compose(self):
        self.textbox = HighlightTextArea(self.text, read_only=True)
        for pat in self.patterns:
            for row, line in enumerate(self.textbox.lines):
                for m in re.finditer(pat['regex'], line, re.I):
                    self.textbox.stylize_by_row(pat['color'], row, m.start(), m.end())
        for mark in self.marks:
            # indices are based on the 'match' section
            start = mark['start'] + len(self.precontext)
            end = mark['end'] + len(self.precontext)
            if start > len(self.text):
                # is in postcontext and postcontext not shown
                continue
            elif start < 0:
                # is in precontext and precontext not shown
                continue

            self.textbox.stylize(
                self.mark_colors.get(mark['kind'], 'skyblue'),
                start,
                end)
        self.textbox.stylize('target', len(self.precontext), len(self.precontext) + len(self.match))
        yield self.textbox
