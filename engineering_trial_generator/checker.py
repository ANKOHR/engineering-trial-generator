"""Objective, structural checks for generated trial acceptance criteria."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


VAGUE_PHRASES = (
    "high quality",
    "user friendly",
    "user-friendly",
    "robust",
    "fast",
    "seamless",
    "appropriate",
    "intuitive",
    "easy to use",
)
MEASURABLE_MARKERS = re.compile(
    r"\d|\b(exactly|at least|at most|no more than|no fewer than|every|each|all|none|zero|one|once|twice)\b",
    re.IGNORECASE,
)
METHOD_ACTIONS = re.compile(
    r"\b(open|list|count|compare|run|inspect|parse|validate|check|calculate|assert|verify|read|group|test|measure|sort|match|diff)\b",
    re.IGNORECASE,
)


def check_trial_data(trial: Any) -> list[dict[str, str]]:
    """Return deterministic findings. An empty list means the trial passes."""
    findings: list[dict[str, str]] = []
    if not isinstance(trial, dict):
        return [{"code": "trial.invalid_root", "path": "$", "message": "Trial JSON root must be an object."}]
    criteria = trial.get("acceptance_criteria")
    if not isinstance(criteria, list) or not criteria:
        return [
            {
                "code": "criteria.missing",
                "path": "acceptance_criteria",
                "message": "At least one acceptance criterion is required.",
            }
        ]

    for index, criterion in enumerate(criteria):
        base = f"acceptance_criteria[{index}]"
        if not isinstance(criterion, dict):
            findings.append(
                {
                    "code": "criterion.invalid",
                    "path": base,
                    "message": "Criterion must be an object with condition, owner, and verification_method fields.",
                }
            )
            continue
        condition = criterion.get("condition")
        if not isinstance(condition, str) or not condition.strip():
            findings.append(
                {
                    "code": "criterion.condition_missing",
                    "path": f"{base}.condition",
                    "message": "Add a non-empty, measurable condition.",
                }
            )
            condition = ""
        else:
            for phrase in VAGUE_PHRASES:
                if phrase in condition.casefold():
                    findings.append(
                        {
                            "code": "criterion.vague_wording",
                            "path": f"{base}.condition",
                            "message": f"Vague phrase '{phrase}' is not objectively checkable; replace it with a measurable threshold or exact rule.",
                        }
                    )
            if not MEASURABLE_MARKERS.search(condition):
                findings.append(
                    {
                        "code": "criterion.not_measurable",
                        "path": f"{base}.condition",
                        "message": "Condition has no count, threshold, exact value, or explicit each/every rule.",
                    }
                )

        owner = criterion.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            findings.append(
                {
                    "code": "criterion.owner_missing",
                    "path": f"{base}.owner",
                    "message": "Name the person or role responsible for acceptance.",
                }
            )
        method = criterion.get("verification_method")
        if not isinstance(method, str) or not method.strip():
            findings.append(
                {
                    "code": "criterion.method_missing",
                    "path": f"{base}.verification_method",
                    "message": "Provide a verification method a third party can perform.",
                }
            )
        elif not METHOD_ACTIONS.search(method):
            findings.append(
                {
                    "code": "criterion.method_not_verifiable",
                    "path": f"{base}.verification_method",
                    "message": "Method must name an action such as inspect, count, compare, parse, or run.",
                }
            )
    return findings


def check_trial_file(path: str | Path) -> list[dict[str, str]]:
    """Load a JSON trial definition and return structural findings."""
    source = Path(path)
    try:
        trial = json.loads(source.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return [
            {
                "code": "trial.invalid_json",
                "path": str(source),
                "message": f"Trial definition must be JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}.",
            }
        ]
    return check_trial_data(trial)
