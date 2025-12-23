from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input


class GoToModal(ModalScreen):
    BINDINGS = [('escape', 'dismiss', 'Close')]

    def __init__(self, reviewed_ids: list[int], total: int):
        super().__init__()
        self.reviewed_ids = reviewed_ids  # up to 15
        self.total = total

    def compose(self) -> ComposeResult:
        yield Label('Jump to a previously reviewed record:')
        self.record_input = Input(placeholder='Record number', id='record_number', max_length=10)
        yield Horizontal(
            self.record_input,
            Button('Open', id='open', classes='goto-reviewed', variant='success'),
        )
        with Vertical():
            if not self.reviewed_ids:
                yield Label('No reviewed records yet.')
            else:
                yield Label('Recently reviewed:')
                # show rows in groups of 5 per row for compactness
                row: list[int] = []
                for idx in self.reviewed_ids:
                    row.append(idx)
                    if len(row) == 5:
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
        elif event.button.id.startswith('goto'):
            record_id = int(event.button.id.split('-', 1)[1])
            self.dismiss(record_id)
        elif event.button.id == 'open':
            val = self.record_input.value
            try:
                # translate from human 1-based index to 0-based
                self.dismiss(int(val) - 1)
            except ValueError as e:
                self.dismiss(f'Invalid number: {val}')

    def action_dismiss(self):
        self.dismiss()
