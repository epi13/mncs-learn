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


def find_mncs() -> str | None:
    for candidate in (
        os.environ.get("MNCS_BIN"),
        os.environ.get("MNCS_BINARY"),
    ):
        if candidate and Path(candidate).is_file():
            return candidate
    root = os.environ.get("MNCS_LANGUAGE_ROOT")
    if root:
        candidate = Path(root) / "target" / "debug" / "mncs"
        if candidate.is_file():
            return str(candidate)
    return None


def native_suites(mncs: str, repo: Path, workspace: Path) -> tuple[bool, str]:
    """Delegate proof to the native MNCS suites (contract over Python)."""
    libraries = [str(repo / "native")]
    language_root = os.environ.get("MNCS_LANGUAGE_ROOT")
    if language_root:
        libraries.append(str(Path(language_root) / "library"))
    test_native = os.environ.get("MNCS_TEST_NATIVE")
    if test_native:
        libraries.append(test_native)
    for owner, sub in (("mncs-data", "src"), ("mncs-math", "src")):
        candidate = workspace / owner / sub
        if candidate.is_dir():
            libraries.append(str(candidate))
    passed, total = 0, 0
    for module in ("codes", "contract", "centroid"):
        command = [mncs, "test", str(repo / "native" / "mncs" / "learn" /
                                     f"{module}.mncs"),
                   "--format", "json"]
        for library in libraries:
            command += ["--library", library]
        try:
            completed = subprocess.run(command, capture_output=True,
                                       text=True, check=False, timeout=300)
            document = json.loads(completed.stdout)
        except Exception as exc:
            return False, f"native {module}: runner error {exc}"
        if document.get("classification") != "passed":
            return False, (f"native {module}: "
                           f"{document.get('classification')}")
        total += 1
        passed += 1
    return True, f"native suites pass ({passed}/{total})"


def run(repo: Path) -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo / "oracle") + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
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

    summary = ("bootstrap contracts, lifecycle tests, rights gating, "
               "and four-scope boundary pass")
    mncs = find_mncs()
    if mncs is None:
        return True, summary + "; native suites not exercised (no toolchain)"
    native_ok, native_note = native_suites(mncs, repo, repo.parent)
    if not native_ok:
        return False, f"{summary}; {native_note}"
    return True, f"{summary}; {native_note}"


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
