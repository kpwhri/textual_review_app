from rich.style import Style
from rich.text import Text
from textual.widgets import Static


class InstructionWidget(Static):
    BASICS = ['Review each piece of text and select the appropriate option.']

    def __init__(self, instructions, curr_idx=0):
        super().__init__()
        self.instructions = instructions
        self.completed = f'Completed so far: {curr_idx}'

    def render(self) -> Text:
        base_style = Style(color='white')
        text = Text('\n'.join(self.BASICS + [self.completed] + self.instructions), style=base_style)
        return text
