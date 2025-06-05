from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Input


class ResponseWidget(Widget):

    def __init__(self, options: list, **kwargs):
        super().__init__(**kwargs)
        self.options = options

    def compose(self):
        with Vertical():
            with Horizontal():
                for i, option in enumerate(self.options):
                    yield Button(f'{option}', id=f'button-{i}')
            yield Input(placeholder='Add comment...', id='comment')
