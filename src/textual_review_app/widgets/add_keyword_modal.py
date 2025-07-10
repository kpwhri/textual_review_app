"""
Widget to Add Keyword
"""
from textual import on
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Label, Input, Select, Button

from textual_review_app.color import COLOR_NAMES


class AddKeywordModal(ModalScreen):
    def compose(self):
        yield Label('Add Keyword')
        yield Input(placeholder='Enter regex...', id='keyword-regex')
        yield Label('Select Keyword Color')
        yield Select(
            options=[(color, color) for color in COLOR_NAMES],
            prompt='Keyword Color',
            id='keyword-color',
            tooltip='Select Keyword Color',
        )
        with Horizontal():
            yield Button('Add Keyword', id='keyword-add', variant='success')
            yield Button('Cancel', id='keyword-cancel', variant='error')

    @on(Button.Pressed, '#keyword-add')
    def add_keyword_pressed(self):
        self.app.config.add_highlight(
            self.query_one('#keyword-regex').value,
            self.query_one('#keyword-color').value,
        )
        self.app.pop_screen()


    @on(Button.Pressed, '#keyword-cancel')
    def cancel_pressed(self):
        self.app.pop_screen()

