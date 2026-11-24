# Contributing to qq

Thanks for helping. qq is small on purpose: one Python file, no dependencies, and plain Markdown cards. Please keep it that way.

## Quick start

```bash
git clone https://github.com/bartawilly/qq && cd qq
python3 tests/test_qq.py          # the whole suite, fully isolated, about 25 s
```

To try your changes in Claude Code, add your clone as a local marketplace:

```text
/plugin marketplace add /path/to/your/clone
/plugin install qq@qq
```

## Ground rules

- **Fail open.** A hook must never block a prompt or a question box because of its own bug. On error, print nothing and exit 0.
- **Never `allow`.** The gate only ever denies. `allow` with `updatedInput` would answer the box for the human.
- **Test first.** Every behaviour change comes with a case in `tests/test_qq.py` that fails without it.
- **Keep cards human.** The card template is for a person returning cold: plain words, real-looking numbers, an honest recommendation.
- **Standard library only**, Python 3.9+.

## Pull requests

- One change per PR. Say what a user sees differently.
- Paste the last line of `python3 tests/test_qq.py`.
- Update `README.md`, `docs/design.md` or the skill when behaviour changes, and add a line to `CHANGELOG.md`.

## Ideas we'd love help with

- Hook support for Codex CLI and other agents with hooks.
- Better presence detection outside Claude Code.
