---
name: qq
description: The question queue for coding agents. Use BEFORE asking the human anything — a decision, a permission, or an action only they can do — and whenever a qq reminder lists waiting cards. Write each question as a card in the project's .qq/ folder, claim it before asking so no other session asks it too, ask only while the human is present, keep their free-text answer possible, and record and act on what they said.
license: MIT
---

# qq: the question queue

Every question for the human is a **card**: one small Markdown file in the project's `.qq/` folder. A card waits until the human is present, it is asked exactly once, and the answer is written into it. This keeps your session from freezing on a question nobody is there to see, stops parallel sessions from asking twice, and means no answer gets lost in scrollback.

The helper sits next to this file: `scripts/qq.py` (Python 3.9+, no dependencies). Below, `qq` means `python3 <this skill's folder>/scripts/qq.py`.

```
.qq/open/     waiting to be asked
.qq/asking/   claimed by the session asking it now (or holding a typed answer to act on)
.qq/closed/   answered or withdrawn
```

## 1. Should you ask at all?

Ask only for:
- **decisions that are the human's:** product, money, scope, risk they must accept;
- **actions only they can do:** pay, rotate a key, change an account setting;
- **permissions they require:** touching production, publishing, spending.

Decide everything else yourself, with the simplest safe option, and say which you chose. Before filing a card, search `.qq/closed/` for the topic: if it is answered, apply that answer.

## 2. Write the card

Run `qq new <slug> --title "<the question in one plain line>" --owner "<your session name and role>"`. It prints the card's path, and its id (e.g. `Q241307`) is the start of the file name. Fill in every section. **One decision per card.**

- **Today, step by step:** what happens now, verified in the code or data. This is the section most often missing: the human does not carry your context.
- **Who meets it, and how often**, and what goes wrong.
- **An example** with a named person and real-looking numbers, labelled as an example.
- **Numbered options.** Each says what the human sees, what their users see, and the cost.
- **The recommendation:**
  - why it beats both the simpler option and the bigger one;
  - what would change your mind;
  - `firm` or `leaning`.

  If you ever change a recommendation, say so: "Changed from X to Y because Z".

**Cold-read test:** could someone who has never seen this project answer from the card alone?

## 3. When to ask, and who asks

- **Ask only while the human is actively talking to you.** If they are away, keep the card in `open/`, park only that item and keep working on everything else. If they say they are leaving, run `qq away`; any session will then hold its questions.
- **Owners ask their own cards**, at the end of their turn, after their other work is moving.
- **Anyone who asks another session's card** asks it word for word: never re-word it or change the recommendation. If you disagree, tell the owner instead.
- **Claim before you ask.** In Claude Code with the qq hooks, the gate claims the card for you. Everywhere else, run `qq claim <id>` first; if it fails, another session is asking it, so drop it.

## 4. Ask

**Before the question, in chat:** today, who meets it, the example and the recommendation, taken from the card.

**Then the question itself**, in your agent's question tool if it has one, or in chat:
- The text carries today and the problem (1–2 lines), the example in one line, then the question.
- Number every option (`1. Rebuild (Recommended)`, `2. Refuse`), with the recommended one first.
- Each option's description is 2–3 sentences: what happens, the example's numbers, and the trade-off. Never a bare "Yes" or "Skip it".
- **Always leave room for the human's own answer.** They may pick an option, pick one and add a condition, discuss it, or propose something else. End the question with: `Other: write your own, or e.g. "1, plus a note".`

**In Claude Code** (`AskUserQuestion`):
- Set `header` to `<card id> <word>`, 12 characters at most (e.g. `Q241307 Fees`).
- Up to 4 cards per box, on one topic.
- Never set an option `preview`: preview boxes drop the free-text "Other" row.
- Never add your own "Other" option; the tool adds one.
- The qq gate refuses a box that breaks these rules, or whose question is under 120 characters or an option description under 60. Read its reason, fix the box, and ask again.

## 5. After the answer

- **In Claude Code with the hooks,** the answer is written into the card automatically. An option pick closes it. A typed answer stays in `asking/` under your name until you act.
- **Elsewhere,** run `qq answer <id> "<the human's words, verbatim>"`.
- **When the answer is the human's own words** (typed text, or an option plus a note), they are talking to you:
  1. Read it literally. A note beats the option it came with.
  2. Answer any question they asked, first.
  3. Verify what they raised, in code or data. Never guess.
  4. If it settles the decision, apply it and close the card. Run `qq answer` if the hooks didn't record it.
  5. If not, update the card's Today, Options and Recommendation, and re-ask it, starting with: "You said: '…'. I checked: … So the question is now: …". Never re-ask the same options unchanged.
  6. After 2 rounds on one card, stop asking. Explain it fully in chat and wait for their reply.
- **If they dismiss the box or pick "clarify":** in Claude Code, their next message releases the card back to `open/`; elsewhere, run `qq release <id>`. Improve the card, then ask once more.
- **If the question became moot:** `qq withdraw <id> "<reason>"`. To ask an answered card again because facts changed: `qq reopen <id> "<what changed>"`.

## Commands

| Command | What it does |
|---|---|
| `qq new <slug> --title "…"` | create a card and print its path |
| `qq list` | cards, and when the human last typed |
| `qq claim <id>` | claim before asking (agents without the hooks) |
| `qq answer <id> "<text>"` | record the answer and close the card |
| `qq release <id>` | give a claim back |
| `qq reopen <id> "<why>"` | ask an answered card again |
| `qq withdraw <id> "<reason>"` | close a moot card |
| `qq away` / `qq back` | the human left / is back |
| `qq off` / `qq on` | turn qq's hooks off or on in this project |
| `qq setup` | Claude Code only: wire the hooks when qq came from a skill install rather than the plugin |
