"""
You reached the start of the review alert modal.
"""
from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Button


class InfoModal(ModalScreen):

    def __init__(self, lines, title='Info'):
        super().__init__()
        if isinstance(lines, list):
            self.message = [line if isinstance(line, Label) else Label(str(line)) for line in lines]
        else:
            self.message = [lines if isinstance(lines, Label) else Label(lines)]
        self.title = title

    def compose(self) -> ComposeResult:
        yield Label(Text(self.title, style=Style(bold=True, underline=True)))
        with Vertical():
            for msg in self.message:
                yield msg
        yield Button('Ok', id='ok', variant='primary')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok':
            self.dismiss()
