"""Census: does any tracked registry row hold a `params` value that is not JSON-native?

Run from the repository root:  python docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/params_census.py

It observes values instead of matching text:
  0. a control: each value the validator must refuse, loaded from YAML text, is
     checked first and must come out NOT-JSON (else the script exits 2);
  1. every tracked .yml/.yaml file is loaded with yaml.safe_load; every row of a
     registry (a top-level list of rows) that has `params` is checked;
  2. every tracked test .py file is parsed; every string constant containing
     "params:" that loads as a registry is checked the same way, every dict literal
     with a "params" key has that value evaluated (ast.literal_eval) and checked,
     and a "params:" in an f-string, in a string fragment that does not load as a
     registry, or in a value literal_eval cannot evaluate is listed as NOT-STATIC,
     never counted as JSON-native: those registries are built at run time.

The check is the proposed validator's: json.loads(json.dumps(v, allow_nan=False)) == v,
with TypeError / ValueError / RecursionError counting as not JSON-native.
One line per checked value; the last line is the verdict.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys

import yaml


def json_native(v) -> bool:
    try:
        return json.loads(json.dumps(v, allow_nan=False)) == v
    except (TypeError, ValueError, RecursionError):
        return False


def tracked(*patterns: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", "--", *patterns], capture_output=True,
                         text=True, encoding="utf-8", check=True).stdout
    return [p for p in out.splitlines() if p]


rows: list[tuple[str, str, str]] = []  # (where, row id, verdict)

CONTROLS = ["k: !!set {a: null}", "k: 2026-11-11", "k: !!binary aGk=", "k: {1: a}",
            "k: {yes: a}", "k: .nan", "k: .inf"]
for text in CONTROLS:
    verdict = "NOT-JSON" if not json_native(yaml.safe_load(text)) else "ok"
    print(f"control {verdict:9} {text}")
    if verdict != "NOT-JSON":
        sys.exit(2)


def check_registry(where: str, doc) -> bool:
    """A registry is a top-level list of rows (or a mapping holding one under `mandates`)."""
    if isinstance(doc, dict) and isinstance(doc.get("mandates"), list):
        doc = doc["mandates"]
    if not isinstance(doc, list):
        return False
    for row in doc:
        if isinstance(row, dict) and "params" in row:
            rows.append((where, str(row.get("id")), "ok" if json_native(row["params"]) else "NOT-JSON"))
    return True


for path in tracked("*.yml", "*.yaml"):
    with open(path, encoding="utf-8") as fh:
        try:
            docs = list(yaml.safe_load_all(fh))
        except yaml.YAMLError:
            continue
    for doc in docs:
        check_registry(path, doc)

for path in tracked("plugins/arch-compliance/tests/*.py", "tests/*.py"):
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr) and any(
                isinstance(c, ast.Constant) and "params:" in str(c.value) for c in node.values):
            rows.append((f"{path}:{node.lineno}", "-", "NOT-STATIC"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and "params:" in node.value:
            where = f"{path}:{node.lineno}"
            try:
                parsed = check_registry(where, yaml.safe_load(node.value))
            except yaml.YAMLError:
                parsed = False
            if not parsed:
                rows.append((where, "-", "NOT-STATIC"))
        elif isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == "params":
                    try:
                        val = ast.literal_eval(v)
                    except (ValueError, SyntaxError, TypeError):
                        rows.append((f"{path}:{v.lineno}", "-", "NOT-STATIC"))
                        continue
                    rows.append((f"{path}:{v.lineno}", "-", "ok" if json_native(val) else "NOT-JSON"))

for where, rid, verdict in rows:
    print(f"{verdict:16} {where}  {rid}")
bad = [r for r in rows if r[2] == "NOT-JSON"]
print(f"checked {len(rows)} params values; NOT-JSON: {len(bad)}")
sys.exit(1 if bad else 0)
