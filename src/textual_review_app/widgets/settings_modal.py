from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea


class SettingsModal(ModalScreen[dict]):
    BINDINGS = [('escape', 'dismiss', 'Close')]

    def __init__(self, font_scale: float, user: str, canned_responses: list[str]):
        super().__init__()
        self._font_scale = str(font_scale)
        self._user = user
        self._canned_responses = '\n'.join(canned_responses)

    def compose(self) -> ComposeResult:
        yield Label('Settings')
        with Vertical():
            yield Label('Font scale (e.g., 1.0, 1.2, 0.9)')
            self.font_input = Input(value=self._font_scale, id='font-scale')
            yield self.font_input
            yield Label('Username:')
            self.user_input = Input(value=self._user, id='user')
            yield self.user_input
            yield Label('Canned responses (one per line):')
            self.canned_input = TextArea(self._canned_responses, id='canned-responses')
            yield self.canned_input
        with Horizontal():
            yield Button('Save', id='ok', variant='success')
            yield Button('Cancel', id='cancel', variant='error')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok':
            values = {
                'font_scale': self.font_input.value,
                'user': self.user_input.value,
                'canned_responses': [r for r in self.canned_input.text.split('\n') if r.strip()],
            }
            self.dismiss(values)
        elif event.button.id == 'cancel':
            self.dismiss()

    def action_dismiss(self):
        self.dismiss()
