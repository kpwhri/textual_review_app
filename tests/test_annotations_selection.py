from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest


pytestmark = pytest.mark.asyncio


async def _get_db_selected(db_path: Path, rowid: int):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute('SELECT annotation FROM annotations WHERE rowid = ?', (rowid,))
        row = cur.fetchone()
        if not row:
            return None
        data = json.loads(row[0])
        return data.get('selected', [])
    finally:
        conn.close()


def _latest_export_jsonl(wksp_dir: Path) -> Path:
    exports = sorted(wksp_dir.glob('export_*.db.jsonl'))
    if not exports:
        raise AssertionError('No export files found')
    return exports[-1]


async def test_no_selection_saved_and_exported(app):
    async with app.run_test() as pilot:
        # go to first record but select nothing
        await pilot.click('#next')
        # save
        await pilot.click('#save')

        db_path = app.config.corpus_path.parent / 'annotations.db'
        selected = await _get_db_selected(db_path, 0)
        assert selected == []

        # export and verify
        app.annotations.export()
        export = _latest_export_jsonl(app.config.corpus_path.parent)
        data = [json.loads(l) for l in export.read_text(encoding='utf8').splitlines()]
        # find row 0
        row0 = next(d for d in data if d['row'] == 0)
        assert row0['selected'] == []


async def test_single_selection_saved_and_exported(app):
    async with app.run_test() as pilot:
        await pilot.click('#next')
        # click first response
        btn = app.response_buttons[0]
        await pilot.click(f'#{btn.id}')
        await pilot.click('#save')

        db_path = app.config.corpus_path.parent / 'annotations.db'
        selected = await _get_db_selected(db_path, 0)
        assert selected == [str(btn.label)]

        app.annotations.export()
        export = _latest_export_jsonl(app.config.corpus_path.parent)
        data = [json.loads(l) for l in export.read_text(encoding='utf8').splitlines()]
        row0 = next(d for d in data if d['row'] == 0)
        assert row0['selected'] == [str(btn.label)]


async def test_all_three_selection_saved_and_exported(app):
    async with app.run_test() as pilot:
        await pilot.click('#next')
        # click all response buttons
        labels = []
        for btn in app.response_buttons[:3]:
            labels.append(str(btn.label))
            await pilot.click(f'#{btn.id}')
        await pilot.click('#save')

        db_path = app.config.corpus_path.parent / 'annotations.db'
        selected = await _get_db_selected(db_path, 0)
        assert selected == labels

        app.annotations.export()
        export = _latest_export_jsonl(app.config.corpus_path.parent)
        data = [json.loads(l) for l in export.read_text(encoding='utf8').splitlines()]
        row0 = next(d for d in data if d['row'] == 0)
        assert row0['selected'] == labels
