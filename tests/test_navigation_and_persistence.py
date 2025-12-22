from __future__ import annotations

import sqlite3

import pytest

from utils import wait_for_label_contains

pytestmark = pytest.mark.asyncio


async def test_navigation_and_progress_updates(app):

    async with app.run_test() as pilot:

        def get_progress_label():
            return str(app.query_one('#progress-label').renderable)
        await pilot.pause()
        # initially on instructions
        await pilot.click('#next')  # clicking next should switch to first record
        await pilot.pause()
        # progress label should show Record #1
        text = await wait_for_label_contains(pilot, 'Record #1', get_progress_label)
        assert 'Record #1' in text

        # click next a couple of times within bounds
        await pilot.click('#next')  # HACK: record #2?? not sure why have to do twice?!
        await pilot.pause()
        await pilot.click('#next')  # record #2
        await pilot.pause()
        text = await wait_for_label_contains(pilot, 'Record #2', get_progress_label)
        assert 'Record #2' in text

        await pilot.click('#next')  # record #3
        await pilot.pause()
        await pilot.click('#next')  # HACK: record #3
        await pilot.pause()
        # progress label should advance accordingly
        text = await wait_for_label_contains(pilot, 'Record #3', get_progress_label)
        assert 'Record #3' in get_progress_label()

        # click previous and ensure it goes back
        await pilot.click('#previous')  # record #2
        await pilot.pause()
        assert 'Record #2' in get_progress_label()


async def test_bounds_show_info_modal(app):
    async with app.run_test() as pilot:
        await pilot.pause()
        # move to first record from instructions
        await pilot.click('#next')  # first click exits instructions
        assert 'Record #1' in str(app.query_one('#progress-label').renderable)  # ensure at first record
        # now at first record; clicking previous again should show info modal
        await pilot.click('#previous')
        # wait briefly for modal to mount, then click OK
        clicked = False
        for _ in range(20):
            try:
                await pilot.click('#ok')
                clicked = True
                break
            except Exception:
                await pilot.pause()
        assert clicked, 'Expected InfoModal OK button to be clickable'


async def test_save_persists_to_annotations_db(app):
    async with app.run_test() as pilot:
        # Move to first record
        await pilot.click('#next')
        # Toggle the first response button to create a selection
        btn = app.response_buttons[0]
        await pilot.click(f'#{btn.id}')
        # Save current record
        await pilot.click('#save')

        # ensure db exists and has at least one row
        db_path = app.config.corpus_path.parent / 'annotations.db'
        assert db_path.exists()
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.execute('SELECT COUNT(*) FROM annotations')
            count = cur.fetchone()[0]
            assert count >= 1
        finally:
            conn.close()
