# Changelog

## 0.1.1

- **Headless runs never count as you being here.** `claude -p` and Agent SDK runs record an `sdk-*` entrypoint, so a scheduled job in a qq repository can no longer mark you present and let other sessions open question boxes while you're away. Found in the live install check.
- **Trust entries carry a random nonce,** because file systems such as ext4 reuse inode numbers.
- **CI tests Python 3.10 and 3.13** on Ubuntu and macOS.

## 0.1.0

First public release.

- **Cards:** question cards in `.qq/`, with a template built for a human returning cold.
- **Claim:** an atomic claim, so no card is asked twice across parallel sessions.
- **Claude Code hooks:**
  - a gate on `AskUserQuestion`: a card is required, no box opens while you're away, the free-text answer row is kept, and questions meet a minimum length;
  - automatic answer recording;
  - reminders when you come back.
- **The `qq` CLI:** new, list, claim, answer, release, reopen, withdraw, away/back, off/on, and setup.
- **Install:** a Claude Code plugin marketplace, and a skill for skills.sh (any agent). The `/qq` command comes with the plugin.
- **Opt-in and safe by default:**
  - opt-in per repository (`qq init`), with one queue shared by its git worktrees;
  - only queues you created are trusted;
  - symlinked or shared queues are refused;
  - safe to install as plugin and skill at once.
