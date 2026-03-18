# Security Policy

## Supported Versions

Only the latest version on the `main` branch receives security fixes.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

If you discover a security issue, report it privately by emailing the maintainers or using [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability) feature on this repository.

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce or a minimal proof-of-concept
- Any suggested mitigations (optional but appreciated)

You can expect an acknowledgement within **72 hours** and a fix or mitigation plan within **14 days** for confirmed vulnerabilities.

## Privacy and Data Handling Notes

chatmask is a privacy tool, so the following design decisions are worth documenting:

- **Only image bytes are transmitted.** The vision API call sends a compressed JPEG of the screenshot and a structured prompt describing which visual elements to locate. No raw message text, contact names, or any other extracted data is included in API payloads.
- **The API key is never logged.** `vision.py` reads the key from the environment and places it in the `Authorization` header only. It is not echoed, printed, or stored anywhere.
- **No data is persisted beyond the output directory.** The tool writes pixelated PNG files to the output directory you specify. No other data is written to disk.
- **Proxy support.** If your environment requires a proxy, set `HTTP_PROXY` / `HTTPS_PROXY`. Traffic is otherwise sent directly to `openrouter.ai`.

## Dependency Security

Dependencies are intentionally minimal (`Pillow`, `requests`, `python-dotenv`). Keep them up to date with `pip install -r requirements.txt --upgrade` to pick up upstream security patches.
