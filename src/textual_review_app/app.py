from pathlib import Path

from loguru import logger
from textual import on

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Label, Button

from textual_review_app.annotation_store import AnnotationStore
from textual_review_app.config import Config
from textual_review_app.corpus import Corpus
from textual_review_app.widgets.add_keyword_modal import AddKeywordModal
from textual_review_app.widgets.info_modal import InfoModal
from textual_review_app.widgets.metadata_modal import MetadataModal
from textual_review_app.widgets.snippet_widget import SnippetWidget
from textual_review_app.widgets.toggle_button import ToggleButton


class ReviewApp(App):
    CSS_PATH = 'css/app.tcss'

    curr_idx = reactive(0)
    current_entry = reactive(dict)

    def __init__(self, config_path: Path):
        super().__init__()
        self.config = Config(config_path)
        self.corpus = Corpus(self.config.corpus_path)
        self.wksp_path = config_path.parent
        self.annotations = AnnotationStore(self.config.corpus_path.parent / 'annotations.db')
        self.snippet_widget: SnippetWidget = None
        self.progress_label: Label = None
        self.current_meta1 = None
        self.current_meta2 = None
        self.current_meta3 = None
        self.current_annot = None
        self.header = None
        self.response_buttons = [
            ToggleButton(f'{option}', id=f'button-{i}', classes='responsebtn')
            for i, option in enumerate(self.config.options)
        ]
        self.show_instructions = True
        self.current_display_metadata = list()

    def compose(self) -> ComposeResult:
        self.header = Header(name=self.config.title)

        # header info
        self.current_meta1 = Label('', id='current-md1')
        self.current_meta2 = Label('Instructions', id='current-md2')
        self.current_meta3 = Label('', id='current-md3')
        self.progress_label = Label('', id='progress-label')
        yield Container(
            Button('Metadata', id='metadata-btn', classes='orange-btn'),
            Container(
                self.current_meta1,
                self.current_meta2,
                self.current_meta3,
                self.progress_label,
                classes='horizontal-layout',
            ),
            Button('Instructions', id='instructions-btn', classes='yellow-btn'),
            id='topbar',
            classes='horizontal-layout',
        )

        # snippet
        self.snippet_widget = SnippetWidget(self.config)
        yield self.snippet_widget

        # button bars
        with Vertical(id='bottom'):
            with Horizontal(classes='buttonbar'):
                yield Button('Save & Exit', variant='default', id='exit')
                yield Button('Previous', variant='warning', id='previous')
                yield Button('Add Highlight', variant='error', id='highlight-keyword')
                yield Button('Save', variant='success', id='save')
                yield Button('Save & Next', variant='primary', id='next')
            with Horizontal(classes='buttonbar'):
                for response in self.response_buttons:
                    yield response

        yield Footer()

    async def on_mount(self):
        self.curr_idx = self.config.offset
        percent_done = self.curr_idx / len(self.corpus) * 100
        self.progress_label.update(f'Completed {self.curr_idx} / {len(self.corpus)} ({percent_done:.2f}%)')
        self.header.title = self.config.title

    async def watch_curr_idx(self, idx: int):
        if idx < 0:
            self.curr_idx = 0
            await self.push_screen(InfoModal([
                'You have reached the first record.',
                'Unable to go back any further.',
            ], title='No Previous Records'))
        elif idx >= len(self.corpus):
            self.curr_idx = len(self.corpus) - 1
            await self.push_screen(InfoModal([
                f'Congratulations! You have finished all {len(self.corpus)} records.'
                'You have finished the last record.',
                'Review has been completed, though you can go back.',
            ], title='Finished Review'))
        else:
            self.config.offset = self.curr_idx
            self.current_entry = self.corpus[idx]
            self.current_annot = self.annotations.get(idx)

    def save(self):
        self.current_annot.comment = self.snippet_widget.get_comment()
        self.current_annot.selected = [
            str(btn.label) for btn in self.response_buttons if 'responsebtn-checked' in btn.classes
        ]
        self.annotations.save(self.curr_idx, self.current_annot)

    async def update_display(self):
        if self.curr_idx < 0:
            self.curr_idx = 0
        await self.snippet_widget.update_entry(self.current_entry, self.current_annot.comment, self.current_annot.marks)
        # update selection
        for response in self.response_buttons:
            response.set_selected(response.label in self.current_annot.selected)
        # update header
        display_metadata = [
            str(v)[:20] for k, v in self.current_entry.items()
            if k not in {'match', 'precontext', 'postcontext', 'pretext', 'posttext'}
        ]
        self.current_meta1.update(display_metadata[0])
        self.current_meta2.update(display_metadata[1])
        self.current_meta3.update(display_metadata[2])
        percent_done = self.curr_idx / len(self.corpus) * 100
        self.progress_label.update(f'Record #{self.curr_idx + 1} / {len(self.corpus)} ({percent_done:.2f}%)')


    @on(Button.Pressed, '#highlight-keyword')
    def open_add_keyword_dialog(self):
        self.push_screen(AddKeywordModal(self.snippet_widget.get_selected_text()))

    @on(Button.Pressed, '#next')
    async def get_next_record(self):
        if self.show_instructions:
            self.show_instructions = False
        else:
            self.save()
            self.curr_idx += 1
            if self.curr_idx >= len(self.corpus):
                self.curr_idx = len(self.corpus) - 1
                await self.push_screen(InfoModal([
                    f'Congratulations! You have finished all {len(self.corpus)} records.'
                    'You have finished the last record.',
                    'Review has been completed, though you can go back.',
                ], title='Finished Review'))
        await self.update_display()

    @on(Button.Pressed, '#save')
    async def save_record(self):
        if not self.show_instructions:
            self.save()

    @on(Button.Pressed, '#exit')
    async def save_and_exit_record(self):
        if not self.show_instructions:
            self.save()
        self.exit()

    @on(Button.Pressed, '#previous')
    async def previous_record(self):
        if self.show_instructions:
            self.show_instructions = False
        else:
            self.save()
            self.curr_idx -= 1
            if self.curr_idx < 0:
                self.curr_idx = 0
                await self.push_screen(InfoModal([
                    'You have reached the first record.',
                    'Unable to go back any further.',
                ], title='No Previous Records'))
        await self.update_display()

    @on(Button.Pressed, '#metadata-btn')
    async def show_metadata(self):
        if self.show_instructions:
            await self.push_screen(InfoModal(self.config.instructions, title='Instructions Page'))
        else:
            await self.push_screen(MetadataModal(self.current_entry))

    @on(Button.Pressed, '#instructions-btn')
    async def show_instructions(self):
        await self.push_screen(InfoModal(self.config.instructions, title='Instructions'))


def main():
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('config_path', type=Path,
                        help='Path to config file (its directory will be the workspace directory).')
    args = parser.parse_args()

    config_path = args.config_path
    if config_path.exists():
        app = ReviewApp(config_path)
        app.run()
        # on exit, export database
        app.annotations.export()
    else:
        logger.error(f'Configuration file does not exist! {config_path}')
        logger.warning(f'Creating default configuration at {config_path}')
        config_path.parent.mkdir(exist_ok=True)
        Config(config_path).save()


if __name__ == '__main__':
    main()
