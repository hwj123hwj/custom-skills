import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
LOCAL_CHROME_PATH = ""  # optional override, e.g. /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
LOCAL_CHROME_HEADLESS = True
DEBUG_MODE = True


def get_launch_kwargs(headless: bool = LOCAL_CHROME_HEADLESS) -> dict:
    """
    Return kwargs for playwright.chromium.launch() that work across environments:
    - Local Mac/Windows with Google Chrome installed: uses channel="chrome"
    - Server (Linux, no Chrome): uses patchright built-in Chromium with --no-sandbox
    - LOCAL_CHROME_PATH set: uses that executable directly

    NOTE: On Linux servers, even when --headed is passed, we force headless=True.
    patchright bypasses webdriver detection, so headless works fine with Douyin.
    xvfb virtual display causes mouse events to not register correctly.
    CDP mouse events (page.mouse) work independently of the display server.
    """
    # Force headless on Linux server (no real display needed, CDP handles mouse events)
    if sys.platform == "linux" and not headless:
        headless = True

    args = ["--force-device-scale-factor=1"]
    if sys.platform == "linux":
        args += ["--no-sandbox", "--disable-dev-shm-usage"]

    kwargs: dict = {"headless": headless, "args": args}

    if LOCAL_CHROME_PATH:
        kwargs["executable_path"] = LOCAL_CHROME_PATH
    elif sys.platform in ("darwin", "win32"):
        # Mac/Windows: prefer real Chrome for better anti-detection
        kwargs["channel"] = "chrome"
    # Linux server: no channel, use patchright built-in Chromium

    return kwargs
