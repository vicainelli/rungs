#!/usr/bin/env python3
"""Self-check for large-read.py: python3 hooks/large-read-check.py"""
import json, os, subprocess, sys, tempfile

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "large-read.py")


def run(stdin, **env):
    e = {**os.environ, **env}
    return subprocess.run([sys.executable, HOOK], input=stdin, text=True, env=e, capture_output=True).returncode


def call(tool, ti, **extra):
    return run(json.dumps({"tool_name": tool, "tool_input": ti, **extra}))


with tempfile.TemporaryDirectory() as d:
    big, small, binf = (os.path.join(d, n) for n in ("big", "small", "bin"))
    open(big, "w").write("x\n" * 400)
    open(small, "w").write("x\n" * 5)
    open(binf, "wb").write(b"\0\n" * 400)
    assert call("Read", {"file_path": big}) == 2
    assert call("Read", {"file_path": big, "limit": 10}) == 0
    assert call("Read", {"file_path": small}) == 0
    assert call("Read", {"file_path": big}, agent_id="a") == 0
    assert call("Read", {"file_path": binf}) == 0
    assert call("Bash", {"command": "cat big"}, cwd=d) == 2
    assert call("Bash", {"command": "cat big | grep x"}, cwd=d) == 0
    assert call("Bash", {"command": "head big"}, cwd=d) == 0
    assert run(json.dumps({"tool_name": "Read", "tool_input": {"file_path": big}}), RUNGS_MAX_LINES="1000") == 0
    assert run("garbage") == 0
print("ok")
