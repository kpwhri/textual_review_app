from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class SearchModal(ModalScreen[str | None]):
    BINDINGS = [('escape', 'dismiss', 'Close')]

    def __init__(self):
        super().__init__()
        self._pattern = ''

    def compose(self) -> ComposeResult:
        yield Label('Search (Ctrl+F) — highlights matches temporarily until next change')
        with Vertical():
            self.input = Input(placeholder='Enter regex...', id='search-pattern')
            yield self.input
        with Horizontal():
            yield Button('Search', id='ok', variant='success')
            yield Button('Cancel', id='cancel', variant='error')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok':
            self.dismiss(self.input.value)
        elif event.button.id == 'cancel':
            self.dismiss(None)

    def action_dismiss(self):
        self.dismiss(None)
