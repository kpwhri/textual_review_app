from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class GoToModal(ModalScreen):
    BINDINGS = [('escape', 'dismiss', 'Close')]

    def __init__(self, reviewed_ids: list[int], total: int):
        super().__init__()
        self.reviewed_ids = reviewed_ids
        self.total = total

    def compose(self) -> ComposeResult:
        yield Label('Jump to a previously reviewed record:')
        with Vertical():
            if not self.reviewed_ids:
                yield Label('No reviewed records yet.')
            else:
                # show rows in groups of 10 per row for compactness
                row: list[int] = []
                for idx in self.reviewed_ids:
                    row.append(idx)
                    if len(row) == 10:
                        yield self._row_buttons(row)
                        row = []
                if row:
                    yield self._row_buttons(row)
        yield Horizontal(Button('Close', id='ok', variant='primary'))

    def _row_buttons(self, indices: list[int]) -> Horizontal:
        buttons = []
        for idx in indices:
            # 1-based label for humans
            label = f'#{idx + 1}'
            buttons.append(Button(label, id=f'goto-{idx}', classes='goto-reviewed'))
        return Horizontal(*buttons)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok':
            self.dismiss()

    def action_dismiss(self):
        self.dismiss()
