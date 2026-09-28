"""Parse problem inputs, map capability claims, and render trial definitions."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CLAIM_CATALOGUE = [
    "parse invoice CSV rows",
    "compare invoice totals and flag mismatches",
    "extract document sections and citations",
    "validate links and required sections",
    "compare order records across two exports",
    "produce a reviewable mismatch report",
]


def normalize_claim(value: str) -> str:
    """Normalize a claim for exact, conservative matching."""
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def slugify(value: str) -> str:
    """Create a stable filesystem-safe identifier."""
    result = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return result[:64].rstrip("-") or "trial"


def _infer_claims(description: str) -> list[str]:
    text = description.casefold()
    groups = [
        (("invoice", "reconcil", "billing", "csv export"), CLAIM_CATALOGUE[:2]),
        (("support doc", "help doc", "documentation", "knowledge base"), CLAIM_CATALOGUE[2:4]),
        (("order", "sync", "commerce export", "shop"), CLAIM_CATALOGUE[4:6]),
    ]
    found: list[str] = []
    for keywords, claims in groups:
        if any(keyword in text for keyword in keywords):
            found.extend(claims)
    return found or ["deliver a checkable workflow for the described problem"]


def load_problem(path: str | Path) -> dict[str, Any]:
    """Load a JSON problem object or infer a conservative claim from plain text."""
    source = Path(path)
    raw = source.read_text(encoding="utf-8-sig")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        description = raw.strip()
        if not description:
            raise ValueError(f"Problem file is empty: {source}")
        title = description.splitlines()[0].strip()
        return {
            "id": slugify(source.stem),
            "title": title[:120],
            "description": description,
            "required_claims": _infer_claims(description),
            "fixture_status": "USER PROVIDED",
        }

    if not isinstance(parsed, dict):
        raise ValueError("Problem JSON must contain an object at its root.")
    description = parsed.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Problem JSON must include a non-empty description string.")
    if "title" in parsed and not isinstance(parsed["title"], str):
        raise ValueError("title must be a string.")
    if "fixture_status" in parsed and not isinstance(parsed["fixture_status"], str):
        raise ValueError("fixture_status must be a string.")
    claims = parsed.get("required_claims")
    if claims is None:
        claims = _infer_claims(description)
    if not isinstance(claims, list) or any(not isinstance(claim, str) or not claim.strip() for claim in claims):
        raise ValueError("required_claims must be a list of non-empty strings.")
    artifact = parsed.get("artifact")
    if artifact is not None:
        if not isinstance(artifact, dict):
            raise ValueError("artifact must be an object.")
        if "files" in artifact and (
            not isinstance(artifact["files"], list)
            or any(not isinstance(name, str) or not name.strip() for name in artifact["files"])
        ):
            raise ValueError("artifact.files must be a list of non-empty strings.")
        if "name" in artifact and not isinstance(artifact["name"], str):
            raise ValueError("artifact.name must be a string.")
        if "format" in artifact and not isinstance(artifact["format"], str):
            raise ValueError("artifact.format must be a string.")
    for field in ("assumptions", "exclusions"):
        values = parsed.get(field)
        if values is not None and (
            not isinstance(values, list) or any(not isinstance(value, str) for value in values)
        ):
            raise ValueError(f"{field} must be a list of strings.")
    checks = parsed.get("acceptance_checks")
    if checks is not None and not isinstance(checks, list):
        raise ValueError("acceptance_checks must be a list.")
    profile = parsed.get("acceptance_profile")
    if profile is not None and not isinstance(profile, dict):
        raise ValueError("acceptance_profile must be an object.")
    profile_requirements = {
        "invoice_csv_reconciliation": {
            "counts": ("input_rows", "matched_rows", "mismatched_rows"),
            "lists": ("required_exception_columns",),
        },
        "support_document_audit": {
            "counts": (
                "document_rows",
                "link_pass_rows",
                "link_fail_rows",
                "broken_link_findings",
                "missing_section_findings",
            ),
            "lists": ("source_map_columns",),
        },
        "two_export_order_comparison": {
            "counts": ("left_records", "right_records", "matched_records", "mismatched_records"),
            "lists": ("mismatch_columns",),
        },
    }
    if isinstance(profile, dict) and profile.get("kind") in profile_requirements:
        requirements = profile_requirements[profile["kind"]]
        for field in requirements["counts"]:
            if not isinstance(profile.get(field), int) or isinstance(profile.get(field), bool) or profile[field] < 0:
                raise ValueError(f"acceptance_profile.{field} must be a non-negative integer.")
        for field in requirements["lists"]:
            values = profile.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(value, str) or not value for value in values):
                raise ValueError(f"acceptance_profile.{field} must be a non-empty list of strings.")
    clean_claims: list[str] = []
    seen: set[str] = set()
    for claim in claims:
        key = normalize_claim(claim)
        if key and key not in seen:
            clean_claims.append(claim.strip())
            seen.add(key)
    return {
        **parsed,
        "id": slugify(str(parsed.get("id") or parsed.get("title") or source.stem)),
        "title": str(parsed.get("title") or source.stem),
        "description": description.strip(),
        "required_claims": clean_claims,
    }


def load_evidence(path: str | Path) -> dict[str, Any]:
    """Load and validate the capability evidence catalogue."""
    source = Path(path)
    try:
        parsed = json.loads(source.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Evidence file is not valid JSON: {source}: {exc.msg}") from exc
    if not isinstance(parsed, dict) or not isinstance(parsed.get("projects"), list):
        raise ValueError("Evidence JSON must contain a projects list.")
    for project_index, project in enumerate(parsed["projects"]):
        if not isinstance(project, dict) or not isinstance(project.get("name"), str):
            raise ValueError(f"Evidence project at index {project_index} must have a name.")
        capabilities = project.get("capabilities", [])
        if not isinstance(capabilities, list):
            raise ValueError(f"Capabilities for project {project['name']} must be a list.")
        for capability_index, capability in enumerate(capabilities):
            if (
                not isinstance(capability, dict)
                or not isinstance(capability.get("claim"), str)
                or not isinstance(capability.get("evidence_pointers"), list)
                or any(not isinstance(pointer, str) or not pointer.strip() for pointer in capability["evidence_pointers"])
            ):
                raise ValueError(
                    f"Capability {capability_index} for project {project['name']} needs a claim and evidence_pointers list."
                )
    return parsed


def map_claims(claims: list[str], evidence: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """Map exact normalized claims to the first supporting project, or flag them."""
    index: dict[str, tuple[dict, dict]] = {}
    for project in evidence["projects"]:
        for capability in project.get("capabilities", []):
            key = normalize_claim(capability["claim"])
            if key and capability["evidence_pointers"] and key not in index:
                index[key] = (project, capability)

    mapped: list[dict] = []
    unsupported: list[dict] = []
    for claim in claims:
        match = index.get(normalize_claim(claim))
        if match:
            project, capability = match
            mapped.append(
                {
                    "claim": claim,
                    "project": project["name"],
                    "evidence_pointers": list(capability["evidence_pointers"]),
                }
            )
        else:
            unsupported.append({"claim": claim, "reason": "No exact capability claim with evidence pointers was found."})
    return mapped, unsupported


def _generated_acceptance_checks(
    problem: dict[str, Any], artifact: dict[str, Any], mapped: list[dict], unsupported: list[dict]
) -> list[dict[str, str]]:
    """Generate objective criteria from a typed acceptance profile or artifact scope."""
    provided = problem.get("acceptance_checks")
    if isinstance(provided, list) and provided:
        return provided

    profile = problem.get("acceptance_profile", {})
    kind = profile.get("kind") if isinstance(profile, dict) else None
    if kind == "invoice_csv_reconciliation":
        files = artifact.get("files", [])
        columns = profile["required_exception_columns"]
        return [
            {
                "condition": f"The output directory contains exactly {len(files)} files: {', '.join(files)}.",
                "owner": "Buyer",
                "verification_method": "List the output directory and compare the filenames with the required set.",
            },
            {
                "condition": (
                    f"Given the {profile['input_rows']}-row synthetic invoice input, reconciled.csv contains "
                    f"{profile['matched_rows']} matching rows and exceptions.csv contains {profile['mismatched_rows']} mismatch rows."
                ),
                "owner": "Buyer",
                "verification_method": "Run the script on the supplied synthetic CSV, then count data rows in both output CSV files.",
            },
            {
                "condition": f"Each exceptions.csv row includes {', '.join(columns)} columns.",
                "owner": "Buyer",
                "verification_method": f"Open exceptions.csv and compare its header row with the {len(columns)} required column names.",
            },
        ]
    if kind == "support_document_audit":
        columns = profile["source_map_columns"]
        row_count = profile["document_rows"]
        return [
            {
                "condition": f"source-map.csv contains exactly {row_count} data rows, each with non-empty {', '.join(columns)} values.",
                "owner": "Buyer",
                "verification_method": f"Count source-map.csv rows and inspect the {len(columns)} required columns for blank cells.",
            },
            {
                "condition": (
                    f"link-results.csv contains exactly {row_count} data rows: {profile['link_pass_rows']} PASS "
                    f"and {profile['link_fail_rows']} FAIL status values."
                ),
                "owner": "Buyer",
                "verification_method": "Count data rows and compare the status column values with the required totals.",
            },
            {
                "condition": (
                    f"issues.csv contains exactly {profile['broken_link_findings'] + profile['missing_section_findings']} data rows: "
                    f"{profile['broken_link_findings']} broken-link findings and {profile['missing_section_findings']} missing-section findings."
                ),
                "owner": "Buyer",
                "verification_method": "Count issues.csv rows and group finding_type values into the 2 required categories.",
            },
        ]
    if kind == "two_export_order_comparison":
        columns = profile["mismatch_columns"]
        return [
            {
                "condition": (
                    f"comparison-summary.json reports exactly {profile['left_records']} left records, "
                    f"{profile['right_records']} right records, {profile['matched_records']} matched records, "
                    f"and {profile['mismatched_records']} mismatched records."
                ),
                "owner": "Buyer",
                "verification_method": "Parse comparison-summary.json and compare each count with the 4 specified values.",
            },
            {
                "condition": (
                    f"mismatches.csv contains exactly {profile['mismatched_records']} data rows and the columns {', '.join(columns)}."
                ),
                "owner": "Buyer",
                "verification_method": f"Count mismatches.csv rows and compare its header with the {len(columns)} required column names.",
            },
            {
                "condition": (
                    f"matched.csv contains exactly {profile['matched_records']} data rows, with one row per matching order_id."
                ),
                "owner": "Buyer",
                "verification_method": "Count matched.csv data rows and verify that order_id values are unique.",
            },
        ]

    files = artifact.get("files", [])
    return [
        {
            "condition": f"The output directory contains exactly {len(files)} artifact files: {', '.join(files)}.",
            "owner": "Buyer",
            "verification_method": "List the output directory and compare the filenames with the required set.",
        },
        {
            "condition": f"The capability coverage table contains exactly {len(mapped) + len(unsupported)} rows, one per required claim, with MAPPED or UNSUPPORTED status.",
            "owner": "Buyer",
            "verification_method": "Open the returned trial summary, count table rows, and compare each status with its evidence pointer.",
        },
        {
            "condition": f"Every one of the {len(unsupported)} unsupported claims is listed under Unsupported claims and in Exclusions.",
            "owner": "Buyer",
            "verification_method": "Compare the unsupported claims list with the Exclusions section in the returned trial summary.",
        },
    ]


def build_trial(problem: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    """Build the complete deterministic trial definition object."""
    mapped, unsupported = map_claims(problem["required_claims"], evidence)
    artifact = problem.get("artifact")
    if not isinstance(artifact, dict):
        artifact = {
            "name": f"Trial readiness note for {problem['title']}",
            "files": ["trial-summary.md"],
            "format": "A Markdown assessment with Inputs, Outputs, Limitations, and a capability coverage table.",
        }
    acceptance = _generated_acceptance_checks(problem, artifact, mapped, unsupported)
    acceptance_criteria = []
    for number, check in enumerate(acceptance, start=1):
        if not isinstance(check, dict):
            check = {"condition": str(check)}
        acceptance_criteria.append(
            {
                "id": f"AC-{number:02d}",
                "condition": str(check.get("condition", "")),
                "owner": str(check.get("owner", "Buyer")),
                "verification_method": str(check.get("verification_method", "")),
            }
        )

    days = 2 if len(acceptance_criteria) > 3 or len(mapped) > 2 else 1
    price = days * 750 + len(acceptance_criteria) * 125
    exclusions = [str(item) for item in problem.get("exclusions", [])]
    if unsupported:
        exclusions.append(
            "Unsupported claims are outside this trial scope and are not implementation promises: "
            + "; ".join(item["claim"] for item in unsupported)
            + "."
        )
    assumptions = [str(item) for item in problem.get("assumptions", [])]
    if not assumptions:
        assumptions = ["The buyer supplies the agreed input files and a named contact for acceptance review."]

    return {
        "schema_version": "1.0",
        "id": problem["id"],
        "title": problem["title"],
        "fixture_status": problem.get("fixture_status", "USER PROVIDED"),
        "honesty_boundary": (
            "This tool is a scoping aid for checkable trial definitions, not a guarantee of outcomes. "
            "Synthetic demo claims describe fictional examples and no real engagements. "
            "Evidence pointers are supplied by the input and are not independently inspected."
        ),
        "problem": problem["description"],
        "scope_status": "evidence-backed scope with flagged gaps" if unsupported else "evidence-backed scope",
        "artifact": {
            "name": str(artifact.get("name", "Trial artifact")),
            "files": list(artifact.get("files", [])),
            "format": str(artifact.get("format", "")),
            "scope_limit": (
                "Only mapped capabilities are in scope. Unsupported claims remain excluded."
                if unsupported
                else "The artifact is limited to the mapped capabilities and listed acceptance criteria."
            ),
        },
        "claim_coverage": {
            "mapped_count": len(mapped),
            "unsupported_count": len(unsupported),
            "mapped_claims": mapped,
            "unsupported_claims": unsupported,
        },
        "acceptance_criteria": acceptance_criteria,
        "assumptions": assumptions,
        "exclusions": exclusions,
        "time_box": {"days": days, "label": f"{days} day" if days == 1 else f"{days} days"},
        "fixed_price": {
            "amount": price,
            "currency": "GBP",
            "display": f"GBP {price:,}",
            "pricing_rule": "GBP 750 per day plus GBP 125 per acceptance criterion; day count follows the documented scope threshold.",
        },
    }


def render_markdown(trial: dict[str, Any]) -> str:
    """Render a stable proposal appendix in Markdown."""
    opening_note = (
        "Fictional synthetic fixture example. This tool is a scoping aid, not a guarantee of outcomes. The demo claims no real engagements."
        if trial["fixture_status"] == "SYNTHETIC"
        else "This tool is a scoping aid, not a guarantee of outcomes. Confirm the inputs and scope before using this definition."
    )
    lines = [
        f"# Trial definition: {trial['title']}",
        "",
        f"> {opening_note}",
        "",
        f"**Fixture status:** {trial['fixture_status']}",
        f"**Scope status:** {trial['scope_status']}",
        "",
        "## Problem",
        "",
        trial["problem"],
        "",
        "## Evidence limit",
        "",
        "Evidence pointers are supplied by the input and are not independently inspected by this tool.",
        "",
        "## Exact artifact to be returned",
        "",
        f"**{trial['artifact']['name']}**. {trial['artifact']['format']}",
        "",
        "Files:",
    ]
    lines.extend(f"- `{name}`" for name in trial["artifact"]["files"])
    lines.extend(["", trial["artifact"]["scope_limit"], "", "## Claim-to-evidence mapping", ""])
    coverage = trial["claim_coverage"]
    lines.append(f"Coverage: {coverage['mapped_count']} mapped, {coverage['unsupported_count']} flagged unsupported.")
    lines.extend(["", "### Coverage table", "", "| Claim | Status | Project | Evidence pointers |", "| --- | --- | --- | --- |"])
    for item in coverage["mapped_claims"]:
        claim = item["claim"].replace("|", "\\|")
        project = item["project"].replace("|", "\\|")
        pointer_list = ", ".join(f"`{pointer}`" for pointer in item["evidence_pointers"])
        lines.append(f"| {claim} | MAPPED | {project} | {pointer_list} |")
    for item in coverage["unsupported_claims"]:
        claim = item["claim"].replace("|", "\\|")
        lines.append(f"| {claim} | UNSUPPORTED | Not applicable | No evidence pointer found |")
    lines.extend(["", "### Mapped claims", ""])
    if coverage["mapped_claims"]:
        for item in coverage["mapped_claims"]:
            lines.append(f"- **{item['claim']}** maps to **{item['project']}**.")
            lines.extend(f"  - Evidence pointer: `{pointer}`" for pointer in item["evidence_pointers"])
    else:
        lines.append("- None.")
    lines.extend(["", "### Unsupported claims", ""])
    if coverage["unsupported_claims"]:
        for item in coverage["unsupported_claims"]:
            lines.append(f"- **{item['claim']}**: {item['reason']} This claim is not promised.")
    else:
        lines.append("- None.")
    lines.extend(["", "## Acceptance criteria", ""])
    for criterion in trial["acceptance_criteria"]:
        lines.extend(
            [
                f"### {criterion['id']}",
                "",
                f"- Condition: {criterion['condition']}",
                f"- Owner: {criterion['owner']}",
                f"- Verification method: {criterion['verification_method']}",
                "",
            ]
        )
    lines.extend(["## Assumptions", ""])
    lines.extend(f"- {assumption}" for assumption in trial["assumptions"])
    lines.extend(["", "## Exclusions", ""])
    lines.extend(f"- {exclusion}" for exclusion in trial["exclusions"])
    lines.extend(
        [
            "",
            "## Commercial terms",
            "",
            f"- Fixed price: **{trial['fixed_price']['display']}**",
            f"- Time box: **{trial['time_box']['label']}**",
            f"- Pricing rule: {trial['fixed_price']['pricing_rule']}",
            "",
        ]
    )
    return "\n".join(lines)


def write_trial(trial: dict[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    """Write a trial's JSON and Markdown files deterministically."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / f"{trial['id']}.json"
    markdown_path = target / f"{trial['id']}.md"
    json_path.write_text(
        json.dumps(trial, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(trial), encoding="utf-8")
    return markdown_path, json_path
