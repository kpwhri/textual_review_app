import re

from rich.style import Style
from rich.text import Text
from textual.widgets import Static

from textual_review_app.color import COLOR_TO_TEXT_COLOR, COLOR_TO_BG_COLOR


class HighlighterWidget(Static):
    def __init__(self, precontext, match, postcontext, patterns: list[dict], **kwargs):
        super().__init__(**kwargs)
        self.precontext = precontext
        self.match = match
        self.postcontext = postcontext
        self.patterns = patterns
        self.text = f'{self.precontext}{self.match}{self.postcontext}'

    def render(self) -> Text:
        base_style = Style(color='white')
        text = Text(self.text, style=base_style)
        for pat in self.patterns:
            for m in re.finditer(pat['regex'], self.text, re.I):
                text.stylize(Style(bgcolor=f'{COLOR_TO_BG_COLOR[pat["color"]]}',
                                   color=f'{COLOR_TO_TEXT_COLOR[pat["color"]]}',
                                   bold=True), m.start(), m.end())
        text.stylize(Style(bgcolor='red', bold=True, underline=True, reverse=True),
                     len(self.precontext), len(self.precontext) + len(self.match))
        return text
