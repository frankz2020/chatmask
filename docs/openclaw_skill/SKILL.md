---
name: chatmask
description: >-
  Pixelate chat/messaging app screenshots (WeChat, WhatsApp, Telegram, iMessage,
  Slack, Discord, etc.) to hide chat name, profile pics, and/or display names.
  Use when the user sends chat screenshots and asks to pixelate, blur, anonymize,
  redact, or hide identity elements. Supports English and Chinese prompts.
  Triggers: pixelate chat screenshot, blur names and avatars, anonymize chat,
  hide profile pics, redact chat, 打码聊天截图, 隐藏头像和昵称, 像素化截图,
  模糊聊天信息, 打码, 匿名截图, 隐藏头像, 隐藏昵称, 隐藏聊天名称
---

# ChatMask Skill

When the user sends chat screenshots and asks to pixelate or hide identity
elements, follow the steps below in order: **Setup → Workflow**.

---

## Setup (run once, idempotent)

Run this block before the first job. Every step is guarded so re-running is safe.

```bash
# Default install path — override by setting CHAT_PIXELATE_PATH before calling the skill
CHAT_PIXELATE_PATH="${CHAT_PIXELATE_PATH:-$HOME/.openclaw/skills/chatmask}"

# 1. Clone repo if not already present
if [ ! -d "$CHAT_PIXELATE_PATH/.git" ]; then
  git clone https://github.com/frankz2020/chatmask.git "$CHAT_PIXELATE_PATH"
fi

# 2. Create virtualenv if not already present
if [ ! -d "$CHAT_PIXELATE_PATH/.venv" ]; then
  python3 -m venv "$CHAT_PIXELATE_PATH/.venv" \
    || { apt-get install -y python3-venv && python3 -m venv "$CHAT_PIXELATE_PATH/.venv"; }
fi

# 3. Install / upgrade dependencies
"$CHAT_PIXELATE_PATH/.venv/bin/pip" install -q -r "$CHAT_PIXELATE_PATH/requirements.txt"

# 4. Configure API key
if [ ! -f "$CHAT_PIXELATE_PATH/.env" ]; then
  cp "$CHAT_PIXELATE_PATH/.env.example" "$CHAT_PIXELATE_PATH/.env"
fi

if ! grep -q "^OPENROUTER_API_KEY=sk-" "$CHAT_PIXELATE_PATH/.env" 2>/dev/null; then
  echo "⚠️  No OpenRouter API key found."
  echo "Please provide your OPENROUTER_API_KEY (get a free key at https://openrouter.ai/keys):"
  # Ask the user for the key, then write it:
  # sed -i "s|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=<key provided by user>|" "$CHAT_PIXELATE_PATH/.env"
fi

export CHAT_PIXELATE_PATH
PYTHON="$CHAT_PIXELATE_PATH/.venv/bin/python3"
```

> **API key prompt:** If the key check above fails, ask the user:
> *"Please paste your OpenRouter API key so I can configure ChatMask. Get a free key at https://openrouter.ai/keys."*
> Then run:
> ```bash
> sed -i "s|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=<user_key>|" "$CHAT_PIXELATE_PATH/.env"
> ```

---

## Workflow

Read **Element Selection** and **Option Configuration** to translate natural-language
requests into the correct flags before running.

### 1. Stage input images

```bash
JOB_ID="job_$(date +%s)"
IN_DIR="/tmp/chat_pixelate_in_$JOB_ID"
OUT_DIR="/tmp/chat_pixelate_out_$JOB_ID"
mkdir -p "$IN_DIR" "$OUT_DIR"

cp ~/.openclaw/media/inbound/*.{png,jpg,jpeg} "$IN_DIR/" 2>/dev/null || true
```

### 2. Run pixelation

```bash
"$PYTHON" "$CHAT_PIXELATE_PATH/process.py" \
    "$IN_DIR" \
    "$OUT_DIR" \
    [OPTIONS]   # see Element Selection and Option Configuration below
```

### 3. Return results to user

```bash
ls "$OUT_DIR/"*_pixelated.png
```

Attach or share the processed images from `$OUT_DIR/`.

---

## Element Selection

Translate the user's intent to `--elements`. Default (no flag) pixelates all three.

| User says (EN / 中文) | `--elements` flag |
|---|---|
| all / default / 全部 / 默认 / 全部打码 | *(omit flag — default: all three)* |
| chat name only / 只隐藏聊天名称 | `--elements chat_name` |
| profile pics only / 只隐藏头像 | `--elements profile_pic` |
| display names only / 只隐藏昵称 / 只隐藏用户名 | `--elements display_name` |
| avatars and display names / 隐藏头像和昵称 | `--elements profile_pic,display_name` |
| chat name and avatars / 隐藏聊天名称和头像 | `--elements chat_name,profile_pic` |
| chat name and display names / 隐藏聊天名称和昵称 | `--elements chat_name,display_name` |

**Element definitions:**
- **chat_name**: Title text in the top navigation bar (group name, contact name, channel title)
- **profile_pic**: Circular/rounded avatar images next to message bubbles
- **display_name**: Text username/nickname labels next to or above message bubbles

---

## Option Configuration

| User says (EN / 中文) | Flag |
|---|---|
| soft blur / mist effect / 模糊效果 / 雾化（默认）| `--pixel-mode A` *(default)* |
| block / mosaic / pixelate blocks / 马赛克 / 方块效果 | `--pixel-mode B` |

---

## Full Example (copy-paste ready)

```bash
# (Assumes Setup block has already run and exported CHAT_PIXELATE_PATH and PYTHON)

JOB_ID="job_$(date +%s)"
IN_DIR="/tmp/chat_pixelate_in_$JOB_ID"
OUT_DIR="/tmp/chat_pixelate_out_$JOB_ID"
mkdir -p "$IN_DIR" "$OUT_DIR"

cp ~/.openclaw/media/inbound/*.{png,jpg,jpeg} "$IN_DIR/" 2>/dev/null || true

# Default: pixelate all three elements with soft blur
"$PYTHON" "$CHAT_PIXELATE_PATH/process.py" "$IN_DIR" "$OUT_DIR"

echo "=== Output images ==="
ls "$OUT_DIR/"*_pixelated.png
```

### More examples

```bash
# Only blur profile pics (avatars)
"$PYTHON" "$CHAT_PIXELATE_PATH/process.py" "$IN_DIR" "$OUT_DIR" \
    --elements profile_pic

# Hide chat name and display names, block mosaic style
"$PYTHON" "$CHAT_PIXELATE_PATH/process.py" "$IN_DIR" "$OUT_DIR" \
    --elements chat_name,display_name \
    --pixel-mode B

# Hide avatars and nicknames, soft blur
"$PYTHON" "$CHAT_PIXELATE_PATH/process.py" "$IN_DIR" "$OUT_DIR" \
    --elements profile_pic,display_name \
    --pixel-mode A
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `OPENROUTER_API_KEY ... required` | Missing API key | Follow the API key prompt in Setup step 4 |
| `python3 -m venv` fails | Missing venv module | Run `apt-get install -y python3-venv` then re-run Setup |
| `git clone` fails | No git installed or no network | Run `apt-get install -y git` or check network connectivity |
| `No images found in input directory` | Copy step failed | Check `ls $IN_DIR/` |
| Image copied unchanged with `SKIPPED` in summary | Vision API or parse failure | Check printed warning for details; retry or check API key |
| Wrong regions pixelated | Model misidentified elements | Try `--pixel-mode B` or report the screenshot type |
