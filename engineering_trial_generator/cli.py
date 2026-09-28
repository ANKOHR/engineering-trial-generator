"""Command line interface for the Engineering Trial Generator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checker import check_trial_file
from .fixtures import write_fixtures
from .generator import build_trial, load_evidence, load_problem, write_trial
from .report import create_report

HONESTY_NOTICE = "Scoping aid only, not a guarantee of outcomes. The synthetic demo claims no real engagements."


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="engineering-trial-generator",
        description=(
            "Generate evidence-mapped, checkable paid trial definitions. "
            "Scoping aid only, not a guarantee of outcomes. The synthetic demo claims no real engagements."
        ),
    )
    commands = parser.add_subparsers(dest="command", required=True)

    fixtures = commands.add_parser("fixtures", help="write fictional synthetic sample inputs")
    fixtures.add_argument("--out", required=True, help="directory for sample problem and evidence JSON files")

    generate = commands.add_parser("generate", help="generate one Markdown and JSON trial definition")
    generate.add_argument("--problem", required=True, help="problem JSON or UTF-8 plain text file")
    generate.add_argument("--evidence", required=True, help="capability evidence JSON file")
    generate.add_argument("--out", required=True, help="output directory for the trial definition")

    check = commands.add_parser("check", help="verify acceptance criteria in a trial JSON file")
    check.add_argument("--trial", required=True, help="trial definition JSON file")

    report = commands.add_parser("report", help="generate all synthetic sample trials and an index")
    report.add_argument("--out", required=True, help="output directory for trial definitions and index")
    return parser


def run(args: argparse.Namespace) -> int:
    if args.command == "fixtures":
        written = write_fixtures(args.out)
        print(f"Wrote {len(written)} synthetic fixture files to {Path(args.out)}.")
        print("All sample problems and capability evidence are fictional, labelled SYNTHETIC, and claim no real engagements.")
        print(HONESTY_NOTICE)
        return 0
    if args.command == "generate":
        problem = load_problem(args.problem)
        evidence = load_evidence(args.evidence)
        trial = build_trial(problem, evidence)
        markdown_path, json_path = write_trial(trial, args.out)
        print(f"Wrote trial definition: {markdown_path}")
        print(f"Wrote trial JSON: {json_path}")
        print(
            "Coverage: "
            f"{trial['claim_coverage']['mapped_count']} mapped, "
            f"{trial['claim_coverage']['unsupported_count']} flagged unsupported."
        )
        print("Evidence pointer strings are supplied by the input and their targets are not inspected.")
        print(HONESTY_NOTICE)
        return 0
    if args.command == "check":
        findings = check_trial_file(args.trial)
        if findings:
            print(f"FAIL: {len(findings)} finding(s).")
            for finding in findings:
                print(f"{finding['code']} at {finding['path']}: {finding['message']}")
            print(HONESTY_NOTICE)
            return 1
        print("PASS: all acceptance criteria include measurable conditions, an owner, and a verification method.")
        print(HONESTY_NOTICE)
        return 0
    if args.command == "report":
        written, index = create_report(args.out)
        print(f"Wrote {len(written) - 1} trial definition files for 3 fictional synthetic problems.")
        print(f"Demo index: {index}")
        print("All projects and results are fictional; the demo claims no real engagements.")
        print(HONESTY_NOTICE)
        return 0
    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
