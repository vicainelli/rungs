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
- The change is to one file that is already in your context, and it is roughly 20 lines or fewer or text you have already written in full.

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
- Exact scope: files and directories in, and out. Paste facts you already hold (names, rows, values) instead of pointing at the file, and name large files the agent must not read. "Optionally" or "if helpful" is not scope.
- Constraints.
- Definition of done.
- Verification command.
- Any prior handoff block, pasted verbatim.

For `reviewer`, put the artifact inline.

Name only tools the target agent has. `researcher` has read, grep, glob, web fetch, and web search; `reviewer` has read, grep, and glob. Neither can edit, run shell commands, or call MCP tools, and no subagent can load skills: paste the rules it needs instead. If a step needs a tool the agent lacks, do that step yourself or give it to `operator` with the exact command.

## 4. Reading the handoff

Act on `STATUS` and `NEXT`:

- `done` → continue. Consider `reviewer` per routing rule 5.
- `escalate` → start the agent named in `NEXT` with the handoff pasted verbatim. Allow one escalation per rung per task; a second goes to the user.
- `question` → ask the user exactly what is in `OPEN`. Do not answer on their behalf.
- `blocked` → resolve the blocker or ask the user.
- No handoff because the run failed (model unavailable, usage limit) → nothing changed. Do not resume or retry that agent. Tell the user which agent and model failed, then do the work yourself if it fits §1, or rerun it on another agent; if that agent is not a rungs agent, paste the contract's handoff block format into its brief.

A named `NEXT` is a suggestion: if the remaining work fits §1, do it yourself.

Then check:

- `STATE: partial` → resolve it before starting anything else on those files.
- `VERIFIED: not run` on a change → run the verification yourself or send the work back before treating it as done.
- Otherwise trust `VERIFIED`. Re-check a claim yourself only when it decides the outcome (a score near a threshold, a pass/fail), with one cheap check. Do not redo the agent's research.

## 5. Parallelism

Read-only agents (`researcher`, `reviewer`) may run in parallel. Write agents run one at a time unless their file sets are provably disjoint.

## 6. Platform note

On Claude Code the agents are `rungs:operator`, `rungs:builder`, `rungs:specialist`, `rungs:researcher`, and `rungs:reviewer`. On Codex, spawn the profile by its name (`operator`, `builder`, ...); the same rules apply. On opencode, spawn the agent by its bare name with the `subagent` tool; the same rules apply. On Copilot CLI, the agents carry the same `rungs:` names; spawn them with the `task` tool.
