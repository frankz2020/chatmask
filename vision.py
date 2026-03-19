"""
OpenRouter vision API client for chat screenshot bbox extraction.

Compresses the image to ≤1024px before sending to the API. The model returns
normalized coordinates (0-1000) relative to the original image dimensions, so
callers must scale back using the original width/height — not the compressed size.

Usage:
    from vision import call_vision
    response_text = call_vision("screenshot.png", prompt)
"""

import base64
import os
import time
from io import BytesIO

import requests
from PIL import Image

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3.1-pro-preview"
_API_MAX_DIM = 1024


def _get_api_key() -> str:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError(
            "OPENROUTER_API_KEY is required for standalone (non-OpenClaw) use. "
            "Get a free key at https://openrouter.ai/keys and set it with: "
            "export OPENROUTER_API_KEY='sk-or-...'"
            "\n\nIf you are running chatmask via the OpenClaw skill, use "
            "--bbox-json instead — no API key is needed."
        )
    return key


def _compress_image_for_api(image_path: str) -> tuple:
    """
    Load image and compress to ≤1024px on the longest side for API transmission.

    Returns (jpeg_bytes, mime_type). The original file is not modified.
    Normalized coordinates (0-1000) returned by the API still map to the
    original image dimensions — callers must scale using orig_width/orig_height.
    """
    img = Image.open(image_path).convert("RGB")
    max_dim = max(img.width, img.height)
    if max_dim > _API_MAX_DIM:
        scale = _API_MAX_DIM / max_dim
        new_w = max(1, int(img.width * scale))
        new_h = max(1, int(img.height * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue(), "image/jpeg"


def call_vision(image_path: str, prompt: str, max_retries: int = 3) -> str:
    """
    Call the OpenRouter vision model with a chat screenshot and return the raw text response.

    Args:
        image_path: Path to the image file.
        prompt: The user prompt (should request a JSON bbox response).
        max_retries: Number of retry attempts on failure.

    Returns:
        Raw response text from the model.

    Raises:
        Exception: If all retries fail or the response is malformed.
    """
    api_key = _get_api_key()

    compressed_bytes, mime_type = _compress_image_for_api(image_path)
    image_b64 = base64.b64encode(compressed_bytes).decode("utf-8")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
                    },
                ],
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    proxies = _get_proxies()
    last_exc: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[vision] Attempt {attempt}/{max_retries} for model {MODEL}")
            response = requests.post(
                OPENROUTER_API_URL,
                json=payload,
                headers=headers,
                timeout=120,
                proxies=proxies,
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"[vision] Response received (len={len(content)})")
            return content
        except Exception as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = attempt * 2
                print(
                    f"[vision] Attempt {attempt} failed: {exc}. Retrying in {wait}s..."
                )
                time.sleep(wait)
            else:
                print(f"[vision] All {max_retries} attempts failed.")

    raise last_exc


def _get_proxies() -> dict | None:
    proxies = {}
    if http := (os.getenv("HTTP_PROXY") or os.getenv("http_proxy")):
        proxies["http"] = http
    if https := (os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")):
        proxies["https"] = https
    return proxies or None
