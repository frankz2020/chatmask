# ChatMask Skill — Release Notes

## v1.1.0 — 2026-03-19

### No API key required

ChatMask no longer requires an OpenRouter API key when used as an OpenClaw skill.
The agent's own built-in AI now handles image analysis directly. Bounding-box
coordinates are passed to the local Python script via `--bbox-json`; the script
performs only image manipulation using Pillow. No credentials are requested,
stored, or written to disk.

**Before:** Setup prompted for an `OPENROUTER_API_KEY`, wrote it to `.env`, and
made one outbound HTTP call per image to OpenRouter.

**After:** Zero credentials. Zero runtime network calls. All processing is local.

### What changed for existing users

- If you previously configured a key in `.env`, it is still read by `process.py`
  in standalone CLI mode — nothing breaks.
- The skill Setup block no longer includes step 4 (API key configuration).
  Re-running Setup is safe and idempotent.
- The workflow now processes each image individually in its own isolated
  invocation. If you have a custom wrapper that called `process.py` with a
  shared directory of multiple images together with `--bbox-json`, update it to
  call once per image.

### Per-image correctness fix

The previous workflow staged all user images into one directory and called
`process.py` once with a single bounding-box JSON. Since different screenshots
have different element positions, images beyond the first received incorrect
coordinates. This is now prevented at two levels:

1. `process.py` exits with an error if `--bbox-json` is used with more than one
   image in the input directory.
2. The SKILL.md workflow explicitly loops per image — analyse one, pixelate it,
   then move to the next.

### Security improvements

| Concern | Resolution |
|---|---|
| Credential prompt and `.env` write in skill Setup | Removed entirely |
| Wildcard glob copying all inbound media | Replaced with explicit per-filename copy |
| `assert` on missing API key (could be silenced) | Replaced with `ValueError` with a message that explains standalone-only context |
| No `metadata` gates in skill frontmatter | Added `requires.bins: [python3, git]` and `homepage` |
| No audited commit reference in `git clone` | Pinned commit SHA annotated in Setup block |

### Standalone CLI unchanged

Running `process.py` directly without `--bbox-json` still works exactly as
before — it calls the OpenRouter API using the key from `.env`. The key is now
described as "standalone only" in `.env.example` and all relevant docs.
