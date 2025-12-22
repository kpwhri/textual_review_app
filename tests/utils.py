import asyncio


async def wait_for_label_contains(pilot, exp_text, get_label_func, timeout=1.0):
    end = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < end:
        try:
            label = get_label_func()
            if exp_text in label:
                return label
        except Exception:
            print(label)
            pass
        await pilot.pause(0.02)  # small yield between polls
    raise AssertionError(f'timeout waiting for progress label to contain {exp_text!r}')
