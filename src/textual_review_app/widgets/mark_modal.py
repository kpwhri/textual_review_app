from textual import on
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Label, TextArea, Select, Button


class MarkModal(ModalScreen):

    def __init__(self, start, end, selection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end
        self.selection = selection

    def compose(self):
        yield TextArea(f'{self.selection}', compact=True)
        yield Label('Select Annotation Type')
        yield Select(
            options=[
                ('Mark', 'mark'),
                ('Negated', 'negated'),
            ],
            prompt='Annotation Type',
            id='keyword-type',
            tooltip='Select Annotation Type',
            value='mark',
        )
        with Horizontal():
            yield Button('Add Annotation', id='keyword-add', variant='success')
            yield Button('Cancel', id='keyword-cancel', variant='error')

    @on(Button.Pressed, '#keyword-add')
    def add_keyword_pressed(self):
        self.app.current_annot.add_mark(self.start, self.end, self.selection, self.query_one('#keyword-type').value)
        self.dismiss(self.app.current_annot.marks)

    @on(Button.Pressed, '#keyword-cancel')
    def cancel_pressed(self):
        self.app.pop_screen()
