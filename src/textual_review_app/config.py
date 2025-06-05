from pathlib import Path

import tomlkit
from rich.text import Text
from textual.style import Style
from textual.widgets import Label


class Config:

    def __init__(self, path: Path):
        self.path = path
        self.data = {
            'title': 'Review App',
            'offset': 0,
            'corpus': 'review.jsonl',
            'highlights': [],
            'instructions': [],
            'options': [],
        }
        self.load()

    def load(self):
        if self.path.exists():
            with open(self.path) as fh:
                self.data |= tomlkit.load(fh)
        else:
            raise ValueError(f'Configuration file does not exist: {self.path}')

    def save(self):
        with open(self.path, 'w') as out:
            tomlkit.dump(self.data, out)

    def add_highlight(self, value, color):
        self.data['highlights'].append({'regex': value, 'color': color})
        self.save()

    @property
    def options(self):
        return self.data['options']

    @property
    def instructions(self):
        return [
            Label('Press [skyblue]"Save & Next"[/skyblue] to start review.'),
            Label('Review the [red][highlight][underline]red highlighted and underlined text[/red][/highlight][/underline] and choose the best response option.'),
            Label('* [orange][bold]Previous[/bold][/orange]: save and go back to previous record *'),
            Label('* [red][bold]Add Highlight[/bold][/red]: add regular expressions to highlight in the text *'),
            Label('* [green][bold]Save[/bold][/green]: save current record *'),
            Label('* [skyblue][bold]Save & Next[/bold][/skyblue]: save current record and open next *'),
            Label('* Press [bold]Ctrl+Q[/bold] to quit *'),
            Label(''),
        ] + self.data['instructions']

    @property
    def corpus_path(self):
        return self.path.parent /  self.data['corpus']

    @property
    def title(self):
        return self.data['title']

    @title.setter
    def title(self, value: str):
        self.data['title'] = value
        self.save()

    @property
    def offset(self):
        return self.data['offset']

    @offset.setter
    def offset(self, value: int):
        self.data['offset'] = value
        self.save()

    @property
    def highlights(self):
        return self.data['highlights']

    @highlights.setter
    def highlights(self, value: list[dict]):
        self.data['highlights'] = value
        self.save()
