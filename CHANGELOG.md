# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Open-source community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- GitHub issue templates (bug report, feature request)
- Pull request template
- GitHub Actions CI workflow (lint + import check)

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

[Unreleased]: https://github.com/your-username/chatmask/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-username/chatmask/releases/tag/v1.0.0
