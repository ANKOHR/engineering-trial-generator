"""Synthetic examples used by the fixtures and report commands."""

from __future__ import annotations

import json
from pathlib import Path


def sample_evidence() -> dict:
    """Return fictional capability claims and synthetic evidence pointers."""
    return {
        "fixture_status": "SYNTHETIC",
        "label": "Fictional capability evidence for demonstration only",
        "projects": [
            {
                "name": "Synthetic Ledger Linter",
                "fixture_status": "SYNTHETIC",
                "description": "A fictional CSV reconciliation prototype and test suite.",
                "capabilities": [
                    {
                        "claim": "parse invoice CSV rows",
                        "evidence_pointers": [
                            "synthetic://ledger-linter/src/csv_reader.py",
                            "synthetic://ledger-linter/tests/test_csv_reader.py#6-cases",
                            "synthetic://ledger-linter/demo/index.html",
                        ],
                    },
                    {
                        "claim": "compare invoice totals and flag mismatches",
                        "evidence_pointers": [
                            "synthetic://ledger-linter/src/reconcile.py",
                            "synthetic://ledger-linter/tests/test_reconcile.py#8-cases",
                        ],
                    },
                ],
            },
            {
                "name": "Synthetic Doc Trust Checker",
                "fixture_status": "SYNTHETIC",
                "description": "A fictional documentation inventory and link-check prototype.",
                "capabilities": [
                    {
                        "claim": "extract document sections and citations",
                        "evidence_pointers": [
                            "synthetic://doc-trust/src/section_index.py",
                            "synthetic://doc-trust/tests/test_section_index.py#7-cases",
                        ],
                    },
                    {
                        "claim": "validate links and required sections",
                        "evidence_pointers": [
                            "synthetic://doc-trust/src/doc_checks.py",
                            "synthetic://doc-trust/tests/test_doc_checks.py#9-cases",
                            "synthetic://doc-trust/demo/index.html",
                        ],
                    },
                ],
            },
            {
                "name": "Synthetic Order Pair Diff",
                "fixture_status": "SYNTHETIC",
                "description": "A fictional comparison tool for two exported order lists.",
                "capabilities": [
                    {
                        "claim": "compare order records across two exports",
                        "evidence_pointers": [
                            "synthetic://order-pair-diff/src/compare.py",
                            "synthetic://order-pair-diff/tests/test_compare.py#10-cases",
                        ],
                    },
                    {
                        "claim": "produce a reviewable mismatch report",
                        "evidence_pointers": [
                            "synthetic://order-pair-diff/src/report.py",
                            "synthetic://order-pair-diff/tests/test_report.py#5-cases",
                            "synthetic://order-pair-diff/demo/index.html",
                        ],
                    },
                ],
            },
        ],
    }


def sample_problems() -> list[dict]:
    """Return three fully fictional, bounded sample business problems."""
    return [
        {
            "id": "invoice-reconciliation",
            "fixture_status": "SYNTHETIC",
            "title": "Invoice reconciliation errors",
            "description": (
                "A small finance team manually compares invoice exports and spends "
                "time finding total mismatches."
            ),
            "required_claims": [
                "parse invoice CSV rows",
                "compare invoice totals and flag mismatches",
            ],
            "artifact": {
                "name": "Invoice reconciliation validator",
                "files": ["reconciled.csv", "exceptions.csv", "README.md"],
                "format": "A runnable standard-library Python script with CSV input and output.",
            },
            "acceptance_profile": {
                "kind": "invoice_csv_reconciliation",
                "input_rows": 10,
                "matched_rows": 8,
                "mismatched_rows": 2,
                "required_exception_columns": [
                    "invoice_id",
                    "expected_total",
                    "observed_total",
                    "difference",
                ],
            },
            "assumptions": [
                "The buyer supplies one UTF-8 CSV with invoice_id, expected_total, and observed_total columns.",
                "Currency values use decimal notation with a period separator.",
            ],
            "exclusions": [
                "No connection to accounting software or live financial data.",
                "No tax, foreign exchange, or accounting policy advice.",
            ],
        },
        {
            "id": "support-document-trust",
            "fixture_status": "SYNTHETIC",
            "title": "Support documents nobody trusts",
            "description": (
                "A support team wants a repeatable way to inspect a fixed set of "
                "help documents for broken links and missing required sections."
            ),
            "required_claims": [
                "extract document sections and citations",
                "validate links and required sections",
            ],
            "artifact": {
                "name": "Support documentation audit bundle",
                "files": ["source-map.csv", "link-results.csv", "issues.csv", "README.md"],
                "format": "A runnable standard-library checker and three CSV result files.",
            },
            "acceptance_profile": {
                "kind": "support_document_audit",
                "document_rows": 12,
                "link_pass_rows": 10,
                "link_fail_rows": 2,
                "broken_link_findings": 2,
                "missing_section_findings": 2,
                "source_map_columns": ["source_id", "section_heading", "citation_locator"],
            },
            "assumptions": [
                "The buyer supplies a frozen bundle of 12 UTF-8 help documents and a required-section list.",
                "The trial checks local copies and does not crawl or change a live help centre.",
            ],
            "exclusions": [
                "No rewrite or factual review of support content.",
                "No live website monitoring or content-management integration.",
            ],
        },
        {
            "id": "two-system-order-sync",
            "fixture_status": "SYNTHETIC",
            "title": "Manual order syncing between two systems",
            "description": (
                "A shop manually compares two order exports and needs a concise "
                "review list of records that differ."
            ),
            "required_claims": [
                "compare order records across two exports",
                "produce a reviewable mismatch report",
            ],
            "artifact": {
                "name": "Two-export order comparison bundle",
                "files": ["matched.csv", "mismatches.csv", "comparison-summary.json", "README.md"],
                "format": "A runnable standard-library comparator and CSV/JSON result files.",
            },
            "acceptance_profile": {
                "kind": "two_export_order_comparison",
                "left_records": 25,
                "right_records": 25,
                "matched_records": 22,
                "mismatched_records": 3,
                "mismatch_columns": [
                    "order_id",
                    "left_status",
                    "right_status",
                    "mismatch_reason",
                ],
            },
            "assumptions": [
                "The buyer supplies two UTF-8 CSV exports with 25 records each and a shared order_id field.",
                "Status values can be compared as exact text after trimming surrounding whitespace.",
            ],
            "exclusions": [
                "No write-back to either commerce or fulfilment system.",
                "No automatic resolution of mismatches or live synchronisation service.",
            ],
        },
    ]


def write_fixtures(output_dir: str | Path) -> list[Path]:
    """Write the deterministic synthetic problem and evidence JSON files."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for problem in sample_problems():
        path = target / f"{problem['id']}.problem.json"
        path.write_text(json.dumps(problem, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(path)
    evidence_path = target / "capability-evidence.json"
    evidence_path.write_text(
        json.dumps(sample_evidence(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    written.append(evidence_path)
    return written
