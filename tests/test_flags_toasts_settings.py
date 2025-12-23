from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio


async def test_flagging_persists_and_in_export(app, tmp_path):
    async with app.run_test() as pilot:
        # go to first record
        await pilot.click('#next')
        # toggle flag with Ctrl+R
        await pilot.press('ctrl+r')
        # save so it is persisted
        await pilot.press('ctrl+s')

        # verify in database row json
        db_path = app.config.corpus_path.parent / 'annotations.db'
        assert db_path.exists()
        conn = sqlite3.connect(db_path)
        try:
            row = conn.execute('SELECT annotation FROM annotations WHERE rowid = 0').fetchone()
            assert row is not None
            data = json.loads(row[0])
            assert data.get('flagged') is True
        finally:
            conn.close()

        # verify in export file
        app.annotations.export()
        exports = sorted((app.config.corpus_path.parent).glob('export_*.db.jsonl'))
        assert exports, 'No export files created'
        export_path = exports[-1]
        lines = export_path.read_text(encoding='utf8').splitlines()
        parsed = [json.loads(line) for line in lines]
        # find row == 0
        rec0 = [r for r in parsed if r.get('row') == 0]
        assert rec0 and rec0[0].get('flagged') is True
        # user should be present
        assert 'user' in rec0[0]


async def test_toasts_on_save(app):
    called = []

    def fake_notify(message, *args, **kwargs):
        called.append((message, args, kwargs))

    async with app.run_test() as pilot:
        # monkeypatch notify on app instance
        app.notify = fake_notify  # type: ignore
        # navigate and trigger a save
        await pilot.click('#next')
        await pilot.press('ctrl+s')
        # ensure our fake was called with a Saved message
        assert any('Saved' in msg for (msg, _, __) in called)


async def test_settings_persist_in_config_file(app):
    async with app.run_test() as pilot:
        # open settings
        await pilot.click('#settings-btn')
        # programmatically set values in modal inputs for reliability
        from textual.widgets import Input
        font_input = app.screen.query_one('#font-scale', Input)
        user_input = app.screen.query_one('#user', Input)
        font_input.value = '2.0'
        user_input.value = 'tester_user'
        # save
        await pilot.click('#ok')

        # verify values applied to current app
        assert abs(app.config.font_scale - 2.0) < 1e-6
        assert app.config.user == 'tester_user'

        # verify persisted in config file by reloading
        from textual_review_app.config import Config
        cfg = Config(app.config.path)
        assert abs(cfg.font_scale - 2.0) < 1e-6
        assert cfg.user == 'tester_user'
