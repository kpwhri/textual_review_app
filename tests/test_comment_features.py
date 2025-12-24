import pytest
from textual_review_app.app import ReviewApp
from textual_review_app.widgets.snippet_widget import SnippetWidget
from textual.widgets import TextArea

@pytest.mark.asyncio
async def test_comment_persistence_and_clearing(app: ReviewApp):
    async with app.run_test() as pilot:
        # Dismiss initial InfoModal
        await pilot.press('enter')
        await pilot.pause()

        # 1. Initial state check
        snippet_widget = app.query_one(SnippetWidget)
        comment_area = snippet_widget.query_one('#comment', TextArea)
        assert comment_area.text == ''

        # 2. Add a comment and save/next
        comment_text = 'This is a test comment'
        comment_area.text = comment_text
        await pilot.click('#next')
        await pilot.pause()

        # 3. Ensure comment is cleared for the next record
        assert comment_area.text == ''
        assert app.curr_idx == 1

        # 4. Go back to previous record and check if comment persists
        await pilot.click('#previous')
        await pilot.pause()
        assert app.curr_idx == 0
        assert comment_area.text == comment_text

@pytest.mark.asyncio
async def test_comment_deletion(app: ReviewApp):
    async with app.run_test() as pilot:
        # Dismiss initial InfoModal
        await pilot.press('enter')
        await pilot.pause()

        snippet_widget = app.query_one(SnippetWidget)
        comment_area = snippet_widget.query_one('#comment', TextArea)

        # Add comment
        comment_area.text = 'Temporary comment'
        await pilot.click('#save')
        await pilot.pause()

        # Delete comment
        comment_area.text = ''
        await pilot.click('#save')
        await pilot.pause()

        # Verify it remains deleted after navigation
        await pilot.click('#next')
        await pilot.pause()
        await pilot.click('#previous')
        await pilot.pause()
        assert comment_area.text == ''

from textual_review_app.widgets.canned_response_modal import CannedResponseModal

@pytest.mark.asyncio
async def test_use_canned_response(app: ReviewApp):
    # Ensure config has some canned responses
    app.config.canned_responses = ['Great', 'Fix it']

    async with app.run_test() as pilot:
        # dismiss initial InfoModal
        await pilot.press('enter')
        await pilot.pause()

        # open canned responses modal
        await pilot.press('ctrl+l')
        await pilot.pause()

        # check if modal is open
        assert isinstance(app.screen, CannedResponseModal)

        # select the first response (Great)
        await pilot.press('enter')
        await pilot.pause()

        # verify comment is updated
        snippet_widget = app.query_one(SnippetWidget)
        comment_area = snippet_widget.query_one('#comment', TextArea)
        assert comment_area.text == 'Great'

@pytest.mark.asyncio
async def test_add_canned_response(app: ReviewApp):
    app.config.canned_responses = ['Existing']

    async with app.run_test() as pilot:
        # dismiss initial InfoModal
        await pilot.press('enter')
        await pilot.pause()

        # open canned responses modal
        await pilot.press('ctrl+l')
        await pilot.pause()

        # focus new response input and type something
        # in CannedResponseModal: ListView(id='response-list') -> Input(id='new-response')
        # we might need more tabs or use specific selector focus
        from textual.widgets import Input
        app.screen.query_one('#new-response', Input).focus()
        await pilot.press('n', 'e', 'w', '_', 'r', 'e', 's', 'p', 'o', 'n', 's', 'e')
        await pilot.press('enter')
        await pilot.pause()

        # verify comment is updated
        snippet_widget = app.query_one(SnippetWidget)
        comment_area = snippet_widget.query_one('#comment', TextArea)
        assert comment_area.text == 'new_response'
        # verify in config
        assert 'new_response' in app.config.canned_responses
