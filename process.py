"""
Main CLI for chat screenshot pixelation.

Loads images from an input directory, calls the OpenRouter vision API to extract
bounding boxes for the requested elements (chat_name, profile_pic, display_name),
applies pixelation to each region, and saves results to an output directory.

Usage:
    python3 process.py <input_dir> <output_dir> [options]

    --elements     Comma-separated elements to pixelate (default: all three)
                   Choices: chat_name, profile_pic, display_name
                   Examples:
                     --elements profile_pic
                     --elements chat_name,display_name
    --pixel-mode   A=soft blur/mist (default) | B=hard block mosaic

Input spec:
    input_dir may contain .png, .jpg, .jpeg files.

Output spec:
    output_dir gets {stem}_pixelated.png for each processed image.
    Images that fail API/parse steps are copied as-is with a warning.
    A summary is printed to stdout on completion.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from pixelate import load_image, save_image, mist_pixelate_region, strong_pixelate_region
from prompts import build_bbox_prompt
from vision import call_vision

_VALID_ELEMENTS = {"chat_name", "profile_pic", "display_name"}
_KEY_MAP = {
    "chat_name": "chat_names",
    "profile_pic": "profile_pics",
    "display_name": "display_names",
}
_IMAGE_EXTS = {".png", ".jpg", ".jpeg"}


def _parse_elements(raw: str) -> set:
    parts = {s.strip() for s in raw.split(",") if s.strip()}
    unknown = parts - _VALID_ELEMENTS
    assert not unknown, f"Unknown elements: {unknown}. Valid: {_VALID_ELEMENTS}"
    return parts


def _convert_norm_to_bbox(region: dict, orig_width: int, orig_height: int) -> tuple:
    """
    Convert normalized (0-1000) y_min/x_min/y_max/x_max to pixel (x, y, width, height).

    Normalised coords are relative to the original image dimensions regardless of
    any compression applied before sending to the API.
    """
    y_min = region.get("y_min", 0)
    x_min = region.get("x_min", 0)
    y_max = region.get("y_max", 0)
    x_max = region.get("x_max", 0)

    x = int(x_min / 1000 * orig_width)
    y = int(y_min / 1000 * orig_height)
    width = int((x_max - x_min) / 1000 * orig_width)
    height = int((y_max - y_min) / 1000 * orig_height)

    x = max(0, min(orig_width - 1, x))
    y = max(0, min(orig_height - 1, y))
    width = min(width, orig_width - x)
    height = min(height, orig_height - y)

    return (x, y, width, height)


def _parse_json_response(text: str) -> dict:
    json_start = text.find("{")
    json_end = text.rfind("}") + 1
    assert json_start >= 0 and json_end > json_start, "No JSON object found in response"
    return json.loads(text[json_start:json_end])


def _process_image(
    image_path: Path,
    output_dir: Path,
    elements: set,
    pixel_mode: str,
) -> dict:
    """
    Process a single image. Returns a result dict with keys: path, success, skipped, reason.
    On API or parse failure, copies the original to output unchanged.
    """
    out_path = output_dir / f"{image_path.stem}_pixelated.png"

    image = load_image(str(image_path))
    orig_width, orig_height = image.size
    print(f"[process] {image_path.name} ({orig_width}x{orig_height})")

    prompt = build_bbox_prompt(elements)

    try:
        response = call_vision(str(image_path), prompt)
    except Exception as exc:
        print(f"[process] WARNING: vision API failed for {image_path.name}: {exc}")
        print(f"[process] Copying original to output unchanged.")
        shutil.copy2(image_path, out_path)
        return {"path": str(out_path), "success": False, "skipped": True, "reason": f"API error: {exc}"}

    try:
        parsed = _parse_json_response(response)
    except (AssertionError, json.JSONDecodeError, ValueError) as exc:
        print(f"[process] WARNING: JSON parse failed for {image_path.name}: {exc}")
        print(f"[process] Raw response (truncated): {response[:300]}")
        print(f"[process] Copying original to output unchanged.")
        shutil.copy2(image_path, out_path)
        return {"path": str(out_path), "success": False, "skipped": True, "reason": f"Parse error: {exc}"}

    bboxes = []
    for element in elements:
        key = _KEY_MAP[element]
        regions = parsed.get(key, [])
        if not isinstance(regions, list):
            continue
        for region in regions:
            if not isinstance(region, dict):
                continue
            bbox = _convert_norm_to_bbox(region, orig_width, orig_height)
            if bbox[2] > 0 and bbox[3] > 0:
                bboxes.append((element, bbox))

    print(f"[process] Found {len(bboxes)} region(s) to pixelate.")

    result_img = image.copy()
    for element, bbox in bboxes:
        try:
            if pixel_mode == "A":
                result_img = mist_pixelate_region(result_img, bbox)
            else:
                result_img = strong_pixelate_region(result_img, bbox)
        except Exception as exc:
            print(f"[process] WARNING: pixelation failed for bbox {bbox}: {exc}")

    save_image(result_img, str(out_path))
    print(f"[process] Saved -> {out_path.name}")
    return {"path": str(out_path), "success": True, "skipped": False, "reason": ""}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pixelate chat screenshots to hide identity elements.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 process.py ./in ./out\n"
            "  python3 process.py ./in ./out --elements profile_pic\n"
            "  python3 process.py ./in ./out --elements chat_name,display_name --pixel-mode B\n"
        ),
    )
    parser.add_argument("input_dir", help="Directory containing input images (.png/.jpg/.jpeg)")
    parser.add_argument("output_dir", help="Directory for output images")
    parser.add_argument(
        "--elements",
        default="chat_name,profile_pic,display_name",
        help=(
            "Comma-separated elements to pixelate "
            "(default: chat_name,profile_pic,display_name). "
            "Options: chat_name, profile_pic, display_name"
        ),
    )
    parser.add_argument(
        "--pixel-mode",
        choices=["A", "B"],
        default="A",
        dest="pixel_mode",
        help="Pixelation style: A=soft blur/mist (default), B=hard block mosaic",
    )
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    assert in_dir.exists(), f"Input directory not found: {in_dir}"
    out_dir.mkdir(parents=True, exist_ok=True)

    elements = _parse_elements(args.elements)
    print(f"[process] Elements: {sorted(elements)}, mode: {args.pixel_mode}")

    images = sorted(p for p in in_dir.iterdir() if p.suffix.lower() in _IMAGE_EXTS)
    if not images:
        print(f"No images found in {in_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[process] Processing {len(images)} image(s) from {in_dir} -> {out_dir}")

    results = []
    for img_path in images:
        result = _process_image(img_path, out_dir, elements, args.pixel_mode)
        results.append(result)

    processed = sum(1 for r in results if r["success"])
    skipped = sum(1 for r in results if r["skipped"])

    print(f"\n=== Summary ===")
    print(f"Total:     {len(results)}")
    print(f"Processed: {processed}")
    print(f"Skipped:   {skipped}")
    print("Output files:")
    for r in results:
        status = "OK" if r["success"] else f"SKIPPED ({r['reason']})"
        print(f"  {r['path']}  [{status}]")


if __name__ == "__main__":
    main()
