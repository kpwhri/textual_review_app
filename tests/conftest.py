from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest
import tomlkit

import sys

# Ensure 'src' is on sys.path to import textual_review_app
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from textual_review_app.app import ReviewApp


@pytest.fixture()
def make_workspace(tmp_path: Path) -> Iterator[Path]:
    """
    Create a temporary workspace by copying example corpus and generating a config.toml.

    Returns the path to the generated config.toml.
    """
    project_root = Path(__file__).resolve().parents[1]
    example_wksp = project_root / 'example' / 'wksp'

    wksp_path = tmp_path / 'wksp'
    wksp_path.mkdir(parents=True, exist_ok=True)

    # Copy corpus file used by examples
    for name in ['corpus.pattern.jsonl', 'patterns.txt']:
        src = example_wksp / name
        if src.exists():
            (wksp_path / name).write_bytes(src.read_bytes())

    # Build a minimal config.toml pointing to the copied corpus, with offset 0
    config_path = wksp_path / 'config.toml'
    doc = tomlkit.document()
    doc['title'] = 'Test Review App'
    doc['offset'] = 0
    doc['corpus'] = 'corpus.pattern.jsonl'
    doc['highlights'] = []
    doc['instructions'] = ['Review and select the relevant options.']
    doc['options'] = ['Relevant', 'Uncertain', 'Not Relevant']
    with config_path.open('w', encoding='utf8') as fh:
        tomlkit.dump(doc, fh)

    yield config_path


@pytest.fixture()
def app(make_workspace: Path) -> ReviewApp:
    """Create a ReviewApp for tests, using the temporary workspace config."""
    return ReviewApp(make_workspace)
