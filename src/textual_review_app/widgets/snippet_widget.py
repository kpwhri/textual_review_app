from rich.text import Text
from textual import on
from textual import log
from textual.containers import Vertical, VerticalScroll, Horizontal, Container
from textual.events import MouseDown, Key
from textual.widget import Widget
from textual.widgets import Button, Static, TextArea, Label, Select

from textual_review_app.config import Config
from textual_review_app.widgets.highlighter_widget import HighlighterWidget
from textual_review_app.widgets.mark_modal import MarkModal


class SnippetWidget(Widget):
    PRETEXT = 'pretext'
    POSTTEXT = 'posttext'
    MATCH = 'match'
    PRE = 'precontext'
    POST = 'postcontext'
    MARKS = 'marks'

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.entry = {}
        self.config = config
        self.show_full_text_pre = False
        self.show_full_text_post = False
        self.scroll = None
        self.comment = ''
        self.comment_area = TextArea(id='comment')
        self.instructions = [
            line if isinstance(line, Label) else Label(str(line)) for line in self.config.instructions
        ]
        self.marks = []

    def compose(self):
        with Horizontal():
            with Vertical(classes='left-dock'):
                yield Button('Hide Before' if self.show_full_text_pre else 'Show Before',
                             id='pretext-button', classes='textbtn float-top purple-btn')
                yield Label('Comments', id='comment-label')
                yield self.comment_area
                yield Button('Hide After' if self.show_full_text_post else 'Show After',
                             id='posttext-button', classes='textbtn float-bottom purple-btn')
            self.scroll = VerticalScroll(
                Container(*self.instructions, id='textfield'),
            )
            yield self.scroll

    async def update_entry(self, entry=None, comment=None, marks=None):
        if entry is not None:
            self.show_full_text_pre = False
            self.show_full_text_post = False
            self.entry = entry

        if marks is not None:
            self.marks = marks
        await self.scroll.query_one('#textfield').remove()
        await self.scroll.mount(
            HighlighterWidget(
                self.entry[self.PRETEXT if self.show_full_text_pre else self.PRE],
                self.entry[self.MATCH],
                self.entry[self.POSTTEXT if self.show_full_text_post else self.POST],
                self.config.highlights,
                self.marks,
                self.config.mark_colors,
                id='textfield',
            ) if self.entry is not None else Static(Text('Press next to continue.'), id='textfield'),
        )
        if comment is not None:
            self.comment = comment
            self.comment_area.text = comment

    def get_comment(self):
        return self.comment_area.text

    @on(Button.Pressed, '#pretext-button')
    async def reveal_pretext(self):
        if self.show_full_text_pre:
            self.query_one('#pretext-button').label = 'Show Before'
            self.show_full_text_pre = False
        else:
            self.query_one('#pretext-button').label = 'Hide Before'
            self.show_full_text_pre = True
        await self.update_entry()

    @on(Button.Pressed, '#posttext-button')
    async def reveal_posttext(self):
        if self.show_full_text_post:
            self.query_one('#posttext-button').label = 'Show After'
            self.show_full_text_post = False
        else:
            self.query_one('#posttext-button').label = 'Hide After'
            self.show_full_text_post = True
        await self.update_entry()

    @on(Key)
    async def handle_annotation(self, event: Key) -> None:
        if event.key == 'enter':  # enter
            widget = self.scroll.query_one('#textfield')
            await self.app.push_screen(
                MarkModal(widget.selection_start, widget.selection_end, widget.selection),
                lambda x: self.update_entry(marks=x),
            )
