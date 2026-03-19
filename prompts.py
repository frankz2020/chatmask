"""
Vision prompt builder for chat screenshot bbox extraction.

Builds an app-agnostic, element-aware prompt that asks the vision model to
return bounding boxes only for the requested elements (chat_name, profile_pic,
display_name). The prompt is designed to work across any messaging app
(WeChat, WhatsApp, Telegram, iMessage, Slack, Discord, etc.) and supports
both English and Chinese chat UIs.

Usage:
    from prompts import build_bbox_prompt
    prompt = build_bbox_prompt({"chat_name", "profile_pic", "display_name"})
"""

_VALID_ELEMENTS = {"chat_name", "profile_pic", "display_name"}

_ELEMENT_DESCRIPTIONS = {
    "chat_name": (
        "**chat_names** — The text title shown in the top navigation/header bar of the chat window. "
        "This is the conversation name, contact name, group name, or channel title "
        "(e.g. the bold text at the very top center of the screen). "
        "Include any back-button label that shows the contact/group name."
    ),
    "profile_pic": (
        "**profile_pics** — Circular or rounded avatar/profile images that appear "
        "next to message bubbles, in the header, or on the participants list. "
        "Each distinct avatar occurrence should be its own region."
    ),
    "display_name": (
        "**display_names** — Text username or nickname labels that appear directly "
        "next to or just above message bubbles (sender names). "
        "These are the short text strings identifying who sent each message, "
        "distinct from the chat title in the header."
    ),
}

_KEY_MAP = {
    "chat_name": "chat_names",
    "profile_pic": "profile_pics",
    "display_name": "display_names",
}


def build_bbox_prompt(elements: set) -> str:
    """
    Build a vision prompt requesting bounding boxes for the given elements only.

    Args:
        elements: Subset of {"chat_name", "profile_pic", "display_name"}.

    Returns:
        Prompt string to send to the vision model.
    """
    assert elements, "elements must be non-empty"
    assert elements <= _VALID_ELEMENTS, (
        f"Invalid elements: {elements - _VALID_ELEMENTS}"
    )

    requested_keys = [_KEY_MAP[e] for e in sorted(elements)]
    element_blocks = "\n".join(
        f"{i + 1}. {_ELEMENT_DESCRIPTIONS[e]}" for i, e in enumerate(sorted(elements))
    )

    json_schema_fields = "\n".join(
        f'    "{k}": [{{"y_min": int, "x_min": int, "y_max": int, "x_max": int}}, ...]'
        for k in requested_keys
    )

    return f"""You are a privacy specialist analyzing a chat/messaging app screenshot.
The app could be WeChat, WhatsApp, Telegram, iMessage, Slack, Discord, LINE, KakaoTalk,
or any other messaging application. The UI may be in English, Chinese, or any other language.
Identify the requested elements **by their visual layout and position**, not by app-specific labels.

**YOUR TASK:**
Locate ALL occurrences of the following elements and return their bounding boxes:

{element_blocks}

**RULES:**
- Return ONLY the elements listed above — do not include any other UI components.
- Each element occurrence (e.g. every avatar next to every message bubble) must be its own region.
- Cover the full visible area of the element with a small amount of padding.
- If an element type is not visible in the screenshot, return an empty list for that key.
- Use **normalized coordinates (0-1000)** where (0, 0) is top-left and (1000, 1000) is bottom-right.
- Coordinate order: y_min, x_min, y_max, x_max (top, left, bottom, right).
- All values must be integers between 0 and 1000.

Respond ONLY with a JSON object using this exact schema (no extra text outside the JSON):
{{
{json_schema_fields}
}}
"""
