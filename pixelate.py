"""
Core pixelation utilities for chat screenshot anonymization.

Provides two pixelation modes applied to bounding-box regions of a PIL Image:
  - mist_pixelate_region: soft Gaussian blur with feathered edges (mode A)
  - strong_pixelate_region: hard block mosaic (mode B)

All bboxes use (x, y, width, height) in pixels where (x, y) is the top-left corner.

Usage:
    from pixelate import load_image, save_image, mist_pixelate_region, strong_pixelate_region
    img = load_image("input.png")
    img = mist_pixelate_region(img, (50, 100, 200, 60))
    save_image(img, "output.png")
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def save_image(image: Image.Image, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG")


def mist_pixelate_region(image: Image.Image, bbox: tuple) -> Image.Image:
    """
    Soft Gaussian blur with feathered edges (mode A).

    bbox: (x, y, width, height) in pixels.
    """
    x, y, w, h = bbox
    if w <= 0 or h <= 0:
        return image

    padding = 5
    x_pad = max(0, x - padding)
    y_pad = max(0, y - padding)
    w_pad = min(image.width - x_pad, w + 2 * padding)
    h_pad = min(image.height - y_pad, h + 2 * padding)

    padded_region = image.crop((x_pad, y_pad, x_pad + w_pad, y_pad + h_pad))

    blur_radius = max(2, int((min(w, h) / 7) * 0.75))
    blurred = padded_region.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    mask = Image.new("L", (w_pad, h_pad), 0)
    draw = ImageDraw.Draw(mask)
    target_bbox = (x - x_pad, y - y_pad, x - x_pad + w, y - y_pad + h)
    draw.rectangle(target_bbox, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=2))

    result = image.copy()
    result.paste(blurred, (x_pad, y_pad), mask)
    return result


def strong_pixelate_region(image: Image.Image, bbox: tuple) -> Image.Image:
    """
    Hard block mosaic pixelation (mode B).

    bbox: (x, y, width, height) in pixels.
    """
    x, y, w, h = bbox
    if w <= 0 or h <= 0:
        return image

    padding = 4
    x_pad = max(0, x - padding)
    y_pad = max(0, y - padding)
    w_pad = min(image.width - x_pad, w + 2 * padding)
    h_pad = min(image.height - y_pad, h + 2 * padding)

    region = image.crop((x_pad, y_pad, x_pad + w_pad, y_pad + h_pad))

    min_dim = min(w_pad, h_pad)
    if min_dim < 10:
        small_size = (1, 1)
    else:
        scale = max(1, min_dim // 5)
        small_size = (max(1, w_pad // scale), max(1, h_pad // scale))

    small = region.resize(small_size, Image.NEAREST)
    pixelated = small.resize((w_pad, h_pad), Image.NEAREST)

    result = image.copy()
    result.paste(pixelated, (x_pad, y_pad))
    return result
