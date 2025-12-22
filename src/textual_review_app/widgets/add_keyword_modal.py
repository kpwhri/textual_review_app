"""
Widget to Add Keyword
"""
import re

from textual import on
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Input, Select, Button, TextArea

from textual_review_app.color import COLOR_NAMES


class AddKeywordModal(ModalScreen):

    def __init__(self, selected_text: str = ''):
        super().__init__()
        self.selected_text = f'{selected_text}' if selected_text else ''

    def compose(self):
        yield TextArea('Use a regular expression to highlight words and phrases across all notes.'
                       ' Provide a regular expression, select a highlight color, and then press'
                       ' "Add Keyword".'
                       f'\nYou selected the following text: \n{self.selected_text}',
                       disabled=True)
        yield Label('Add Keyword')
        yield Input(placeholder='Enter regex...', id='keyword-regex')
        yield Label('Select Keyword Color')
        yield Select(
            options=[(color, color) for color in COLOR_NAMES],
            prompt='Keyword Color',
            id='keyword-color',
            tooltip='Select Keyword Color',
        )
        with Vertical():
            with Horizontal():
                yield Button('Test Regex', id='keyword-test', variant='default')
                yield Input(value=self.selected_text[:50] or None,
                            placeholder='Text to test regex on.',
                            id='keyword-test-text')
            with Horizontal():
                yield Button('Clear Test Response', id='keyword-test-response-clear')
                self._keyword_test_response = Label('', id='keyword-test-response')
                yield self._keyword_test_response
        # add keyword/cancel at the bottom
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

    @on(Button.Pressed, '#keyword-test')
    def test_regex_pressed(self):
        pattern = self.query_one('#keyword-regex').value
        target = self.query_one('#keyword-test-text').value
        if not target.strip():
            self._keyword_test_response.update('ERROR: No test text.')
        else:
            rx = re.compile(pattern, re.I | re.MULTILINE)
            m = rx.search(target)
            if m is None:
                self._keyword_test_response.update(f'Failed to find match: {m}')
            else:
                self._keyword_test_response.update(f'Success! Found match: {m}')

    @on(Button.Pressed, '#keyword-test-response-clear')
    def clear_test_response(self):
        self._keyword_test_response.update('')
