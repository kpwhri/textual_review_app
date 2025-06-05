from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Button


class MetadataModal(ModalScreen):

    def __init__(self, data: dict, title='Metadata'):
        super().__init__()
        self.data = data
        self.title = title

    def compose(self) -> ComposeResult:
        yield Vertical(
            DataTable(id='metadata'),
            Button('Ok', id='ok', variant='primary'),
        )

    async def on_mount(self):
        table = self.query_one('#metadata', DataTable)
        table.add_columns('Element', 'Value')
        for k, v in self.data.items():
            table.add_row(str(k), str(v)[:50])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok':
            self.dismiss()
