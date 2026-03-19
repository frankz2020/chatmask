<div align="center">

# 🎭 chatmask

**Automatically detect and redact identities in chat screenshots — locally, in seconds.**

[![CI](https://github.com/frankz2020/chatmask/actions/workflows/ci.yml/badge.svg)](https://github.com/frankz2020/chatmask/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Pillow](https://img.shields.io/badge/image%20processing-Pillow-orange)](https://python-pillow.org)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa)](CODE_OF_CONDUCT.md)

Works with **any** messaging app — WeChat, WhatsApp, Telegram, iMessage, Slack, Discord, LINE, KakaoTalk, and more.
Supports English and Chinese UIs.

</div>

---

> **How it works in one sentence:** A vision model finds the sensitive regions; [Pillow](https://python-pillow.org) blurs them locally. Via the OpenClaw skill, your agent's own AI is the vision model — no extra API key needed. In standalone mode, a Gemini vision model via OpenRouter locates regions; only compressed image bytes leave your machine — no text, names, or message content are ever sent.

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
- [OpenClaw Skill](#openclaw-skill)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| | |
|---|---|
| 🔒 **Privacy-first** | Via the OpenClaw skill, all processing is local — no data leaves the machine. In standalone mode, only compressed image bytes reach the API; no text, usernames, or message content is ever sent. |
| 📱 **App-agnostic** | Works on screenshots from any messaging app, in any UI language. |
| 🎯 **Selective redaction** | Hide chat names, profile pictures, and display names independently — or all at once. |
| 🎨 **Two visual styles** | Soft Gaussian blur (mode A) for a natural look, or hard block mosaic (mode B) for classic censorship. |
| ♻️ **Fault-tolerant** | If the vision step or JSON parsing fails for an image, the original is copied unchanged and the batch continues — it never crashes. |
| 🔁 **Auto-retry** | Standalone mode: up to 3 attempts with exponential back-off on API failure. |
| 🌐 **Proxy support** | Configurable via standard `HTTP_PROXY` / `HTTPS_PROXY` environment variables. |
| 🤖 **OpenClaw native** | First-class skill: no API key, no credential storage, per-image analysis by the agent's own AI. |

---

## How It Works

chatmask supports two operating modes that share the same pixelation engine.

### OpenClaw skill mode (no API key)

```
┌─────────────────────────────────────────────────────────┐
│              User sends screenshot to agent             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  OpenClaw agent (your existing AI)                      │
│  • Analyses the image with its own vision model         │
│  • Emits bounding-box JSON (normalised 0-1000 coords)   │
└────────────────────────┬────────────────────────────────┘
                         │  --bbox-json  (no network call)
                         ▼
┌─────────────────────────────────────────────────────────┐
│  process.py                                             │
│  • Parses JSON, scales coords → full-resolution pixels  │
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

### Standalone CLI mode (OpenRouter API key required)

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
                         │  normalized coords (0 – 1000)
                         ▼
┌─────────────────────────────────────────────────────────┐
│  process.py  →  pixelate.py                             │
│  • Parse response, scale coords, apply blur/mosaic      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              {stem}_pixelated.png                       │
└─────────────────────────────────────────────────────────┘
```

Normalized coordinates (0–1000) are mapped back to the original full-resolution image before pixelation, so output quality is fully independent of any compression applied during analysis.

---

## Requirements

- **Python 3.10+**

| Package | Version | Purpose |
|---|---|---|
| [`Pillow`](https://python-pillow.org) | ≥ 10.0.0 | Image loading, blurring, mosaic pixelation |
| [`requests`](https://requests.readthedocs.io) | ≥ 2.31.0 | HTTP calls to the OpenRouter API (standalone mode only) |
| [`python-dotenv`](https://pypi.org/project/python-dotenv/) | ≥ 1.0.0 | Load API key from a `.env` file (standalone mode only) |

**OpenRouter API key:** only required for standalone CLI use. When running via the OpenClaw skill, the agent's own AI handles image analysis and no key is needed. Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys) if you need standalone mode.

> **Privacy note:** In standalone mode, only compressed image bytes are sent to the API. No text, usernames, or message content is ever included in the prompt or leaves your machine. In OpenClaw skill mode, no data leaves the local Python script at all.

---

## Installation

```bash
# 1. Clone
git clone https://github.com/frankz2020/chatmask.git
cd chatmask

# 2. (Recommended) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

**OpenClaw skill users:** that's it — no API key needed. See [OpenClaw Skill](#openclaw-skill).

**Standalone CLI users:** also configure your OpenRouter key:

```bash
cp .env.example .env
```

Open `.env` and paste your key:

```dotenv
OPENROUTER_API_KEY=sk-or-v1-...
```

Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys) — no credit card required.

---

## Usage

```
python process.py <input_dir> <output_dir> [--elements <list>] [--pixel-mode <A|B>] [--bbox-json <json>]
```

### Quick examples

```bash
# Redact everything — chat name, profile pics, and display names (default)
# Standalone: calls OpenRouter API per image
python process.py ./input ./output

# Hide only profile pictures
python process.py ./input ./output --elements profile_pic

# Hide chat name + display names, block mosaic style
python process.py ./input ./output --elements chat_name,display_name --pixel-mode B

# OpenClaw skill mode: skip the API entirely — pass pre-analysed bounding boxes
# (input_dir must contain exactly one image when --bbox-json is used)
python process.py ./input ./output --bbox-json '{"chat_names":[...],"profile_pics":[...],"display_names":[...]}'

# Read bounding-box JSON from stdin
cat bbox.json | python process.py ./input ./output --bbox-json -
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
| `--bbox-json` | *(none)* | Pre-analysed bounding-box JSON string or `-` for stdin. Skips the vision API entirely. Input dir must contain exactly one image. |

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
The `.env` file is only needed for standalone CLI mode.

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | Standalone only | Your OpenRouter API key — get one free at [openrouter.ai/keys](https://openrouter.ai/keys). Not needed when using `--bbox-json` or the OpenClaw skill. |
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

**`process.py`** — Parses CLI arguments, discovers input images, and orchestrates the pipeline. Accepts `--bbox-json` for API-free operation (single image per call); falls back to `vision.py` for standalone use. Converts normalized coordinates to pixel coordinates, applies pixelation, and saves output. On any per-image failure the original is copied and processing continues.

**`vision.py`** — Used in standalone mode only. Compresses the image to ≤ 1024px on the longest side before sending (reduces API cost and latency). Encodes as base64 JPEG and POSTs to the OpenRouter API. Retries up to 3 times with exponential back-off. Reads proxy settings from the environment.

**`prompts.py`** — Builds an app-agnostic, element-aware prompt that asks a vision model to return bounding boxes only for the requested elements. Uses a 0–1000 normalized coordinate space so the prompt is resolution-independent. Used by `vision.py` in standalone mode; the same schema is replicated verbatim in `SKILL.md` for the OpenClaw agent.

**`pixelate.py`** — Applies pixelation to a bounding-box region of a PIL Image. `mist_pixelate_region` uses Gaussian blur with a feathered alpha mask. `strong_pixelate_region` uses nearest-neighbour resize to create a block mosaic. Both accept `(x, y, width, height)` bounding boxes in pixels.

</details>

---

## OpenClaw Skill

`docs/openclaw_skill/SKILL.md` is a skill definition for the [OpenClaw](https://openclaw.ai) AI agent platform. Install it once and you can send chat screenshots to any OpenClaw-connected channel and ask in plain English or Chinese — the agent handles everything automatically.

### Two ways to use chatmask

| | OpenClaw skill | Standalone CLI |
|---|---|---|
| **API key required?** | **No** — OpenClaw's own AI locates the regions | Yes — requires `OPENROUTER_API_KEY` |
| **Network calls at runtime?** | **None** — only local image processing | One call per image to OpenRouter |
| **Setup** | Clone + pip install (one-time) | Clone + pip install + set `.env` |
| **Best for** | Day-to-day use via chat/voice | Scripts, CI, headless automation |

**OpenClaw skill path:** The agent analyses each screenshot using its own built-in vision capabilities to produce bounding-box coordinates, then passes them to `process.py --bbox-json`. The Python script performs only local image manipulation — Pillow blurs the specified regions. No credentials are stored.

**Standalone CLI path:** `process.py` calls the OpenRouter API (`vision.py`) to get coordinates. You need an `OPENROUTER_API_KEY` in `.env`. Only compressed image bytes are sent — no text, usernames, or message content.

### What you need before installing the OpenClaw skill

| Requirement | Notes |
|---|---|
| OpenClaw running on a machine with Python 3.10+ and `git` | The skill auto-installs everything else. |
| Internet access on that machine | Needed once to clone the repo and install deps. |

### Install the skill

```bash
# 1. Copy the skill file into your OpenClaw workspace
mkdir -p ~/.openclaw/workspace/skills/chatmask
cp docs/openclaw_skill/SKILL.md ~/.openclaw/workspace/skills/chatmask/

# 2. Reload skills
openclaw skills
```

That's it. The skill handles cloning, venv creation, and dependency installation automatically the first time it runs.

> **Default install path:** `~/.openclaw/skills/chatmask`
> To use a custom location, set `CHAT_PIXELATE_PATH` before the skill runs:
> ```bash
> export CHAT_PIXELATE_PATH="/your/preferred/path"
> ```

### First-run flow

```
User: "打码聊天截图"
  → OpenClaw reads SKILL.md
  → Clones https://github.com/frankz2020/chatmask.git  (skipped if already present)
  → Creates .venv and installs requirements             (skipped if already present)
  → Agent analyses the image with its own vision model
  → Passes bounding-box JSON to process.py --bbox-json (no API key needed)
  → Returns pixelated result
```

Subsequent runs skip all setup steps and go straight to processing.

### Trigger phrases

| English | Chinese |
|---|---|
| *"Pixelate this chat screenshot"* | *"打码聊天截图"* |
| *"Hide the avatars and names"* | *"隐藏头像和昵称"* |
| *"Only blur the profile pictures"* | *"只模糊头像"* |
| *"Redact all identities, block style"* | *"马赛克方式隐藏全部"* |

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
