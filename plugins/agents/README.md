# agents

Five subagents tiered by how much judgment a task needs, not by job title. The main session decides, sequences, and talks to the user; subagents do the work and report back in one fixed handoff format. The `orchestrate` skill tells the main session whether to delegate and to whom. Claude Code is the primary target; Codex, opencode and Copilot CLI are supported through generated agent profiles.

## Rungs

| Agent | Use when | Claude pin | Codex pin | opencode pin | Copilot pin |
|-------|----------|------------|-----------|--------------|-------------|
| `operator` | Exact files and edits are named, nothing is left to decide, and the work is bulk or mechanical | haiku | gpt-6-luna / low | github-copilot/claude-haiku-4.5 | claude-haiku-4.5 / low |
| `builder` | The task fits an existing pattern, touches a bounded set of files, and the open choices are local | sonnet / medium | gpt-6-sol / medium | github-copilot/claude-sonnet-5.5#medium | claude-sonnet-5.5 / medium |
| `specialist` | No pattern exists, the change is cross-cutting, or a wrong call is expensive | opus / high | gpt-6.1-sol / high | github-copilot/claude-opus-5.5#high | claude-opus-5.5 / high |

## Services

| Agent | Use when | Claude pin | Codex pin | opencode pin | Copilot pin |
|-------|----------|------------|-----------|--------------|-------------|
| `researcher` | The caller needs facts before deciding (read-only) | sonnet / medium | gpt-6-sol / medium | github-copilot/claude-sonnet-5.5#medium | claude-sonnet-5.5 / medium |
| `reviewer` | The caller is about to commit to a plan, diff, or decision with real blast radius (read-only) | opus / high | gpt-6.1-sol / high | github-copilot/claude-opus-5.5#high | claude-opus-5.5 / high |

## How handoffs work

![flow](../../assets/flow.png)

Only the main session starts agents. An escalation is a request in the handoff, not a direct call: the main session reads it and starts the next rung.
Every agent ends with the same handoff block: `STATUS`, `NEXT`, `SUMMARY`, `CHANGED`, `VERIFIED`, `STATE`, `OPEN`.
An agent that needs another one says so in `NEXT`; the main session decides whether to start it.
Escalation climbs one rung at a time: `operator` hands up to `builder`, `builder` to `specialist`. Each rung may escalate once per task; a second escalation goes to the user.
Any agent that changed files reports the verification command and its output, not a claim.
Questions that belong to the user come back as `STATUS: question` and are passed on unanswered.

The format and the rules live in one file: [skills/contract/SKILL.md](skills/contract/SKILL.md).

## Install

### Claude Code

```
/plugin marketplace add vicainelli/rungs
/plugin install agents@rungs
```

### Codex

```sh
codex plugin marketplace add vicainelli/rungs
```

Enable the plugin in the Codex app's plugin list, or in `~/.codex/config.toml`:

```toml
[plugins."agents@rungs"]
enabled = true
```

Codex plugins cannot ship agent profiles, so install those from a checkout of this repo:

```sh
sh plugins/agents/scripts/install-codex.sh
```

This copies five files into `${CODEX_HOME:-~/.codex}/agents/`. An existing file that differs is backed up to `<name>.toml.bak` first. To remove the profiles:

```sh
cd "${CODEX_HOME:-$HOME/.codex}/agents" && rm operator.toml researcher.toml builder.toml specialist.toml reviewer.toml
```

### opencode

opencode has no plugin install for this, so install from a checkout of this repo:

```sh
sh plugins/agents/scripts/install-opencode.sh
```

This copies five agents into `${XDG_CONFIG_HOME:-~/.config}/opencode/agents/` and the `orchestrate` skill into `.../opencode/skills/orchestrate/`. An existing file that differs is backed up to `<file>.bak` first. It does not touch `AGENTS.md`; paste the Delegation block from "Codex routing" below into `~/.config/opencode/AGENTS.md` (the skill is named `orchestrate` there too). To remove everything:

```sh
cd "${XDG_CONFIG_HOME:-$HOME/.config}/opencode" && rm agents/{operator,researcher,builder,specialist,reviewer}.md && rm -r skills/orchestrate
```

### Copilot CLI

```sh
copilot plugin marketplace add vicainelli/rungs
copilot plugin install agents@rungs
```

`gh copilot` launches the same CLI. The plugin ships the agents, the `orchestrate` skill and a `sessionStart` hook that injects the delegation rule, so there is nothing to paste.

## Codex routing

Claude Code and Copilot CLI get the delegation rule from the plugin's session-start hook. On Codex, paste this into `~/.codex/AGENTS.md`; on opencode, into `~/.config/opencode/AGENTS.md`:

```markdown
## Delegation
The session orchestrates: it decides, sequences and talks to the user; subagents do the work.
Before any search, change, research, review, or external write, load the `orchestrate` skill;
it decides whether and to whom to delegate.
```

## Development

1. Edit `agents/*.md`, `skills/contract/SKILL.md` or `hooks/delegation.md`.
2. Run `python3 scripts/build.py`. Model pins live in `PINS` (Codex), `OPENCODE_PINS` (opencode) and `COPILOT_PINS` (Copilot CLI) at the top of that script. `python3 scripts/build.py --check` writes nothing and exits 1 if a generated file has drifted.
3. Commit the sources and the regenerated `codex/*.toml`, `opencode/agents/*.md` and `copilot/` together. Never edit the generated files by hand.

## Limits

- Read-only agents have no MCP access: their `tools` allowlist excludes everything not listed. Add specific read-only MCP tools to `tools:` if you need them.
- Claude model aliases (`haiku`, `sonnet`, `opus`) resolve to whatever Claude Code currently maps them to.
- Claude Code lets subagents start subagents by default. These agents cannot, because `Agent` is not in any `tools` list; adding it breaks the design.
- On Codex, read-only is the `read-only` sandbox mode, not a tool allowlist.
- The Codex profiles are generated and parsed but have not been run: no Codex CLI was available when this was built. Whether Codex subagents can start further subagents is not documented and was not tested.
- opencode has no SessionStart hook, so the delegation instruction lives in `AGENTS.md` and is not scoped to the primary agent. The generated agents therefore deny the `subagent` and `skill` actions.
- opencode has one `edit` permission, so Edit and Write are the same grant.
- The opencode pins need the GitHub Copilot provider connected in opencode; edit `OPENCODE_PINS` and rebuild to use another provider. The `#medium` / `#high` variant names have not been confirmed against a live run.
- Copilot CLI agents have no turn cap: `maxTurns` has no equivalent, so it is not emitted.
- An unknown model ID in `COPILOT_PINS` falls back silently to the session model.
