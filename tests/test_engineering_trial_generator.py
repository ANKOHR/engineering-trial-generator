from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from engineering_trial_generator.checker import check_trial_data
from engineering_trial_generator.fixtures import sample_evidence, sample_problems, write_fixtures
from engineering_trial_generator.generator import build_trial, load_problem, render_markdown, write_trial


ROOT = Path(__file__).resolve().parents[1]


def cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "engineering_trial_generator", *args],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_fixture_generator_writes_three_problems_and_evidence(tmp_path: Path) -> None:
    paths = write_fixtures(tmp_path)
    problems = list(tmp_path.glob("*.problem.json"))
    evidence = json.loads((tmp_path / "capability-evidence.json").read_text(encoding="utf-8"))

    assert len(paths) == 4
    assert len(problems) == 3
    assert len(evidence["projects"]) == 3
    assert evidence["fixture_status"] == "SYNTHETIC"


def test_fixture_generator_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_fixtures(first)
    write_fixtures(second)

    assert {path.name: path.read_bytes() for path in first.iterdir()} == {
        path.name: path.read_bytes() for path in second.iterdir()
    }


@pytest.mark.parametrize("problem", sample_problems(), ids=lambda item: item["id"])
def test_each_problem_fixture_is_labelled_synthetic(problem: dict) -> None:
    assert problem["fixture_status"] == "SYNTHETIC"


@pytest.mark.parametrize("problem", sample_problems(), ids=lambda item: item["id"])
def test_generation_has_required_trial_sections_and_checkable_criteria(problem: dict) -> None:
    trial = build_trial(problem, sample_evidence())

    assert trial["artifact"]["name"]
    assert trial["acceptance_criteria"]
    assert trial["assumptions"]
    assert trial["exclusions"]
    assert trial["fixed_price"]["amount"] > 0
    assert trial["time_box"]["days"] in (1, 2)
    assert check_trial_data(trial) == []


def test_present_capability_maps_to_its_evidence_pointer() -> None:
    trial = build_trial(
        {
            "id": "present",
            "title": "Invoice check",
            "description": "Check invoice rows.",
            "required_claims": ["parse invoice CSV rows"],
        },
        sample_evidence(),
    )

    mapping = trial["claim_coverage"]["mapped_claims"][0]
    assert mapping["project"] == "Synthetic Ledger Linter"
    assert "synthetic://ledger-linter/src/csv_reader.py" in mapping["evidence_pointers"]
    assert trial["claim_coverage"]["unsupported_count"] == 0


def test_absent_capability_is_flagged_and_excluded() -> None:
    trial = build_trial(
        {
            "id": "absent",
            "title": "Voice assistant",
            "description": "Create a voice assistant.",
            "required_claims": ["deploy a speech recognition service"],
        },
        sample_evidence(),
    )

    assert trial["claim_coverage"]["mapped_count"] == 0
    assert trial["claim_coverage"]["unsupported_claims"][0]["claim"] == "deploy a speech recognition service"
    assert "not implementation promises" in trial["exclusions"][-1]
    assert "not promised" in render_markdown(trial)


def test_generation_is_byte_identical_for_markdown_and_json(tmp_path: Path) -> None:
    problem = sample_problems()[0]
    first = tmp_path / "first"
    second = tmp_path / "second"
    trial = build_trial(problem, sample_evidence())
    first_md, first_json = write_trial(trial, first)
    second_md, second_json = write_trial(build_trial(problem, sample_evidence()), second)

    assert first_md.read_bytes() == second_md.read_bytes()
    assert first_json.read_bytes() == second_json.read_bytes()


def test_checker_flags_vague_criteria_with_specific_findings() -> None:
    findings = check_trial_data(
        {
            "acceptance_criteria": [
                {"id": "AC-1", "condition": "The output is high quality.", "owner": "", "verification_method": "review output"}
            ]
        }
    )
    codes = {finding["code"] for finding in findings}

    assert "criterion.vague_wording" in codes
    assert "criterion.not_measurable" in codes
    assert "criterion.owner_missing" in codes
    assert "criterion.method_not_verifiable" in codes
    assert all(finding["path"].startswith("acceptance_criteria[0]") for finding in findings)


def test_checker_accepts_clean_criterion() -> None:
    assert check_trial_data(
        {
            "acceptance_criteria": [
                {
                    "id": "AC-1",
                    "condition": "The result contains exactly 3 CSV data rows.",
                    "owner": "Buyer",
                    "verification_method": "Count the data rows in the CSV file.",
                }
            ]
        }
    ) == []


def test_json_problem_without_claims_uses_conservative_plain_text_inference(tmp_path: Path) -> None:
    problem_path = tmp_path / "problem.json"
    problem_path.write_text(
        json.dumps({"title": "Invoice matching", "description": "We compare invoice CSV exports."}),
        encoding="utf-8",
    )

    problem = load_problem(problem_path)
    trial = build_trial(problem, sample_evidence())
    assert problem["required_claims"] == [
        "parse invoice CSV rows",
        "compare invoice totals and flag mismatches",
    ]
    assert trial["claim_coverage"]["mapped_count"] == 2


def test_fixtures_cli_smoke(tmp_path: Path) -> None:
    result = cli("fixtures", "--out", str(tmp_path / "fixtures"))
    assert result.returncode == 0, result.stderr
    assert "fictional" in result.stdout.casefold()
    assert (tmp_path / "fixtures" / "capability-evidence.json").exists()


def test_generate_cli_smoke(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures"
    write_fixtures(fixture_dir)
    problem = fixture_dir / "invoice-reconciliation.problem.json"
    evidence = fixture_dir / "capability-evidence.json"
    result = cli("generate", "--problem", str(problem), "--evidence", str(evidence), "--out", str(tmp_path / "out"))
    assert result.returncode == 0, result.stderr
    assert "2 mapped" in result.stdout
    assert (tmp_path / "out" / "invoice-reconciliation.md").exists()
    assert (tmp_path / "out" / "invoice-reconciliation.json").exists()


def test_check_cli_smoke_pass_and_findings(tmp_path: Path) -> None:
    clean_path = tmp_path / "clean.json"
    clean_path.write_text(
        json.dumps({"acceptance_criteria": [{
            "condition": "The file contains exactly 2 rows.",
            "owner": "Buyer",
            "verification_method": "Count rows in the file.",
        }]}),
        encoding="utf-8",
    )
    passing = cli("check", "--trial", str(clean_path))
    assert passing.returncode == 0
    assert "PASS" in passing.stdout

    vague_path = tmp_path / "vague.json"
    vague_path.write_text(
        json.dumps({"acceptance_criteria": [{
            "condition": "The output is high quality.",
            "owner": "Buyer",
            "verification_method": "Inspect the output.",
        }]}),
        encoding="utf-8",
    )
    failing = cli("check", "--trial", str(vague_path))
    assert failing.returncode == 1
    assert "criterion.vague_wording" in failing.stdout


def test_report_cli_smoke_generates_three_trials_and_coverage_index(tmp_path: Path) -> None:
    out = tmp_path / "report"
    result = cli("report", "--out", str(out))

    assert result.returncode == 0, result.stderr
    assert len(list(out.glob("*.json"))) == 3
    assert len(list(out.glob("*.md"))) == 4
    index = (out / "index.md").read_text(encoding="utf-8")
    assert "fictional synthetic fixtures" in index
    assert "Mapped claims" in index
    assert "Flagged unsupported" in index


def test_plain_text_problem_falls_back_to_an_unsupported_claim(tmp_path: Path) -> None:
    problem_path = tmp_path / "problem.txt"
    problem_path.write_text("A team wants a custom quantum computing platform.", encoding="utf-8")

    problem = load_problem(problem_path)
    trial = build_trial(problem, sample_evidence())
    assert trial["claim_coverage"]["mapped_count"] == 0
    assert trial["claim_coverage"]["unsupported_count"] == 1


def test_synthetic_fixture_evidence_projects_are_explicitly_labelled() -> None:
    evidence = sample_evidence()
    assert all(project["fixture_status"] == "SYNTHETIC" for project in evidence["projects"])
    assert all(pointer.startswith("synthetic://") for project in evidence["projects"] for item in project["capabilities"] for pointer in item["evidence_pointers"])


def test_claim_without_any_evidence_pointer_is_unsupported() -> None:
    evidence = {
        "projects": [
            {
                "name": "Empty pointer project",
                "capabilities": [{"claim": "parse invoice CSV rows", "evidence_pointers": []}],
            }
        ]
    }
    trial = build_trial(
        {"id": "empty-pointer", "title": "Invoice", "description": "Invoices", "required_claims": ["parse invoice CSV rows"]},
        evidence,
    )
    assert trial["claim_coverage"]["mapped_count"] == 0
    assert trial["claim_coverage"]["unsupported_count"] == 1


def test_acceptance_criteria_are_generated_from_profile_values() -> None:
    problem = sample_problems()[0]
    assert "acceptance_checks" not in problem
    trial = build_trial(problem, sample_evidence())
    assert "10-row synthetic invoice input" in trial["acceptance_criteria"][1]["condition"]
    assert "8 matching rows" in trial["acceptance_criteria"][1]["condition"]
    assert "Coverage table" in render_markdown(trial)


def test_scope_threshold_sets_two_day_price() -> None:
    trial = build_trial(
        {
            "id": "larger-scope",
            "title": "Larger scope",
            "description": "Compare invoices and export their totals.",
            "required_claims": [
                "parse invoice CSV rows",
                "compare invoice totals and flag mismatches",
                "extract document sections and citations",
            ],
            "acceptance_checks": [
                {"condition": f"The output has exactly {number} files.", "owner": "Buyer", "verification_method": "Count the output files."}
                for number in range(1, 5)
            ],
        },
        sample_evidence(),
    )
    assert trial["time_box"]["days"] == 2
    assert trial["fixed_price"]["amount"] == 2 * 750 + 4 * 125
