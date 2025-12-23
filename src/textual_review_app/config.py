import random
from pathlib import Path

import tomlkit
from rich.text import Text
from textual.style import Style
from textual.widgets import Label


def _generate_username():
    names = ['marjatta', 'louhi', 'ukko', 'kaleva', 'hiisi', 'aino',
             'joukahainen', 'ilmatar', 'annikki', 'tapio',
             'tellervo', 'tuonetar', 'ikuturso', 'ilmarinen', 'väinämöinen']
    return f'{random.choice(names)}{random.randint(1, 100)}'


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
            'first_run': True,
            'user': None,
            'font_scale': 1.0,
            'snippets': [],
            'mark_colors': {
                'mark': 'blue',
                'negated': 'orange',
            },
        }
        self.load()
        if not self.data['user']:
            self.data['user'] = _generate_username()

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

    def add_snippet(self, text: str):
        self.data['snippets'].append(text)
        self.save()

    @property
    def mark_colors(self):
        return self.data['mark_colors']

    @property
    def options(self):
        return self.data['options']

    @property
    def instructions(self):
        return self.data['instructions']

    @property
    def corpus_path(self):
        return self.path.parent / self.data['corpus']

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

    @property
    def user(self) -> str:
        return self.data['user']

    @user.setter
    def user(self, value: str):
        self.data['user'] = value
        self.save()

    @property
    def font_scale(self) -> float:
        return float(self.data.get('font_scale', 1.0))

    @font_scale.setter
    def font_scale(self, value: float):
        self.data['font_scale'] = float(value)
        self.save()

    @property
    def first_run(self) -> bool:
        return bool(self.data.get('first_run', True))

    @first_run.setter
    def first_run(self, value: bool):
        self.data['first_run'] = bool(value)
        self.save()
