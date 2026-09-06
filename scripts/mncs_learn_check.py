#!/usr/bin/env python3
"""Produce an mncs.check-result/1 document for the mncs-learn foundation.

The check intentionally validates bootstrap invariants only. As native
mncs-language coverage grows, this script should delegate more of the proof to
native MNCS programs rather than expanding into a permanent Python validator.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

RESULT_SCHEMA = "mncs.check-result/1"
CHECK_ID = "learn-contract-tests"
PROVIDER = "mncs-learn-bootstrap"


def run(repo: Path) -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "src") + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    if completed.returncode != 0:
        tail = (completed.stdout + completed.stderr)[-1200:].strip()
        return False, f"unittest failed: {tail or 'no output'}"

    required_json = [
        repo / "mncs-boundary.json",
        repo / "spec" / "mncs-learn-v0.schema.json",
        repo / "examples" / "fox-learning-cycle.json",
    ]
    for path in required_json:
        try:
            json.loads(path.read_text())
        except Exception as exc:  # pragma: no cover - defensive evidence path
            return False, f"invalid JSON {path.relative_to(repo)}: {exc}"

    boundary = json.loads((repo / "mncs-boundary.json").read_text())
    expected_scopes = {"internal", "relationship", "topology", "routing"}
    if set(boundary.get("mutation_scopes", [])) != expected_scopes:
        return False, "boundary mutation scopes do not match the four-scope learning model"

    expected_invariants = {
        "no universal train method is required",
        "observations do not directly mutate durable target state",
        "rights can prohibit learning independently of observation visibility",
        "topology and routing changes use the governed learning lifecycle",
    }
    if not expected_invariants <= set(boundary.get("invariants", [])):
        return False, "boundary is missing required machine-native learning invariants"

    return True, "bootstrap contracts, lifecycle tests, rights gating, and four-scope boundary pass"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-file", required=True)
    parser.add_argument("--revision", default="working-tree")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    passed, summary = run(repo)
    result = {
        "schema_version": RESULT_SCHEMA,
        "id": CHECK_ID,
        "provider": PROVIDER,
        "verdict": "PASS" if passed else "FAIL",
        "summary": summary,
        "subject": {"repository": "mncs-learn", "revision": args.revision},
    }

    destination = Path(args.result_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"id": CHECK_ID, "verdict": result["verdict"], "summary": summary}))

    # The mncs-actions boundary consumes the verdict as data. Always emit the
    # result file successfully when the checker itself ran.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
