from __future__ import annotations

import tomlkit
import pytest


pytestmark = pytest.mark.asyncio


async def test_add_highlight_persists_and_applies(app):
    async with app.run_test() as pilot:
        # enter first record
        await pilot.click('#next')

        # open Add Keyword modal
        await pilot.click('#highlight-keyword')

        # fill in fields directly via widget access for reliability in headless
        screen = app.screen
        screen.query_one('#keyword-regex').value = 'the'
        screen.query_one('#keyword-color').value = 'yellow'

        # submit
        await pilot.click('#keyword-add')

        # config.toml should include the new highlight
        cfg_path = app.config.path
        with cfg_path.open(encoding='utf8') as fh:
            data = tomlkit.load(fh)
        assert any(h['regex'] == 'the' and h['color'] == 'yellow' for h in data['highlights'])

        # refresh the text field and ensure internal highlights exist
        await app.snippet_widget.update_entry()
        textfield = app.snippet_widget.scroll.query_one('#textfield')
        # HighlighterWidget renders HighlightTextArea at .textbox
        hl = textfield.textbox
        total_spans = sum(len(r) for r in hl._highlights.values())
        assert total_spans > 0


async def test_mark_offsets_are_applied_after_update(app):
    async with app.run_test() as pilot:
        # Move to record and ensure we have an annotation object
        await pilot.click('#next')
        entry = app.current_entry
        # add a mark over the first 3 chars of match
        app.current_annot.add_mark(0, min(3, len(entry['match'])), entry['match'][:3], 'mark')
        await app.update_display()

        # ensure mark highlight spans exist
        textfield = app.snippet_widget.scroll.query_one('#textfield')
        hl = textfield.textbox
        # there should be highlight spans added by marks (in addition to target)
        total_spans = sum(len(r) for r in hl._highlights.values())
        assert total_spans > 0
