---
description: "qq, the question queue: /qq init | list | away | back | off | on | path | new <slug> --title \"…\""
argument-hint: "init | list | away | back | off | on | path | new <slug> --title \"…\""
allowed-tools: Bash(python3:*)
---

!`python3 "${CLAUDE_PLUGIN_ROOT}/skills/qq/scripts/qq.py" $ARGUMENTS`

Tell the human what that qq command did, in one or two plain lines. If it printed an error, say what to run instead.
