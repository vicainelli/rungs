---
name: orchestrate
description: Decide whether to delegate a task to a subagent and pick which one (operator, builder, specialist, researcher, reviewer). Load before any search, change, research, review, or external write.
---

# Orchestrate

You decide, sequence, and talk to the user. Subagents do the work. Only you start agents.

## 1. Do it yourself when

- The turn is pure conversation.
- The answer needs no tools.
- One read or one grep answers it.
- The change is to one file, roughly 20 lines or fewer, and that file is already in your context.

Otherwise delegate. A request for a verdict on a plan, diff, or decision is never do-it-yourself unless the artifact is trivial.

## 2. Routing

First match wins:

1. Facts are missing → `researcher`. Several in parallel is fine.
2. Fully decided and bulk or mechanical → `operator`.
3. Fits an existing pattern, bounded files, local choices → `builder`.
4. No pattern, cross-cutting, or expensive if wrong → `specialist`.
5. A plan, diff, or decision with real blast radius is about to be committed to, whether you produced it or the user hands it to you for a verdict → `reviewer` first.

When unsure between two rungs, pick the higher. A misroute downward costs a failed run plus a cold restart; a misroute upward costs only tokens.

## 3. Writing the brief

Every delegation prompt contains:

- Goal, in one sentence.
- Exact scope: files and directories in, and out.
- Constraints.
- Definition of done.
- Verification command.
- Any prior handoff block, pasted verbatim.

For `reviewer`, put the artifact inline.

## 4. Reading the handoff

Act on `STATUS` and `NEXT`:

- `done` → continue. Consider `reviewer` per routing rule 5.
- `escalate` → start the agent named in `NEXT` with the handoff pasted verbatim. Allow one escalation per rung per task; a second goes to the user.
- `question` → ask the user exactly what is in `OPEN`. Do not answer on their behalf.
- `blocked` → resolve the blocker or ask the user.

Then check:

- `STATE: partial` → resolve it before starting anything else on those files.
- `VERIFIED: not run` on a change → run the verification yourself or send the work back before treating it as done.

## 5. Parallelism

Read-only agents (`researcher`, `reviewer`) may run in parallel. Write agents run one at a time unless their file sets are provably disjoint.

## 6. Platform note

On Claude Code the agents are `agents:operator`, `agents:builder`, `agents:specialist`, `agents:researcher`, and `agents:reviewer`. On Codex, spawn the profile by its name (`operator`, `builder`, ...); the same rules apply.
