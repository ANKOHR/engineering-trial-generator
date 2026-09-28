# Trial definition: Invoice reconciliation errors

> Fictional synthetic fixture example. This tool is a scoping aid, not a guarantee of outcomes. The demo claims no real engagements.

**Fixture status:** SYNTHETIC
**Scope status:** evidence-backed scope

## Problem

A small finance team manually compares invoice exports and spends time finding total mismatches.

## Evidence limit

Evidence pointers are supplied by the input and are not independently inspected by this tool.

## Exact artifact to be returned

**Invoice reconciliation validator**. A runnable standard-library Python script with CSV input and output.

Files:
- `reconciled.csv`
- `exceptions.csv`
- `README.md`

The artifact is limited to the mapped capabilities and listed acceptance criteria.

## Claim-to-evidence mapping

Coverage: 2 mapped, 0 flagged unsupported.

### Coverage table

| Claim | Status | Project | Evidence pointers |
| --- | --- | --- | --- |
| parse invoice CSV rows | MAPPED | Synthetic Ledger Linter | `synthetic://ledger-linter/src/csv_reader.py`, `synthetic://ledger-linter/tests/test_csv_reader.py#6-cases`, `synthetic://ledger-linter/demo/index.html` |
| compare invoice totals and flag mismatches | MAPPED | Synthetic Ledger Linter | `synthetic://ledger-linter/src/reconcile.py`, `synthetic://ledger-linter/tests/test_reconcile.py#8-cases` |

### Mapped claims

- **parse invoice CSV rows** maps to **Synthetic Ledger Linter**.
  - Evidence pointer: `synthetic://ledger-linter/src/csv_reader.py`
  - Evidence pointer: `synthetic://ledger-linter/tests/test_csv_reader.py#6-cases`
  - Evidence pointer: `synthetic://ledger-linter/demo/index.html`
- **compare invoice totals and flag mismatches** maps to **Synthetic Ledger Linter**.
  - Evidence pointer: `synthetic://ledger-linter/src/reconcile.py`
  - Evidence pointer: `synthetic://ledger-linter/tests/test_reconcile.py#8-cases`

### Unsupported claims

- None.

## Acceptance criteria

### AC-01

- Condition: The output directory contains exactly 3 files: reconciled.csv, exceptions.csv, README.md.
- Owner: Buyer
- Verification method: List the output directory and compare the filenames with the required set.

### AC-02

- Condition: Given the 10-row synthetic invoice input, reconciled.csv contains 8 matching rows and exceptions.csv contains 2 mismatch rows.
- Owner: Buyer
- Verification method: Run the script on the supplied synthetic CSV, then count data rows in both output CSV files.

### AC-03

- Condition: Each exceptions.csv row includes invoice_id, expected_total, observed_total, difference columns.
- Owner: Buyer
- Verification method: Open exceptions.csv and compare its header row with the 4 required column names.

## Assumptions

- The buyer supplies one UTF-8 CSV with invoice_id, expected_total, and observed_total columns.
- Currency values use decimal notation with a period separator.

## Exclusions

- No connection to accounting software or live financial data.
- No tax, foreign exchange, or accounting policy advice.

## Commercial terms

- Fixed price: **GBP 1,125**
- Time box: **1 day**
- Pricing rule: GBP 750 per day plus GBP 125 per acceptance criterion; day count follows the documented scope threshold.
