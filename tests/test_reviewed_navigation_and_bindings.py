from __future__ import annotations

import sqlite3

import pytest

pytestmark = pytest.mark.asyncio


async def test_goto_reviewed_lists_and_navigates(app):
    async with app.run_test() as pilot:
        # move to first record and save to mark as reviewed
        await pilot.click('#next')
        await pilot.click('#save')

        # open the reviewed nav and click the first reviewed button (#1)
        await pilot.click('#goto-reviewed-btn')
        await pilot.pause()

        # Button id is goto-0 for first record (0-based index)
        await pilot.click('#goto-0')

        # Ensure progress label shows Record #1 after navigation
        assert 'Record #1' in str(app.query_one('#progress-label').renderable)


async def test_escape_closes_info_modal(app):
    async with app.run_test() as pilot:
        # open instructions/info modal directly
        await pilot.click('#instructions-btn')
        # press escape to close
        await pilot.press('escape')
        # nothing to assert explicitly; if not closed, subsequent actions will fail
        # try opening again to ensure app still responsive
        await pilot.click('#instructions-btn')
        await pilot.press('escape')


async def test_keybindings_save_and_navigation(app):
    async with app.run_test() as pilot:
        # go to first record
        await pilot.click('#next')
        # toggle a response to create a selection
        btn = app.response_buttons[0]
        await pilot.click(f'#{btn.id}')

        # use Ctrl+S to save
        await pilot.press('ctrl+s')

        # verify row exists in db
        db_path = app.config.corpus_path.parent / 'annotations.db'
        assert db_path.exists()
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.execute('SELECT COUNT(*) FROM annotations')
            count = cur.fetchone()[0]
            assert count >= 1
        finally:
            conn.close()

        # use Ctrl+Right to go to next (Save & Next)
        await pilot.press('ctrl+right')
        assert 'Record #2' in str(app.query_one('#progress-label').renderable)

        # use Ctrl+Left to go back previous
        await pilot.press('ctrl+left')
        assert 'Record #1' in str(app.query_one('#progress-label').renderable)
