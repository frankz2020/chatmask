# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.1.1] — 2026-03-19

### Added
- `--bbox-json` flag on `process.py`: accepts pre-computed bounding-box JSON (or `-` for stdin), bypassing the vision API entirely. No `OPENROUTER_API_KEY` is required when this flag is used. Input directory must contain exactly one image per invocation.
- OpenClaw skill (`SKILL.md`) now uses the agent's own built-in AI for image analysis instead of routing through OpenRouter — zero credentials required, zero runtime network calls.
- `metadata` frontmatter in `SKILL.md`: explicit `requires.bins` gates (`python3`, `git`) and `homepage` link so OpenClaw can surface and gate the skill correctly.
- `requirements-standalone.txt`: separates the `requests` package (only needed for standalone/OpenRouter mode) from the skill-mode install, so the skill setup installs the minimum possible footprint.

### Changed
- `SKILL.md` workflow restructured for correctness: each image is now analysed and pixelated in its own isolated invocation (separate `$IN_DIR` per image). Previously a single `process.py` call covered all images with one shared bounding-box dict, which would silently apply one image's coordinates to all others.
- `process.py` enforces the single-image constraint when `--bbox-json` is supplied: exits with a clear error if more than one image is found in the input directory.
- `vision.py`: replaced bare `assert` on missing API key with a `ValueError` whose message explicitly identifies the standalone-only context and points OpenClaw users to `--bbox-json`.
- `dotenv` and `vision` imports are now lazy (loaded only in the standalone code path), so `process.py` has zero module-level side-effects and passes ruff E402.
- Removed three spurious `f`-string prefixes (ruff F541).
- Removed `OpenRouter` badge from README header; updated Features table, How It Works diagrams, Requirements, Installation, Usage, Configuration, and module descriptions to accurately reflect both operating modes.
- Dependency versions in `requirements.txt` pinned exactly (`Pillow==11.2.1`, `python-dotenv==1.2.2`) — previously `>=` floor bounds allowed silent upgrades to unreviewed versions.

### Security
- Eliminated credential prompt and `.env` write from the OpenClaw skill Setup block. No secret is ever requested, stored on disk, or written by the skill.
- Narrowed inbound file copy from a wildcard glob (`*.{png,jpg,jpeg}`) to explicit per-image copy, limiting file-system access to only the files the user sent.
- Skill Setup now executes `git checkout <sha>` after cloning, enforcing the pinned audited commit (`62b0d1132e8cad8455ef29f74a98da486ff102d4`). Previously the SHA was documented in a comment but never actually checked out, so installs silently tracked the branch tip.
- Replaced all remaining `assert` statements in `process.py` with explicit `ValueError` / `sys.exit(1)` calls. `assert` can be silenced by running Python with `-O`, which would have bypassed input validation in `_parse_elements()`, `_parse_json_response()`, and the input-directory existence check.
- Removed `requests` from `requirements.txt` (skill-mode install). The package is only used by `vision.py` in standalone mode and had no purpose in skill operation; its presence in the install unnecessarily added a network-capable dependency.

---

## [1.0.0] — 2026-03-18

Initial public release.

### Added
- `process.py` — CLI entry point; orchestrates the full pipeline
- `vision.py` — OpenRouter API client with image compression, retry, and proxy support
- `prompts.py` — App-agnostic, element-aware bounding-box prompt builder
- `pixelate.py` — Gaussian blur (mode A) and block mosaic (mode B) pixelation
- `submit.sh` — Batch runner for multiple job directories with per-job logging
- Support for `chat_name`, `profile_pic`, and `display_name` element types
- Normalized coordinate system (0–1000) for resolution-independent bbox detection
- Fault-tolerant processing: failed images are copied unchanged; the batch never crashes
- Proxy support via `HTTP_PROXY` / `HTTPS_PROXY` environment variables
- OpenClaw AI agent skill (`docs/openclaw_skill/SKILL.md`) — bilingual EN/ZH
- MIT License

[Unreleased]: https://github.com/frankz2020/chatmask/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/frankz2020/chatmask/compare/v1.0.0...v1.1.1
[1.0.0]: https://github.com/frankz2020/chatmask/releases/tag/v1.0.0
