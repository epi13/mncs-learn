"""mncs-learn CLI: train, predict, evaluate, show learned artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from learn import codes, engine, model, native, store


def _mncs(args: argparse.Namespace) -> str:
    found = native.find_mncs(getattr(args, "mncs", None))
    if not found:
        print("mncs-learn: set MNCS_BIN or MNCS_LANGUAGE_ROOT",
              file=sys.stderr)
        raise SystemExit(2)
    return found


def _load_dataset(path: str) -> tuple[dict[str, Any], str]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"mncs-learn: cannot read {path}: {error}", file=sys.stderr)
        raise SystemExit(2)
    try:
        clean = model.validate_dataset(document)
    except model.DatasetError as error:
        print(f"mncs-learn: invalid dataset: {error}", file=sys.stderr)
        raise SystemExit(2)
    return clean, model.dataset_digest(clean)


def cmd_train(args: argparse.Namespace) -> int:
    mncs = _mncs(args)
    dataset, digest = _load_dataset(args.file)
    ndim = args.ndim or len(dataset["feature_names"])
    try:
        state, report = engine.train(mncs=mncs, dataset=dataset, ndim=ndim)
    except native.NativeError as error:
        print(f"mncs-learn: train refused: {error}", file=sys.stderr)
        return 1
    artifact = model.build_artifact(name=args.name, dataset=dataset,
                                    digest=digest, ndim=ndim, state=state,
                                    train_report=report)
    if args.evaluate:
        held_path = getattr(args, "held_out", None)
        if held_path:
            held, _ = _load_dataset(held_path)
        else:
            _, held = model.split_holdout(dataset)
        try:
            eval_report = engine.evaluate(mncs=mncs, dataset=held,
                                          state=state)
        except native.NativeError as error:
            print(f"mncs-learn: evaluate refused: {error}", file=sys.stderr)
            return 1
        acc = engine.accuracy(eval_report)
        base = engine.baseline_accuracy(eval_report)
        decision = engine.decide(mncs=mncs, before_pm=base, after_pm=acc)
        artifact["metrics"] = {
            "held_out_rows": eval_report["total"],
            "held_out_skipped": eval_report["skipped"],
            "accuracy_pm": acc,
            "majority_baseline_pm": base,
            "majority_label": eval_report["majority_label"],
            "confusion": eval_report["confusion"],
            "decision": codes.DECISIONS[decision["decision"]],
            "decision_reason":
                codes.REASONS[decision["reason"]],
            "dataset_digest_held_out": model.dataset_digest(held)}
    path = engine.save_artifact(state_dir=args.state_dir, artifact=artifact)
    print(json.dumps({"artifact": str(path), "name": artifact["name"],
                      "revision": artifact["revision"],
                      "classes": len(artifact["classes"]),
                      "rows_used": artifact["train"]["rows_used"],
                      "metrics": artifact["metrics"]}, indent=2))
    return 0


def cmd_predict(args: argparse.Namespace) -> int:
    mncs = _mncs(args)
    try:
        artifact = store.read_json(Path(args.artifact))
        features = [int(value) for value in args.features.split(",")]
        report = engine.predict(mncs=mncs, state=artifact["state"],
                                features=features)
    except (OSError, ValueError, KeyError) as error:
        print(f"mncs-learn: bad input: {error}", file=sys.stderr)
        return 2
    except native.NativeError as error:
        print(f"mncs-learn: predict refused: {error}", file=sys.stderr)
        return 1
    label = report["label"]
    names = artifact.get("label_names", {})
    print(json.dumps({"label": label,
                      "label_name": names.get(str(label)),
                      "dist2": report["dist2"]}, indent=2))
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    mncs = _mncs(args)
    try:
        artifact = store.read_json(Path(args.artifact))
    except (OSError, ValueError) as error:
        print(f"mncs-learn: cannot read {args.artifact}: {error}",
              file=sys.stderr)
        return 2
    dataset, digest = _load_dataset(args.file)
    try:
        eval_report = engine.evaluate(mncs=mncs, dataset=dataset,
                                      state=artifact["state"])
    except native.NativeError as error:
        print(f"mncs-learn: evaluate refused: {error}", file=sys.stderr)
        return 1
    acc = engine.accuracy(eval_report)
    base = engine.baseline_accuracy(eval_report)
    decision = engine.decide(mncs=mncs, before_pm=base, after_pm=acc)
    evaluation = {"schema_version": codes.EVALUATION_SCHEMA,
                  "artifact": artifact["name"],
                  "artifact_revision": artifact["revision"],
                  "algorithm": artifact["algorithm"],
                  "dataset_digest": digest,
                  "dataset_rows": len(dataset["rows"]),
                  "correct": eval_report["correct"],
                  "total": eval_report["total"],
                  "skipped": eval_report["skipped"],
                  "accuracy_pm": acc,
                  "majority_baseline_pm": base,
                  "majority_label": eval_report["majority_label"],
                  "confusion": eval_report["confusion"],
                  "decision": codes.DECISIONS[decision["decision"]],
                  "decision_reason": codes.REASONS[decision["reason"]]}
    path = engine.save_evaluation(state_dir=args.state_dir,
                                  evaluation=evaluation)
    print(json.dumps({"evaluation": str(path), **evaluation}, indent=2))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    try:
        artifact = store.read_json(Path(args.artifact))
    except (OSError, ValueError) as error:
        print(f"mncs-learn: cannot read {args.artifact}: {error}",
              file=sys.stderr)
        return 2
    print(json.dumps(artifact, indent=2))
    return 0


def cmd_eligible(args: argparse.Namespace) -> int:
    mncs = _mncs(args)
    try:
        capability = json.loads(args.capability)
        rep = engine.check_eligible(
            mncs=mncs, capability=capability,
            obs_kind=int(args.obs_kind),
            rights_learn=not args.no_rights)
    except (ValueError, KeyError) as error:
        print(f"mncs-learn: bad input: {error}", file=sys.stderr)
        return 2
    except native.NativeError as error:
        print(f"mncs-learn: eligibility failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"ok": rep["ok"],
                      "reason": codes.REASONS.get(rep["reason"],
                                                 rep["reason"])}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mncs-learn")
    parser.add_argument("--state-dir", default="state")
    parser.add_argument("--mncs", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    train = sub.add_parser("train")
    train.add_argument("--file", required=True)
    train.add_argument("--name", required=True)
    train.add_argument("--ndim", type=int, default=None)
    train.add_argument("--evaluate", action="store_true")
    train.add_argument("--held-out", default=None)
    train.set_defaults(func=cmd_train)

    predict = sub.add_parser("predict")
    predict.add_argument("--artifact", required=True)
    predict.add_argument("--features", required=True,
                         help="comma-separated ints, e.g. 1,0")
    predict.set_defaults(func=cmd_predict)

    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--artifact", required=True)
    evaluate.add_argument("--file", required=True)
    evaluate.set_defaults(func=cmd_evaluate)

    show = sub.add_parser("show")
    show.add_argument("artifact")
    show.set_defaults(func=cmd_show)

    eligible = sub.add_parser("eligible")
    eligible.add_argument("--capability", required=True,
                          help="capability JSON")
    eligible.add_argument("--obs-kind", required=True)
    eligible.add_argument("--no-rights", action="store_true")
    eligible.set_defaults(func=cmd_eligible)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
