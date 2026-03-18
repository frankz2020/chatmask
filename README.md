<div align="center">

# 🎭 chatmask

**Automatically detect and redact identities in chat screenshots — locally, in seconds.**

[![CI](https://github.com/frankz2020/chatmask/actions/workflows/ci.yml/badge.svg)](https://github.com/frankz2020/chatmask/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![OpenRouter](https://img.shields.io/badge/powered%20by-OpenRouter-purple)](https://openrouter.ai)
[![Pillow](https://img.shields.io/badge/image%20processing-Pillow-orange)](https://python-pillow.org)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa)](CODE_OF_CONDUCT.md)

Works with **any** messaging app — WeChat, WhatsApp, Telegram, iMessage, Slack, Discord, LINE, KakaoTalk, and more.
Supports English and Chinese UIs.

</div>

---

> **How it works in one sentence:** A Gemini vision model (via OpenRouter) finds the sensitive regions; [Pillow](https://python-pillow.org) blurs them locally. Only compressed image bytes leave your machine — no text, names, or message content are ever sent to the API.

---

## Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Pixelation Modes](#pixelation-modes)
- [Batch Processing](#batch-processing)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [OpenClaw Integration](#openclaw-integration)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| | |
|---|---|
| 🔒 **Privacy-first** | Only compressed image bytes reach the API. No text, usernames, or message content is ever included in the prompt. |
| 📱 **App-agnostic** | Works on screenshots from any messaging app, in any UI language. |
| 🎯 **Selective redaction** | Hide chat names, profile pictures, and display names independently — or all at once. |
| 🎨 **Two visual styles** | Soft Gaussian blur (mode A) for a natural look, or hard block mosaic (mode B) for classic censorship. |
| ♻️ **Fault-tolerant** | If the API or JSON parsing fails for an image, the original is copied unchanged and the batch continues — it never crashes. |
| 🔁 **Auto-retry** | Up to 3 attempts with exponential back-off on API failure. |
| 🌐 **Proxy support** | Configurable via standard `HTTP_PROXY` / `HTTPS_PROXY` environment variables. |

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                      Input image                        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  vision.py                                              │
│  • Compress to ≤ 1024px on longest side                 │
│  • Encode as base64 JPEG                                │
│  • POST to OpenRouter  (gemini-3.1-pro-preview)         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  prompts.py                                             │
│  • App-agnostic, element-aware JSON prompt              │
│  • Requests bounding boxes for selected elements only   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼  normalized coords (0 – 1000)
┌─────────────────────────────────────────────────────────┐
│  process.py                                             │
│  • Parse JSON response                                  │
│  • Scale normalized coords → full-resolution pixels     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  pixelate.py                                            │
│  • Mode A: Gaussian blur with feathered edges           │
│  • Mode B: block mosaic (nearest-neighbour resize)      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              {stem}_pixelated.png                       │
└─────────────────────────────────────────────────────────┘
```

Normalized coordinates (0–1000) are mapped back to the original full-resolution image before pixelation, so output quality is fully independent of API compression.

---

## Requirements

- **Python 3.10+**
- An [OpenRouter](https://openrouter.ai/keys) API key (free tier available)

| Package | Version | Purpose |
|---|---|---|
| [`Pillow`](https://python-pillow.org) | ≥ 10.0.0 | Image loading, blurring, mosaic pixelation |
| [`requests`](https://requests.readthedocs.io) | ≥ 2.31.0 | HTTP calls to the OpenRouter API |
| [`python-dotenv`](https://pypi.org/project/python-dotenv/) | ≥ 1.0.0 | Load API key from a `.env` file |

---

## Installation

```bash
# 1. Clone
git clone https://github.com/frankz2020/chatmask.git
cd chatmask

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
cp .env.example .env
```

Then open `.env` and set your key:

```dotenv
OPENROUTER_API_KEY=sk-or-v1-...
```

Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys).

---

## Usage

```
python process.py <input_dir> <output_dir> [--elements <list>] [--pixel-mode <A|B>]
```

### Quick examples

```bash
# Redact everything — chat name, profile pics, and display names (default)
python process.py ./input ./output

# Hide only profile pictures
python process.py ./input ./output --elements profile_pic

# Hide chat name + display names, block mosaic style
python process.py ./input ./output --elements chat_name,display_name --pixel-mode B
```

### What gets hidden

| Element | `--elements` key | What it targets |
|---|---|---|
| Chat name | `chat_name` | Title text in the top navigation / header bar |
| Profile pictures | `profile_pic` | Circular / rounded avatars next to message bubbles |
| Display names | `display_name` | Sender name labels next to message bubbles |

> Default when `--elements` is omitted: **all three**.

### CLI reference

| Flag | Default | Description |
|---|---|---|
| `--elements` | `chat_name,profile_pic,display_name` | Comma-separated elements to redact |
| `--pixel-mode` | `A` | `A` = soft blur/mist · `B` = hard block mosaic |

### Output

Each image is saved as **`{original_stem}_pixelated.png`** in the output directory.
Accepted input formats: `.png`, `.jpg`, `.jpeg`.

If the API or JSON parsing fails for any image, the original is copied to the output directory unchanged and a warning is printed. The run always completes.

```
=== Summary ===
Total:     5
Processed: 4
Skipped:   1
Output files:
  ./output/chat1_pixelated.png  [OK]
  ./output/chat2_pixelated.png  [OK]
  ./output/chat3_pixelated.png  [SKIPPED (API error: timeout)]
  ...
```

---

## Pixelation Modes

### Mode A — Soft blur / mist *(default)*

Gaussian blur with feathered edges. The blur radius scales automatically with the region size. Produces a smooth, "frosted glass" appearance.

```bash
python process.py ./input ./output --pixel-mode A
```

### Mode B — Block mosaic

Downscales the region to a small grid and upscales back with nearest-neighbour interpolation. Produces the familiar pixelation / censorship-bar look.

```bash
python process.py ./input ./output --pixel-mode B
```

---

## Batch Processing

`submit.sh` iterates over every immediate subdirectory of an input root, runs `process.py` on each one as a separate job, and writes a per-job log.

```bash
chmod +x submit.sh

# Process every subdirectory under ./data/screenshots
./submit.sh ./data/screenshots ./data/out

# Pass extra flags — they are forwarded to process.py for every job
./submit.sh ./data/screenshots ./data/out --elements profile_pic --pixel-mode B
```

Logs are written to `<output_root>/logs/<job_name>.log`.

---

## Configuration

All settings are loaded from `.env` (or real environment variables) at startup.

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | **Yes** | Your OpenRouter API key |
| `HTTP_PROXY` / `http_proxy` | No | HTTP proxy for API calls |
| `HTTPS_PROXY` / `https_proxy` | No | HTTPS proxy for API calls |

> Proxy support is particularly useful in network environments that block direct HTTPS, such as some corporate networks or regions in China.

---

## Project Structure

```
chatmask/
├── process.py           # CLI entry point — orchestrates the full pipeline
├── vision.py            # OpenRouter API client (compression · retry · proxy)
├── prompts.py           # Builds the element-aware bounding-box prompt
├── pixelate.py          # Gaussian blur (A) and block mosaic (B) pixelation
├── submit.sh            # Batch runner for multiple job directories
├── requirements.txt
├── .env.example
└── docs/
    └── openclaw_skill/
        └── SKILL.md     # OpenClaw AI agent skill (bilingual EN / ZH)
```

<details>
<summary><strong>Module responsibilities</strong></summary>

**`process.py`** — Parses CLI arguments, discovers input images, calls the vision API, converts normalized coordinates to pixel coordinates, applies pixelation, and saves output. On any per-image failure the original is copied and processing continues.

**`vision.py`** — Compresses the image to ≤ 1024px on the longest side before sending (reduces API cost and latency). Encodes as base64 JPEG and POSTs to the OpenRouter API. Retries up to 3 times with exponential back-off. Reads proxy settings from the environment.

**`prompts.py`** — Builds an app-agnostic, element-aware prompt that asks the vision model to return bounding boxes only for the requested elements. Uses a 0–1000 normalized coordinate space so the prompt is resolution-independent.

**`pixelate.py`** — Applies pixelation to a bounding-box region of a PIL Image. `mist_pixelate_region` uses Gaussian blur with a feathered alpha mask. `strong_pixelate_region` uses nearest-neighbour resize to create a block mosaic. Both accept `(x, y, width, height)` bounding boxes in pixels.

</details>

---

## OpenClaw Integration

`docs/openclaw_skill/SKILL.md` is a skill definition for the [OpenClaw](https://openclaw.ai) AI agent platform. It lets you send a screenshot to an OpenClaw-connected channel and ask in plain English or Chinese — the agent picks the right flags and runs the pipeline automatically.

<details>
<summary><strong>Setup instructions</strong></summary>

```bash
# 1. Copy the skill into your OpenClaw workspace
mkdir -p ~/.openclaw/workspace/skills/chat-screenshot-pixelate
cp docs/openclaw_skill/SKILL.md ~/.openclaw/workspace/skills/chat-screenshot-pixelate/

# 2. Tell the skill where chatmask lives
export CHAT_PIXELATE_PATH="/path/to/chatmask"

# 3. Reload skills
openclaw skill reload
```

</details>

Send a screenshot through your channel (Feishu, Telegram, etc.) and say:

| English | Chinese |
|---|---|
| *"Pixelate this chat screenshot"* | *"打码聊天截图"* |
| *"Hide the avatars and names"* | *"隐藏头像和昵称"* |
| *"Only blur the profile pictures"* | *"只模糊头像"* |

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding guidelines, and the pull request process.

Some ideas for good first contributions:

- **New element types** — reactions, timestamps, phone numbers
- **Additional pixelation styles** — solid fill, emoji overlay, redaction bar
- **Support for video frames** — extract frames, process, re-encode
- **GUI / drag-and-drop wrapper** — for non-technical users

Open an issue to discuss significant changes before writing code.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to abide by its terms.

---

## Security

Please do **not** open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md) for the responsible disclosure process and data handling notes.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a full history of notable changes.

---

## License

Released under the [MIT License](LICENSE). © 2026 chatmask contributors.
