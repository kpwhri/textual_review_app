import asyncio
from pathlib import Path

import pytest


pytestmark = pytest.mark.asyncio


async def test_ui_elements_present(app):
    async with app.run_test() as pilot:
        # header buttons and labels
        assert app.query_one('#metadata-btn')
        assert app.query_one('#instructions-btn')
        assert app.query_one('#progress-label')

        # snippet widget should exist
        assert app.snippet_widget is not None

        # footer exists
        from textual.widgets import Footer
        assert app.query_one(Footer)

        # bottom bar buttons exist
        assert app.query_one('#exit')
        assert app.query_one('#previous')
        assert app.query_one('#highlight-keyword')
        assert app.query_one('#save')
        assert app.query_one('#next')


async def test_instructions_modal_and_metadata_modal(app):
    async with app.run_test() as pilot:
        # instructions button should open an InfoModal
        await pilot.click('#instructions-btn')
        screen = app.screen
        # modal screen is pushed, find the OK button and close
        ok = screen.query_one('#ok')
        await pilot.click('#ok')

        # move to first record, then metadata shows MetadataModal (not instructions)
        await pilot.click('#next')
        await pilot.click('#metadata-btn')
        # metadata modal also has an OK, close it
        await pilot.click('#ok')
