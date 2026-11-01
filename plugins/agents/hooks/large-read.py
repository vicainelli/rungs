#!/usr/bin/env python3
"""PreToolUse hook: block full reads of large files in the main session."""
import json, os, re, shlex, sys


def big(path, limit):
    """Line count if path is a large text file, else 0."""
    if not os.path.isfile(path):
        return 0
    with open(path, "rb") as f:
        if b"\0" in f.read(8192):
            return 0
        f.seek(0)
        n = sum(1 for _ in f)
    return n if n > limit else 0


def paths(data):
    ti = data["tool_input"]
    if data["tool_name"] == "Read":
        return [] if ti.get("offset") or ti.get("limit") else [ti["file_path"]]
    cmd = ti["command"]
    # ponytail: only simple cat/less/more are caught (sed -n, awk, compound commands
    # slip through); a real shell parser is the upgrade path.
    if re.search(r"[|><;&`]|\$\(", cmd):
        return []
    try:
        argv = shlex.split(cmd)
    except ValueError:
        return []
    if not argv or os.path.basename(argv[0]) not in ("cat", "less", "more"):
        return []
    return [os.path.join(data.get("cwd") or "", a) for a in argv[1:] if not a.startswith("-")]


def main():
    try:
        data = json.load(sys.stdin)
        if "agent_id" in data:
            return 0
        try:
            limit = int(os.environ.get("RUNGS_MAX_LINES", 350))
        except ValueError:
            limit = 350
        for p in paths(data):
            n = big(p, limit)
            if n:
                print(f"rungs: {p} has {n} lines (limit {limit}). Ask rungs:researcher the question instead of reading the whole file, or Read with offset/limit for the section you need to edit.", file=sys.stderr)
                return 2
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
