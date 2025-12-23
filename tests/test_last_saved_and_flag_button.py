from __future__ import annotations

import json
import sqlite3

import pytest

from textual.widgets import Button

pytestmark = pytest.mark.asyncio


async def test_last_saved_label_updates_on_save(app):
    async with app.run_test() as pilot:
        # go to first record
        await pilot.click('#next')
        # trigger save via shortcut (works even when focused elsewhere)
        await pilot.press('ctrl+s')
        # label should contain timestamp prefix
        text = str(app.query_one('#last-saved-label').renderable)
        assert 'Last saved:' in text


async def test_flag_toggle_button_toggles_and_colors(app):
    async with app.run_test() as pilot:
        await pilot.click('#next')
        # initial state should be unflagged (green)
        btn = app.query_one('#flag-toggle', Button)
        assert str(btn.label) == 'Flag'
        assert btn.variant == 'success'

        # click to flag
        await pilot.click('#flag-toggle')
        # state updates
        assert getattr(app.current_annot, 'flagged', False) is True
        assert str(btn.label) == 'Flagged'
        assert btn.variant == 'error'

        # save and verify in DB
        await pilot.press('ctrl+s')
        db_path = app.config.corpus_path.parent / 'annotations.db'
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute('SELECT annotation FROM annotations WHERE rowid = 0').fetchone()
            data = json.loads(row[0])
            assert data.get('flagged') is True
        finally:
            conn.close()


async def test_ctrl_r_in_snippet_view_flags_record(app):
    async with app.run_test() as pilot:
        await pilot.click('#next')
        # focus into the snippet text area area
        await pilot.click('#textfield')
        # toggle flag via Ctrl+R inside snippet view
        await pilot.press('ctrl+r')
        # save via Ctrl+S
        await pilot.press('ctrl+s')
        # verify in DB
        db_path = app.config.corpus_path.parent / 'annotations.db'
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute('SELECT annotation FROM annotations WHERE rowid = 0').fetchone()
            data = json.loads(row[0])
            assert data.get('flagged') is True
        finally:
            conn.close()
