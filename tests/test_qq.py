#!/usr/bin/env python3
"""End-to-end tests for qq.py: every hook mode and every CLI command, fully isolated.

Each run uses a temp project, a temp HOME and temp session records, so it never touches
your real .qq folders, Claude Code settings or sessions. Run: python3 tests/test_qq.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
QQ = os.path.join(HERE, "..", "plugins", "qq", "skills", "qq", "scripts", "qq.py")

T = tempfile.mkdtemp(prefix="qq-test-")
PROJ = os.path.join(T, "proj")
HOME = os.path.join(T, "home")
SESS = os.path.join(T, "sessions")
for d in (PROJ, HOME, SESS):
    os.makedirs(d)
Q = os.path.join(PROJ, ".qq")
ST = os.path.join(Q, ".state")
TP = os.path.join(T, "session.jsonl")
open(TP, "w").close()
ENV = dict(os.environ, CLAUDE_PROJECT_DIR=PROJ, HOME=HOME, QQ_SESSIONS_DIR=SESS, QQ_CONFIRM_DELAYS="1,1,1,1")
json.dump({"sessionId": "LIVE", "pid": os.getpid(), "name": "live-lead"}, open(os.path.join(SESS, f"{os.getpid()}.json"), "w"))
json.dump({"sessionId": "DEAD", "pid": 999999, "name": "dead-lead"}, open(os.path.join(SESS, "999999.json"), "w"))

L = "The site check rebuilds the whole site every run, about 157 s. Keeping the build cache saves about $2-3 a month. Add it?"
D = "Each run drops from about 157 s to about 90 s; about 400 runs a month saves $2-3 with the free cache."
res = [0, 0]


def check(name, cond):
    res[0 if cond else 1] += 1
    print(("PASS " if cond else "FAIL ") + name)


def hook(mode, **d):
    d.setdefault("transcript_path", TP)
    d.setdefault("cwd", PROJ)
    return subprocess.run([sys.executable, QQ, "hook", mode], input=json.dumps(d), capture_output=True,
                          text=True, env=ENV).stdout


def cli(*args):
    return subprocess.run([sys.executable, QQ, *args], capture_output=True, text=True, env=ENV, cwd=PROJ)


def card(i, folder="open", extra="", filed="24-11-2026 00:00"):
    os.makedirs(os.path.join(Q, folder), exist_ok=True)
    with open(os.path.join(Q, folder, f"{i}-t.md"), "w") as fh:
        fh.write(f"# {i} · test card\n- Owner: owner-x (test)\n- Filed: {filed}\n{extra}")


def box(i, q=L, desc=D, preview=None, ids=None):
    qs = []
    for n, cid in enumerate(ids or [i]):
        o1 = dict(label="1. Add (Recommended)", description=desc)
        if preview:
            o1["preview"] = preview
        qs.append(dict(question=q if n == 0 else f"{q} {cid}", header=f"{cid} T", multiSelect=False,
                       options=[o1, dict(label="2. Skip", description=D)]))
    return dict(questions=qs)


def denied(out):
    return '"deny"' in out


def present(ago=0):
    os.makedirs(ST, exist_ok=True)
    with open(os.path.join(ST, "last-human"), "w") as fh:
        fh.write(f"{time.time() - ago}\n")


def ls(f):
    p = os.path.join(Q, f)
    return sorted(os.listdir(p)) if os.path.isdir(p) else []


def where(name):
    for f in ("open", "asking", "closed"):
        if name in ls(f):
            return f
    return None


def rm(*names):
    for n in names:
        f = where(n)
        if f:
            os.remove(os.path.join(Q, f, n))


def mv(name, dst):
    f = where(name)
    if f:
        shutil.move(os.path.join(Q, f, name), os.path.join(Q, dst, name))


def age(path, secs):
    t = time.time() - secs
    os.utime(path, (t, t))


def clear_told():
    if os.path.isdir(ST):
        for f in os.listdir(ST):
            if f.startswith("told-"):
                os.remove(os.path.join(ST, f))


def ent(source, text, ago=0):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() - ago))
    with open(TP, "a") as fh:
        fh.write(json.dumps({"type": "user", "promptSource": source, "timestamp": ts, "message": {"content": text}}) + "\n")


def last_human():
    return open(os.path.join(ST, "last-human")).read()


def body(name):
    return open(os.path.join(Q, where(name), name)).read()


try:
    # --- gate: presence, claim, races ---
    card("Q900001")
    check("away (no presence) -> deny", denied(hook("pre", session_id="LIVE", tool_input=box("Q900001"))))
    present()
    check("present -> allow and claim", not denied(hook("pre", session_id="LIVE", tool_input=box("Q900001"))) and where("Q900001-t.md") == "asking")
    check("other session, same card -> deny", denied(hook("pre", session_id="B", tool_input=box("Q900001"))))
    check("own re-ask -> allow", not denied(hook("pre", session_id="LIVE", tool_input=box("Q900001"))))

    # --- post ---
    hook("post", session_id="LIVE", tool_input=box("Q900001"), tool_response={"questions": [], "answers": {L: "1. Add (Recommended)"}, "annotations": {}})
    check("option answer -> closed", where("Q900001-t.md") == "closed")
    check("closed re-ask -> deny", denied(hook("pre", session_id="LIVE", tool_input=box("Q900001"))))
    card("Q900002"); hook("pre", session_id="LIVE", tool_input=box("Q900002"))
    hook("post", session_id="LIVE", tool_input=box("Q900002"), tool_response={"questions": [], "answers": {L: "1, but also check fees"}, "annotations": {}})
    check("typed answer -> stays in asking", where("Q900002-t.md") == "asking")
    check("owner sees TYPED ANSWER WAITING", "YOURS, TYPED ANSWER WAITING" in hook("prompt", session_id="LIVE", prompt="hello"))
    mv("Q900002-t.md", "closed")
    card("Q900003"); hook("pre", session_id="LIVE", tool_input=box("Q900003"))
    hook("post", session_id="LIVE", tool_input=box("Q900003"), tool_response={"questions": [], "answers": {L: "1. Add (Recommended)"}, "annotations": {L: {"notes": "but check fees"}}})
    check("option + notes -> stays open with the notes", where("Q900003-t.md") == "asking" and "Notes from the human: but check fees" in body("Q900003-t.md"))
    rm("Q900003-t.md")
    card("Q900004", "asking", "- Asker-session: DEAD\n## Answer (free text: x; recorded x)\nhi\n")
    check("typed answer, asker ended -> ASKER ENDED line", "TYPED ANSWER, ASKER ENDED" in hook("prompt", session_id="C", prompt="hello"))
    rm("Q900004-t.md")
    card("Q900005", "asking", "- Asker-session: LIVE\n## Answer (free text: x; recorded x)\nhi\n")
    check("only a live session's typed-answer card -> silent for others", hook("prompt", session_id="C", prompt="hello").strip() == "")
    rm("Q900005-t.md")

    # --- quality floor ---
    card("Q900006")
    check("preview -> deny", denied(hook("pre", session_id="LIVE", tool_input=box("Q900006", preview="a preview"))))
    check("thin question -> deny", denied(hook("pre", session_id="LIVE", tool_input=box("Q900006", q="Add cache?"))))
    check("hint line not counted -> deny", denied(hook("pre", session_id="LIVE", tool_input=box("Q900006", q='The site check rebuilds each run, about 157 s. Add the cache? Other: write your own, or e.g. "1, plus a note".'))))
    check("thin option description -> deny", denied(hook("pre", session_id="LIVE", tool_input=box("Q900006", desc="Faster."))))
    check("denied boxes claim nothing", where("Q900006-t.md") == "open")
    check("no card id -> deny", denied(hook("pre", session_id="LIVE", tool_input=dict(questions=[dict(question=L, header="Fees", options=[dict(label="1", description=D)])]))))

    # --- partial deny ---
    card("Q900007"); card("Q900008", "asking", "- Asker-session: B\n")
    check("partial box -> deny", denied(hook("pre", session_id="LIVE", tool_input=box("Q900007", ids=["Q900007", "Q900008"]))))
    check("partial deny keeps my claim on A", where("Q900007-t.md") == "asking")
    hook("prompt", session_id="LIVE", prompt="let me re-ask")
    check("next typed prompt releases A", where("Q900007-t.md") == "open")
    rm("Q900007-t.md", "Q900008-t.md")

    # --- releases ---
    hook("pre", session_id="LIVE", tool_input=box("Q900006"))
    hook("prompt", session_id="LIVE", prompt="I want to clarify this")
    check("clarify leftover released on typed prompt", where("Q900006-t.md") == "open" and "Released:" in body("Q900006-t.md"))
    rm("Q900006-t.md")
    card("Q900009", "open", "- Asker-session: LIVE\n## Answer (verbatim; recorded x)\n1. Add (Recommended)\n- Released: x (re-opened)\n")
    hook("pre", session_id="LIVE", tool_input=box("Q900009"))
    hook("prompt", session_id="LIVE", prompt="let me clarify")
    check("re-opened card (old answer) released after clarify", where("Q900009-t.md") == "open")
    hook("pre", session_id="LIVE", tool_input=box("Q900009")); hook("fail", session_id="LIVE", tool_input=box("Q900009"))
    check("re-opened card (old answer) released after a failed box", where("Q900009-t.md") == "open")
    rm("Q900009-t.md")
    card("Q900010", "asking", "- Asker-session: DEAD\n"); age(os.path.join(Q, "asking", "Q900010-t.md"), 31 * 60)
    card("Q900011", "asking", "- Asker-session: LIVE\n"); age(os.path.join(Q, "asking", "Q900011-t.md"), 31 * 60)
    card("Q900016", "asking", "- Asker-session: UNKNOWN\n"); age(os.path.join(Q, "asking", "Q900016-t.md"), 31 * 60)
    hook("prompt", session_id="C", prompt="Another Claude session sent a message: x")
    check("dead asker, 31 min -> auto-released", where("Q900010-t.md") == "open")
    check("live asker, 31 min -> kept", where("Q900011-t.md") == "asking")
    check("unknown asker, 31 min -> kept (until 2 h)", where("Q900016-t.md") == "asking")
    age(os.path.join(Q, "asking", "Q900016-t.md"), 2 * 3600 + 60)
    hook("prompt", session_id="C2", prompt="Another Claude session sent a message: y")
    check("unknown asker, 2 h -> auto-released", where("Q900016-t.md") == "open")
    rm("Q900010-t.md", "Q900011-t.md", "Q900016-t.md")

    # --- orphans ---
    present()
    with open(os.path.join(ST, "back-since"), "w") as fh:
        fh.write(f"{time.time() - 11 * 60}\n")
    card("Q900012", filed="23-11-2026 00:00"); card("Q900013", extra="- Released: x (clarify)\n", filed="23-11-2026 00:00")
    out = hook("prompt", session_id="DESK", prompt="hello")
    desk = out.split("unclaimed cards")[-1] if "unclaimed cards" in out else ""
    check("orphan listed for the desk", "Q900012" in desk)
    check("just-released card held back", "Q900013" not in desk)
    age(os.path.join(Q, "open", "Q900013-t.md"), 31 * 60)
    out = hook("prompt", session_id="DESK", prompt="hello again")
    check("released card listed after 31 min", "Q900013" in (out.split("unclaimed cards")[-1] if "unclaimed cards" in out else ""))
    check("typed-looking prompt -> conditional IF wording", "IF the human typed this message" in out)
    clear_told()
    check('peer prompt -> "in some session"', "in some session" in hook("prompt", session_id="E", prompt="Another Claude session sent a message: hi"))
    rm("Q900012-t.md", "Q900013-t.md")

    # --- fail, away, opt-out, garbage ---
    card("Q900014"); hook("pre", session_id="LIVE", tool_input=box("Q900014")); hook("fail", session_id="LIVE", tool_input=box("Q900014"))
    check("failed box released", where("Q900014-t.md") == "open")
    time.sleep(0.05); cli("away")
    check("qq away -> deny", denied(hook("pre", session_id="LIVE", tool_input=box("Q900014"))))
    cli("back")
    check("qq back -> allow", not denied(hook("pre", session_id="LIVE", tool_input=box("Q900014"))))
    mv("Q900014-t.md", "open")
    cli("off")
    check("qq off -> hooks silent", hook("pre", session_id="LIVE", tool_input=dict(questions=[dict(question="x", header="Fees")])) == "")
    cli("on")
    r = subprocess.run([sys.executable, QQ, "hook", "pre"], input="garbage", capture_output=True, text=True, env=ENV)
    check("garbage stdin -> exit 0, silent", r.returncode == 0 and r.stdout == "")

    # --- presence from the asking session's own transcript ---
    present(ago=7200); ent("typed", "please continue", ago=300)
    check("stale presence + own typed entry 5 min ago -> allow", not denied(hook("pre", session_id="LIVE", tool_input=box("Q900014"))))
    rm("Q900014-t.md")

    # --- likely-away cron prompt ---
    card("Q900015"); present(ago=7200); clear_told()
    o1 = hook("prompt", session_id="N", prompt="Lead orchestrator hourly auto-continue")
    o2 = hook("prompt", session_id="N", prompt="Lead orchestrator hourly auto-continue")
    check("likely-away cron prompt -> one short line naming OWN cards", o1.strip().count("\n") == 0 and "your OWN" in o1)
    check("second cron prompt within 10 min -> silent", o2.strip() == "")
    rm("Q900015-t.md")

    # --- confirm (delays 1 s in tests) ---
    with open(os.path.join(ST, "last-human"), "w") as fh:
        fh.write("100\n")
    hook("prompt", session_id="LIVE", prompt="HOURLY USAGE CHECK: check")
    time.sleep(0.5); ent("system", "HOURLY USAGE CHECK: check"); time.sleep(2.5)
    check("scheduled prompt does not set presence", last_human().startswith("100"))
    hook("prompt", session_id="LIVE", prompt="yes")
    time.sleep(0.5); ent("typed", "yes"); time.sleep(2.5)
    check('typed "yes" sets presence', not last_human().startswith("100"))
    with open(os.path.join(ST, "last-human"), "w") as fh:
        fh.write("100\n")
    hook("prompt", session_id="LIVE", prompt="a typed message that never reaches the transcript")
    time.sleep(5.5)
    check("prompt never written -> presence unchanged", last_human().startswith("100"))
    old = TP + ".old"; shutil.move(TP, old)
    with open(TP, "w") as fh:
        fh.write(json.dumps({"type": "user", "message": {"content": "an older format"}}) + "\n")
    hook("prompt", session_id="LIVE", prompt="new format prompt")
    time.sleep(2.5)
    check("transcript without promptSource -> fail open (presence set)", not last_human().startswith("100"))
    shutil.move(old, TP)

    # --- CLI ---
    out = cli("new", "Fee Split!", "--title", "How should fees be split?", "--owner", "tester").stdout.strip()
    cid = os.path.basename(out)[:7]
    check("qq new creates a card from the template", out.endswith(".md") and "## Today, step by step" in open(out).read())
    check("qq new never reuses an id", os.path.basename(cli("new", "second").stdout.strip())[:7] != cid)
    check(".qq/.gitignore keeps cards out of git", open(os.path.join(Q, ".gitignore")).read().strip().endswith("*"))
    check("qq claim moves to asking", cli("claim", cid, "--as", "codex").returncode == 0 and where(os.path.basename(out)) == "asking")
    check("second qq claim fails", cli("claim", cid).returncode != 0)
    check("qq release gives it back", cli("release", cid).returncode == 0 and where(os.path.basename(out)) == "open")
    check("qq answer records and closes", cli("answer", cid, "Option 2, and log it").returncode == 0 and where(os.path.basename(out)) == "closed" and "Option 2, and log it" in body(os.path.basename(out)))
    check("qq reopen moves back with a hold", cli("reopen", cid, "prices changed").returncode == 0 and "Released:" in body(os.path.basename(out)))
    check("qq withdraw closes with a reason", cli("withdraw", cid, "moot").returncode == 0 and "Withdrawn:" in body(os.path.basename(out)))
    check("qq list runs", "open/" in cli("list").stdout)

    # --- setup ---
    settings = os.path.join(HOME, ".claude", "settings.json")
    os.makedirs(os.path.dirname(settings))
    with open(settings, "w") as fh:
        json.dump({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "other-guard"}]}]}, "theme": "dark"}, fh)
    cli("setup"); cli("setup")
    s = json.load(open(settings))
    qq_groups = sum(1 for ev in s["hooks"].values() for g in ev if "qq.py" in json.dumps(g))
    check("qq setup wires 4 hooks, idempotent", qq_groups == 4)
    check("qq setup keeps other hooks and settings", "other-guard" in json.dumps(s) and s.get("theme") == "dark")
    check("qq setup backs up settings", any(n.startswith("settings.json.qq-backup-") for n in os.listdir(os.path.dirname(settings))))
    cli("setup", "--remove")
    s = json.load(open(settings))
    check("qq setup --remove takes only qq's hooks out", "qq.py" not in json.dumps(s) and "other-guard" in json.dumps(s))
    os.makedirs(os.path.join(HOME, ".claude", "plugins"))
    with open(os.path.join(HOME, ".claude", "plugins", "installed_plugins.json"), "w") as fh:
        json.dump({"version": 2, "plugins": {"qq@qq": [{"scope": "user"}]}}, fh)
    r = cli("setup")
    check("qq setup refuses when the plugin is installed", r.returncode != 0 and "qq.py" not in open(settings).read())
finally:
    shutil.rmtree(T, ignore_errors=True)

print(f"\n{res[0]} passed, {res[1]} failed")
sys.exit(1 if res[1] else 0)
