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
from textual_review_app.widgets.settings_modal import SettingsModal
from textual_review_app.widgets.search_modal import SearchModal


class ReviewApp(App):
    CSS_PATH = 'css/app.tcss'
    BINDINGS = [
        ('ctrl+s', 'save', 'Save'),
        ('ctrl+right', 'save_next', 'Save & Next'),
        ('ctrl+left', 'previous', 'Previous'),
        ('ctrl+f', 'search', 'Search'),
        ('ctrl+r', 'toggle_flag', 'Flag Record'),
        ('ctrl+l', 'open_canned_responses', 'Canned Responses'),
    ]

    curr_idx = reactive(0)
    current_entry = reactive(dict)

    def __init__(self, config_path: Path):
        super().__init__()
        self.config = Config(config_path)
        self.corpus = Corpus(self.config.corpus_path)
        self.wksp_path = config_path.parent
        self.annotations = AnnotationStore(self.config.corpus_path.parent / 'annotations.db', user=self.config.user)
        self.snippet_widget: SnippetWidget = None
        self.progress_label: Label = None
        self.last_saved_label: Label = None
        self.current_meta1 = None
        self.current_meta2 = None
        self.current_meta3 = None
        self.current_annot = None
        self.header = None
        self.response_buttons = [
            ToggleButton(f'{option}', id=f'button-{i}', classes='responsebtn')
            for i, option in enumerate(self.config.options)
        ]
        self.current_display_metadata = list()

    def compose(self) -> ComposeResult:
        self.header = Header(name=self.config.title)

        # header info
        self.current_meta1 = Label('', id='current-md1')
        self.current_meta2 = Label('Instructions', id='current-md2')
        self.current_meta3 = Label('', id='current-md3')
        self.progress_label = Label('', id='progress-label')
        self.last_saved_label = Label('', id='last-saved-label')
        yield Vertical(
            Container(
                Button('Metadata', id='metadata-btn', classes='orange-btn'),
                Button('Instructions', id='instructions-btn', classes='yellow-btn'),
                Button('Settings', id='settings-btn', classes='yellow-btn'),
                Button('Go To Reviewed', id='goto-reviewed-btn', classes='blue-btn'),
                id='buttonbar',
                classes='horizontal-layout',
            ),
            Container(
                self.current_meta1,
                self.current_meta2,
                self.current_meta3,
                self.progress_label,
                self.last_saved_label,
                id='infobar',
                classes='horizontal-layout',
            ),
            id='topbar',
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
                # toggle review flag button (green when unflagged, red when flagged)
                yield Button('Flag', variant='success', id='flag-toggle')
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
        # apply font scale
        try:
            self.styles.scale = float(self.config.font_scale)
        except Exception:
            pass
        # getting started overlay will be shown from Instructions button on first use to avoid blocking flows
        recovery_file = self.wksp_path / '.recovery.json'
        if recovery_file.exists():
            import json
            try:
                data = json.loads(recovery_file.read_text(encoding='utf8'))
                idx = int(data.get('idx', 0))
                self.curr_idx = max(0, min(idx, len(self.corpus) - 1))
                self.current_entry = self.corpus[self.curr_idx]
                self.current_annot = AnnotationStore.Annotation if False else None
                # load comment/selected/marks into current_annot
                from textual_review_app.annotation_store import Annotation
                self.current_annot = Annotation(self.curr_idx, json.dumps(data.get('annotation', {})))
                await self.update_display()
                await self.push_screen(InfoModal('Recovered unsaved session state.', title='Recovery'))
            except Exception:
                pass
            finally:
                try:
                    recovery_file.unlink(missing_ok=True)
                except Exception:
                    pass

    async def on_ready(self):
        """Called when the app is fully loaded and ready."""
        # showing a modal once the app has finished loading
        await self.update_display()
        await self.show_instructions()

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
            if self.is_mounted:
                await self.update_display()

    def save(self):
        comment = self.snippet_widget.get_comment()
        self.current_annot.comment = comment
        self.current_annot.selected = [
            str(btn.label) for btn in self.response_buttons if 'responsebtn-checked' in btn.classes
        ]
        self.annotations.save(self.curr_idx, self.current_annot)
        # update last saved timestamp and toast
        from datetime import datetime
        self.last_saved_label.update(f'Last saved: {datetime.now().strftime("%H:%M:%S")}')
        self.notify('Saved', severity='information', timeout=2)

    async def update_display(self):
        if self.curr_idx < 0:
            self.curr_idx = 0
        await self.snippet_widget.update_entry(self.current_entry, self.current_annot.comment, self.current_annot.marks)
        # Update comment area explicitly to ensure it matches current annotation
        self.snippet_widget.comment_area.text = self.current_annot.comment
        # update selection
        for response in self.response_buttons:
            response.set_selected(response.label in self.current_annot.selected)
        # update header
        display_metadata = [
            str(v)[:20] for k, v in self.current_entry.items()
            if k not in {'match', 'precontext', 'postcontext', 'pretext', 'posttext'}
        ]
        self.current_meta1.update(display_metadata[0])
        if len(display_metadata) > 1:
            self.current_meta2.update(display_metadata[1])
        if len(display_metadata) > 2:
            self.current_meta3.update(display_metadata[2])
        percent_done = self.curr_idx / len(self.corpus) * 100
        self.progress_label.update(f'Record #{self.curr_idx + 1} / {len(self.corpus)} ({percent_done:.2f}%)')
        # sync review flag button state
        try:
            self._update_flag_button()
        except Exception:
            pass

    @on(Button.Pressed, '#highlight-keyword')
    def open_add_keyword_dialog(self):
        self.push_screen(AddKeywordModal(self.snippet_widget.get_selected_text()))

    @on(Button.Pressed, '#next')
    async def get_next_record(self):
        self.save()
        self.curr_idx += 1

    @on(Button.Pressed, '#save')
    async def save_record(self):
        self.save()

    @on(Button.Pressed, '#exit')
    async def save_and_exit_record(self):
        self.save()
        self.exit()

    @on(Button.Pressed, '#previous')
    async def previous_record(self):
        self.save()
        self.curr_idx -= 1

    @on(Button.Pressed, '#metadata-btn')
    async def show_metadata(self):
        await self.push_screen(MetadataModal(self.current_entry))

    @on(Button.Pressed, '#canned-btn')
    def action_open_canned_responses(self):
        from textual_review_app.widgets.canned_response_modal import CannedResponseModal
        self.push_screen(CannedResponseModal(self.config.canned_responses), self.handle_canned_response)

    def handle_canned_response(self, response: str | None):
        if response is None:
            return

        if response.startswith('ADD:'):
            new_response = response[4:]
            if new_response not in self.config.canned_responses:
                self.config.canned_responses.append(new_response)
                self.config.save()
            response = new_response

        current_comment = self.snippet_widget.get_comment()
        if current_comment:
            if not current_comment.endswith('\n'):
                current_comment += '\n'
            new_comment = current_comment + response
        else:
            new_comment = response

        self.snippet_widget.comment_area.text = new_comment
        self.snippet_widget.comment_area.focus()

    @on(Button.Pressed, '#instructions-btn')
    async def show_instructions(self):
        await self.push_screen(InfoModal(
            [
                '[b]Welcome to the Textual Review App![/b]',
                '',
                '[b]Instructions:[b]',
                'Review the [red][highlight][underline]red highlighted and underlined text[/red][/highlight][/underline] and choose the best response option.'
                '',
                'Use the buttons at the bottom to annotate the corpus:',
                ' • [b]Save & Next[/b]: Save current work and move to the next record.',
                ' • [b]Save[/b]: Save your progress without moving.',
                ' • [b]Previous[/b]: Go back to the preceding record.',
                ' • [b]Flag[/b]: Mark records for further review.',
                ' • [b]Add Highlight[/b]: Add custom highlights to the text.',
                '',
                '[b]Keyboard Shortcuts:[/b]',
                ' • [yellow]Ctrl+S[/yellow]: Save current record',
                ' • [yellow]Ctrl+→[/yellow]: Save and go to next',
                ' • [yellow]Ctrl+←[/yellow]: Go to previous',
                ' • [yellow]Ctrl+F[/yellow]: Search',
                ' • [yellow]Ctrl+R[/yellow]: Toggle flag',
                ' • [yellow]Ctrl+l[/yellow]: When in comments, open canned responses.',
                '',
                '[b]Here are your project-specific instructions:[/b]',
            ] + self.config.instructions +[
                '',
                'Press [b]OK[/b] to get started.',
            ],
            title='Instructions'))

    @on(Button.Pressed, '#settings-btn')
    async def open_settings(self):
        async def _apply_settings(values: dict):
            if not values:
                return  # 'cancel'
            # values keys: 'font_scale', 'user', 'canned_responses'
            try:
                self.config.font_scale = float(values.get('font_scale', self.config.font_scale))
                self.styles.scale = self.config.font_scale
            except Exception:
                pass
            user = values.get('user')
            if user:
                self.config.user = user
                self.annotations.user = user

            if 'canned_responses' in values:
                self.config.canned_responses = values['canned_responses']

        await self.push_screen(
            SettingsModal(self.config.font_scale, self.config.user, self.config.canned_responses),
            _apply_settings
        )

    @on(Button.Pressed, '#goto-reviewed-btn')
    async def open_goto(self):
        from textual_review_app.widgets.goto_modal import GoToModal
        async def _send_to_record_id(result=None):
            """result: str interpreted as message, int as record_id to navigate to"""
            if isinstance(result, str):
                self.notify(result, severity='error')
            elif isinstance(result, int):
                if self.annotations.exists(result):
                    self.curr_idx = result
                    await self.update_display()
                else:
                    await self.push_screen(InfoModal([
                        f'Record #{result + 1} has not been reviewed yet.',
                        'You can only jump to records that were already saved.'
                    ], title='Unreviewed Record'))

        reviewed = self.annotations.recent_reviewed_ids(15)
        await self.push_screen(GoToModal(reviewed, total=len(self.corpus)), _send_to_record_id)

    async def action_save(self):
        await self.save_record()

    async def action_save_next(self):
        await self.get_next_record()

    async def action_previous(self):
        await self.previous_record()

    async def action_search(self):
        async def _apply_search(pattern: str):
            if pattern:
                self.snippet_widget.set_temp_highlights([{'regex': pattern, 'color': 'yellow'}])
                await self.update_display()

        await self.push_screen(SearchModal(), _apply_search)

    async def action_toggle_flag(self):
        self.current_annot.flagged = not getattr(self.current_annot, 'flagged', False)
        try:
            msg = 'Flagged' if self.current_annot.flagged else 'Unflagged'
            self.notify(f'{msg} record', severity='warning' if self.current_annot.flagged else 'information')
        except Exception:
            pass
        # update button state immediately
        try:
            self._update_flag_button()
        except Exception:
            pass

    def _update_flag_button(self):
        btn = self.query_one('#flag-toggle', Button)
        if getattr(self.current_annot, 'flagged', False):
            btn.variant = 'error'  # red
            btn.label = 'Flagged'
        else:
            btn.variant = 'success'  # green
            btn.label = 'Flag'

    @on(Button.Pressed, '#flag-toggle')
    async def on_flag_toggle_pressed(self):
        await self.action_toggle_flag()


def main():
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('config_path', type=Path,
                        help='Path to config file (its directory will be the workspace directory).')
    parser.add_argument('--sample', action='store_true', help='Generate a sample workspace for exploration.')
    args = parser.parse_args()

    config_path = args.config_path
    if args.sample:
        # generate sample workspace
        wksp = config_path.parent
        wksp.mkdir(parents=True, exist_ok=True)
        # copy example corpus
        from shutil import copy2
        from pathlib import Path as _Path
        sample_dir = _Path(__file__).resolve().parents[2] / 'example' / 'wksp'
        for name in ['corpus.pattern.jsonl', 'patterns.txt']:
            src = sample_dir / name
            if src.exists():
                copy2(src, wksp / name)
        # create config if missing
        if not config_path.exists():
            Config(config_path).save()
        logger.info(f'Sample workspace generated at {wksp}')
        return
    if config_path.exists():
        app = ReviewApp(config_path)
        app.run()
        # on exit, export database
        try:
            app.annotations.export()
            app.notify('Exported annotations', severity='information')
        except Exception as exc:
            logger.error(f'Export failed: {exc}')
    else:
        logger.error(f'Configuration file does not exist! {config_path}')
        logger.warning(f'Creating default configuration at {config_path}')
        config_path.parent.mkdir(exist_ok=True)
        Config(config_path).save()


if __name__ == '__main__':
    main()
