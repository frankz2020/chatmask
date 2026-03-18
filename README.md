# chat_screenshot_pixelate

Pixelate identity elements in chat/messaging app screenshots to protect privacy.
Works with any messaging app — WeChat, WhatsApp, Telegram, iMessage, Slack,
Discord, LINE, KakaoTalk, etc. Supports English and Chinese UI/prompts.

Uses Gemini via OpenRouter to locate bounding boxes, then applies local PIL
pixelation (no data leaves your machine except the image sent to the vision API).

## What it hides

| Element | `--elements` key | Description |
|---|---|---|
| Chat name | `chat_name` | Title in top navigation bar |
| Profile pics | `profile_pic` | Avatar images next to message bubbles |
| Display names | `display_name` | Username/nickname text labels next to bubbles |

Default: all three.

## Setup

```bash
cd /home/ubuntu/chat_screenshot_pixelate

# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env and set: OPENROUTER_API_KEY=sk-or-v1-...
```

## Usage

```bash
# Pixelate all elements (default)
python3 process.py ./input ./output

# Hide only avatars
python3 process.py ./input ./output --elements profile_pic

# Hide chat name and display names, block mosaic style
python3 process.py ./input ./output --elements chat_name,display_name --pixel-mode B
```

### CLI options

| Flag | Default | Description |
|---|---|---|
| `--elements` | `chat_name,profile_pic,display_name` | Comma-separated elements to pixelate |
| `--pixel-mode` | `A` | `A` = soft blur/mist; `B` = hard block mosaic |

### Output

Each processed image is saved as `{original_stem}_pixelated.png` in `output_dir`.
If the vision API or JSON parsing fails for an image, the original is copied
unchanged and a warning is printed — the batch never crashes.

## Batch processing

Use `submit.sh` to process multiple job directories at once:

```bash
# Process all subdirs of ./data/screenshots
chmod +x submit.sh
./submit.sh ./data/screenshots ./data/out

# With extra flags (e.g. only avatars)
./submit.sh ./data/screenshots ./data/out --elements profile_pic
```

Logs per job are written to `./data/out/logs/<job_name>.log`.

## OpenClaw Integration

1. Copy the skill into your OpenClaw workspace:

   ```bash
   mkdir -p ~/.openclaw/workspace/skills/chat-screenshot-pixelate
   cp docs/openclaw_skill/SKILL.md ~/.openclaw/workspace/skills/chat-screenshot-pixelate/
   ```

2. Set the path in your environment:

   ```bash
   export CHAT_PIXELATE_PATH="/home/ubuntu/chat_screenshot_pixelate"
   ```

3. Reload skills:

   ```bash
   openclaw skill reload
   ```

4. Send chat screenshots through your channel (Feishu, Telegram, etc.) and ask:
   - "Pixelate this chat screenshot"
   - "Hide the avatars and names"
   - "打码聊天截图"
   - "隐藏头像和昵称"

The agent reads the SKILL.md to map your intent to the correct `--elements` flag and runs the pipeline automatically.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |
| `HTTP_PROXY` / `HTTPS_PROXY` | No | Proxy for API calls (useful in China) |

## Project structure

```
chat_screenshot_pixelate/
├── pixelate.py          # Mist/strong pixelation functions
├── vision.py            # OpenRouter API client with retry
├── prompts.py           # Element-aware bbox prompt builder
├── process.py           # Main CLI
├── submit.sh            # Batch runner for multiple job dirs
├── requirements.txt
├── .env.example
└── docs/
    └── openclaw_skill/
        └── SKILL.md     # OpenClaw skill (bilingual EN/ZH)
```
