# Security

qq runs as Claude Code hooks on your machine, so we take its safety seriously:

- **Writes:**
  - your project's `.qq/` folder;
  - its list of trusted queues in `~/.config/qq/trusted-queues`;
  - `~/.claude/settings.json`, only when you run `qq setup` (backed up first, private permissions kept).
- **Reads:**
  - your session's own transcript, to tell a message you typed from a scheduled one;
  - `~/.claude/sessions/*.json`, for session names and liveness (never the key files beside them);
  - `~/.claude/plugins/installed_plugins.json`, during `qq setup` only.
- **Processes:** after a message you type, a small background check (at most about 46 s) confirms it was typed by you.
- **Logs:** `.qq/.state/hook.log` keeps hook errors and up to 30 characters of each confirmed prompt. It rotates at 256 KB.
- **Network:** none.
- **Planted content:** qq acts only on queues it created itself, recorded by path and folder identity. An existing `.qq/` needs your explicit `qq init --trust-existing`, run in your own terminal with the path typed to confirm (agents cannot run it); it refuses one committed to git. Symlinked queue folders and card files are refused, and a queue writable by other users is ignored.
- **Decisions:** it never answers a question box for you. The gate can only refuse a box.

**Reporting a vulnerability:** use [private vulnerability reporting](https://github.com/bartawilly/qq/security/advisories/new). Please don't open a public issue. We aim to reply within a few days.
