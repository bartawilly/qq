# qq design

qq is a question queue for coding agents. Agents write each question they need a human to answer as a small **card** file. The cards are asked when the human is actually there, each one exactly once, and answers are recorded next to the question.

## Problems it solves

1. **A question box freezes its session.** An agent that opens a blocking question while the human is away waits for hours, and everything it was coordinating waits with it.
2. **Questions asked in chat get lost.** They scroll away in a long transcript, or die in a context compaction.
3. **Parallel sessions ask the same thing twice.** Sometimes they also word it differently and get two different answers.
4. **Questions arrive without context.** The human returns to a terse question, with ticket keys and no example, and can't answer it.
5. **There is no room for "neither, and here's why".** The human's own words get treated as a non-answer.

## Two layers

| Layer | Works in | What it does |
|---|---|---|
| **Portable core** (the skill + `qq.py` CLI) | Any agent that loads Agent Skills (Claude Code, Codex, Cursor, Gemini CLI, …) | Card template and rules; `qq new / claim / answer / release / list / away` keep the folder consistent; an atomic claim prevents double-asks |
| **Enforcement** (the Claude Code plugin's hooks) | Claude Code | A gate on `AskUserQuestion`; automatic claim and answer recording; a reminder on each message; presence detection |

Both layers share one folder in the project, `.qq/`, kept out of git by its own `.gitignore`.

**Opt-in, one queue per repository.** The hooks act only where a queue already exists, and they never create one. The queue is found in this order:
1. `QQ_DIR`;
2. the nearest `.qq/` above the project folder;
3. the `.qq/` of the repository's **main** worktree, so linked worktrees share one queue and parallel sessions can't double-ask.

If none is found, qq does nothing. `qq init` (or the first `qq new`) creates the queue.

```
.qq/
  open/      cards waiting to be asked        Q0001-<slug>.md
  asking/    claimed by the session asking now, or holding a typed answer it must act on
  closed/    answered or withdrawn
  .state/    presence timestamps, hook log (hook-managed)
```

## The card

The template has these sections:
- **Today, step by step:** what the system does now, verified.
- **Who meets it, and how often.**
- **An example** with real-looking numbers.
- **Numbered options.**
- **An honest recommendation:** why it beats both the simpler and the bigger option, what would change the agent's mind, and firm or leaning.

One decision per card. The owner writes it, and anyone who asks it uses it word for word.

## Lifecycle

`open → asking → closed`. Every move is a `rename(2)` in one folder tree, so it is atomic: when two sessions claim the same card, exactly one wins.

Ids are sequential (`Q0001`, `Q0002`, …), reserved with `O_EXCL` in `.qq/.state/ids/`, so they never collide and never repeat.

- **The claim:** made by the gate hook in Claude Code; elsewhere by `qq claim <id>` before asking.
- **An option answer:** closes the card.
- **A typed answer** (the human's own words): stays in `asking/` until the asking agent studies it, then applies it or re-asks an updated card.
- **A dismissed or "clarify" box:** its claim is released on the human's next typed message (Claude Code), or by `qq release` (elsewhere).
- **A session that ends:** a `SessionEnd` hook releases its unanswered claims.
- **A crashed asker's claim:** released after 30 min when its session record (`~/.claude/sessions`, POSIX only) shows the process is gone; otherwise after 2 h.

## Presence (Claude Code)

- **Who counts as present:** the human typed in the last 60 min (`QQ_AWAY_MINUTES`), and has not said they're leaving (`qq away`).
- **Proof, not guessing:** scheduled prompts look like typed text, and the prompt hook runs before the prompt reaches the transcript. So a detached check confirms presence a few seconds later, from the transcript's `promptSource: typed`. If a transcript has no such field at all (a format change), qq falls back to trusting the prompt text, so it fails open rather than locking every box.
- **The gate also checks** the asking session's own transcript for a recent typed message.

## Who asks

- **Owners ask their own cards,** at the end of their turn.
- **The desk:** the session the human is typing to also asks *orphans*. An orphan is a card still unclaimed 10 min after the human came back. A just-released card is held for 30 min, while its owner explains.

## The gate's quality floor

| Rule | Why |
|---|---|
| Question ≥ 120 chars (`QQ_MIN_QUESTION`), not counting the hint line | The box can hide the chat above it, so the question must carry today, the problem and the example |
| Each option description ≥ 60 chars (`QQ_MIN_OPTION`) | A bare "Skip it" says nothing about what happens |
| No option `preview` | Inferred from usage: the preview layout drops the free-text "Other" row, and that row is how the human answers in their own words |

## Safety

- **Every hook is fail-open:** an error prints nothing and exits 0.
- **The only decision the gate ever emits is `deny`.** It never emits `allow`, because `allow` with `updatedInput` would answer the box on the human's behalf.
- **Outside the project:** the hooks write only inside `.qq/`, and read only the session's own transcript and `~/.claude/sessions/*.json` (never key files).
- **Per-project opt-out:** `qq off` writes `.qq/off`, and the hooks then stay silent.
- **No planted cards:** a `.qq/` tracked by git is ignored, so a cloned repository can't inject card text into your prompts. Card text shown to agents is labelled as data and stripped of control characters.
- **No symlink tricks:** symlinked queue folders and card files are refused, and every write uses `O_NOFOLLOW`.
- **Settings stay private:** the backup and temp files `qq setup` writes are created private and keep the original file's mode.
- **Safe to install twice** (plugin plus `setup`): tool events dedupe on `tool_use_id`, the handlers are idempotent, and a prompt reminder prints once.
- **Windows:** there is no process-liveness check, because `os.kill(pid, 0)` would send Ctrl-C there. A crashed asker's claim is freed after 2 h.

## Not handled (on purpose)

| Case | Why |
|---|---|
| A central inbox UI | Cards are plain files, readable in any editor |
| Push notifications from the hook | The agent can send its own, where its harness offers one |
| Enforcement in agents without hooks | The skill and CLI carry the protocol; the gate is Claude Code only |

## Install routes, and what each one gives

| Route | Gives | Notes |
|---|---|---|
| **Claude Code plugin** (`/plugin marketplace add bartawilly/qq`, then `/plugin install qq@qq`) | Skill, CLI and hooks | The full version. Hooks are wired by the plugin system and updated with the plugin |
| **skills.sh** (`npx skills add bartawilly/qq`) in Claude Code | Skill and CLI. Hooks after one command: `qq.py setup` | Setup adds four hook entries to `~/.claude/settings.json`: idempotent, backed up first, undone by `qq.py setup --remove`. It refuses when the qq plugin is already installed, so hooks never run twice. This is the same pattern other hook-bearing skills use (a plugin auto-wires; a skill copy wires with one command) |
| **skills.sh** in Codex, Cursor, Gemini CLI and others | Skill and CLI | The protocol works through `qq.py`, but there is no automatic gate. Codex has hooks of its own, so wiring qq to them is a later step once its question tool and hook payloads are verified |

The README states this table plainly, so nobody believes they are protected by checks they don't have.
