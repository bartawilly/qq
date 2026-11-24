<p align="center">
  <img src="assets/qq-hero.svg" width="100%" alt="qq mascots: a round purple Q raising its hand with a question, and a teal Q holding question cards, next to a queue of question cards that turns into an answered check when you are back">
</p>

<h1 align="center">qq</h1>

<p align="center">
  <b>Your coding agent asked you something an hour ago. You never saw it, and it's been frozen ever since.</b><br>
  qq is the question queue for coding agents: questions wait as cards until you're back, each is asked exactly once, and your answer is never lost.
</p>

<p align="center">
  <a href="https://github.com/bartawilly/qq/actions/workflows/test.yml"><img src="https://github.com/bartawilly/qq/actions/workflows/test.yml/badge.svg" alt="tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/bartawilly/qq" alt="MIT license"></a>
  <a href="https://github.com/bartawilly/qq/releases"><img src="https://img.shields.io/github/v/release/bartawilly/qq" alt="latest release"></a>
</p>

## Sound familiar?

- **You stepped away, and everything stopped.** Your agent opened a question box, froze until you came back, and so did everything it was running.
- **The question scrolled away.** It was asked in chat, buried in a long transcript or lost in a context compaction, and never asked again.
- **Two sessions asked you the same thing.** Worded differently, so now you have two different answers on record.
- **You came back to "Approve option B for PROJ-482?"** No context, no example, no idea.
- **None of the options fit.** And there was nowhere to say "neither, and here's why".

## What qq does

Every question becomes a **card**: a small Markdown file in your project's `.qq/` folder.

| | |
|---|---|
| **Asked when you're here** | Cards wait while you're away. Nobody freezes, and other work keeps moving. |
| **Asked once** | A card is claimed by an atomic file move before it's asked, so parallel sessions can't double-ask. |
| **Asked properly** | Every card says what happens today, who it affects, gives an example with numbers, and makes an honest recommendation. |
| **Your words count** | Every question keeps a free-text answer. Pick an option, add a condition, or push back: the agent studies what you said and re-asks if needed. |
| **Nothing lost** | Your answer is written into the card, word for word. |

## Install

**Claude Code: the full version** (skill, CLI and the hooks that enforce it):

```text
/plugin marketplace add bartawilly/qq
/plugin install qq@qq
```

**Any agent: Codex, Cursor, Gemini CLI, Claude Code and more** (skill and CLI, through [skills.sh](https://skills.sh)):

```bash
npx skills add bartawilly/qq
```

| You get | Plugin (Claude Code) | skills.sh (any agent) |
|---|:-:|:-:|
| Card template, rules and the `qq` CLI | ✅ | ✅ |
| Atomic claim, so a card is never asked twice | ✅ automatic | ✅ via `qq claim` |
| Question boxes refused while you're away | ✅ | — |
| Answers recorded automatically | ✅ | — via `qq answer` |
| Reminders when you come back | ✅ | — |

**Then turn it on in a repository.** qq is opt-in, so nothing changes anywhere else:

```bash
python3 <skill folder>/scripts/qq.py init     # or just ask your agent: "use qq here"
```

Installed through skills.sh into Claude Code? Run `qq.py setup` once to add the hooks. It backs up your settings first, and `setup --remove` undoes it.

Needs Python 3.9+ as `python3`, and nothing else. On a fresh Mac, `python3` may first prompt you to install Apple's command-line tools.

## A card

```markdown
# Q0007 · Should a late cancellation still get a refund?
- Owner: billing-agent (payments lead)
- Blocks: the refund-policy PR

## Today, step by step
A guest who cancels inside 48 hours is refunded in full; nothing checks the timing.

## Who meets it, and how often
About 1 booking in 20; on a €2,000 trip we lose the full amount.

## Options
1. 50% refund inside 48 h (Recommended): guest sees the rule at checkout; ~€1,000 kept per case.
2. Keep full refunds: nothing changes.

## Recommendation: option 1 · leaning
- Why: protects revenue without surprising guests, because the rule shows before they pay.
- What would change my mind: if most late cancellations are weather-related.
```

## How it works

```mermaid
flowchart LR
  A[Agent needs a decision] --> B["qq new → .qq/open/"]
  B -->|you're away| W[wait; keep working]
  W --> C
  B -->|you're here| C[claim → .qq/asking/]
  C --> D[ask: options + your own answer]
  D -->|option| E["recorded → .qq/closed/"]
  D -->|your own words| F[agent studies it → applies or re-asks]
```

[docs/design.md](docs/design.md) covers how presence is detected, who asks which card, and the safety rules: every hook fails open, and qq never answers a box for you.

## Configure

| Variable | Default | Meaning |
|---|---|---|
| `QQ_AWAY_MINUTES` | `60` | No typed message for this long means you're away |
| `QQ_MIN_QUESTION` | `120` | Minimum question length, so it carries context |
| `QQ_MIN_OPTION` | `60` | Minimum length of each option's explanation |
| `QQ_OWNER` | | Default owner name for `qq new` |

`qq off` turns the hooks off in one project, and `qq on` turns them back on. Linked git worktrees share the main worktree's queue, so parallel sessions in worktrees still never double-ask.

**To uninstall:** `/plugin uninstall qq@qq` (or `qq.py setup --remove` for a skills.sh install), then delete the `.qq/` folders you no longer need.

## What qq doesn't do

- **No inbox app, no server, no account.** Cards are plain files you can read in any editor.
- **Nothing in repositories you didn't opt in.** Without a `.qq/` folder, qq does nothing. A `.qq/` committed to git is ignored, so a cloned repository can never plant questions in your sessions.
- **No enforcement outside Claude Code (yet).** Other agents follow the protocol through the skill and CLI. Hook support for Codex is the next step.
- **Never answers for you.** The hooks only ever refuse a question box. They never fill one in.

## Contributing

Issues and PRs are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). Run the tests with `python3 tests/test_qq.py`.

## License

[MIT](LICENSE)
