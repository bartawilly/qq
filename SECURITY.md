# Security

qq runs as Claude Code hooks on your machine, so we take its safety seriously:

- **Writes:** it only writes inside your project's `.qq/` folder, plus `~/.claude/settings.json` when you run `qq setup` (backed up first).
- **Reads:** your session's own transcript, and `~/.claude/sessions/*.json` (never key files).
- **Network:** none.
- **Decisions:** it never answers a question box for you. The gate can only refuse a box.

**Reporting a vulnerability:** use [private vulnerability reporting](https://github.com/bartawilly/qq/security/advisories/new). Please don't open a public issue. We aim to reply within a few days.
