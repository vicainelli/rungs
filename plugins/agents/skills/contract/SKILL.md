---
name: contract
description: Shared handoff contract preloaded into the agents plugin's subagents. Not meant to be invoked by the user or loaded on its own.
user-invocable: false
---

# Contract

## Rules

- Stay on your rung. If the task needs a decision above it, do not guess; stop and hand off.
- You cannot start other agents. To involve one, end with a handoff naming it.
- Decisions that belong to the user (product intent, priority, security posture, personal data, money) go back as `STATUS: question`, `NEXT: user`, with the options and the cost of each.
- Never leave the tree half-applied silently. On escalation either finish to a consistent state or revert your own edits; say which in `STATE`.
- Never write "tests pass" or an equivalent without the command and its output in `VERIFIED`.
- Do not touch files outside the brief's scope. If you must, stop and hand off.
- Your final message ends with the handoff block and nothing after it.

## Handoff block

Exact format, always last:

```
STATUS: done | escalate | question | blocked
NEXT: none | operator | builder | specialist | researcher | reviewer | user
SUMMARY: <max 3 lines: what was asked, what happened>
CHANGED: <paths, one per line, or "none">
VERIFIED: <command -> key output line(s)>, or "not run: <reason>"
STATE: clean | partial: <what is half-applied and where>
OPEN: <blocker, or question with options and cost of each, or "none">
```

Pick one value for `STATUS`, `NEXT`, and `STATE`. Read-only agents always write `CHANGED: none` and `STATE: clean`.
