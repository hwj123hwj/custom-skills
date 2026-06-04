from pathlib import Path
from conf import BASE_DIR


async def set_init_script(context):
    """Inject stealth.min.js to reduce automation detection."""
    stealth_js_path = Path(BASE_DIR / "utils" / "stealth.min.js")
    await context.add_init_script(path=stealth_js_path)
    return context
