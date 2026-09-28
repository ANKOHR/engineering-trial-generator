# Trial definition: Manual order syncing between two systems

> Fictional synthetic fixture example. This tool is a scoping aid, not a guarantee of outcomes. The demo claims no real engagements.

**Fixture status:** SYNTHETIC
**Scope status:** evidence-backed scope

## Problem

A shop manually compares two order exports and needs a concise review list of records that differ.

## Evidence limit

Evidence pointers are supplied by the input and are not independently inspected by this tool.

## Exact artifact to be returned

**Two-export order comparison bundle**. A runnable standard-library comparator and CSV/JSON result files.

Files:
- `matched.csv`
- `mismatches.csv`
- `comparison-summary.json`
- `README.md`

The artifact is limited to the mapped capabilities and listed acceptance criteria.

## Claim-to-evidence mapping

Coverage: 2 mapped, 0 flagged unsupported.

### Coverage table

| Claim | Status | Project | Evidence pointers |
| --- | --- | --- | --- |
| compare order records across two exports | MAPPED | Synthetic Order Pair Diff | `synthetic://order-pair-diff/src/compare.py`, `synthetic://order-pair-diff/tests/test_compare.py#10-cases` |
| produce a reviewable mismatch report | MAPPED | Synthetic Order Pair Diff | `synthetic://order-pair-diff/src/report.py`, `synthetic://order-pair-diff/tests/test_report.py#5-cases`, `synthetic://order-pair-diff/demo/index.html` |

### Mapped claims

- **compare order records across two exports** maps to **Synthetic Order Pair Diff**.
  - Evidence pointer: `synthetic://order-pair-diff/src/compare.py`
  - Evidence pointer: `synthetic://order-pair-diff/tests/test_compare.py#10-cases`
- **produce a reviewable mismatch report** maps to **Synthetic Order Pair Diff**.
  - Evidence pointer: `synthetic://order-pair-diff/src/report.py`
  - Evidence pointer: `synthetic://order-pair-diff/tests/test_report.py#5-cases`
  - Evidence pointer: `synthetic://order-pair-diff/demo/index.html`

### Unsupported claims

- None.

## Acceptance criteria

### AC-01

- Condition: comparison-summary.json reports exactly 25 left records, 25 right records, 22 matched records, and 3 mismatched records.
- Owner: Buyer
- Verification method: Parse comparison-summary.json and compare each count with the 4 specified values.

### AC-02

- Condition: mismatches.csv contains exactly 3 data rows and the columns order_id, left_status, right_status, mismatch_reason.
- Owner: Buyer
- Verification method: Count mismatches.csv rows and compare its header with the 4 required column names.

### AC-03

- Condition: matched.csv contains exactly 22 data rows, with one row per matching order_id.
- Owner: Buyer
- Verification method: Count matched.csv data rows and verify that order_id values are unique.

## Assumptions

- The buyer supplies two UTF-8 CSV exports with 25 records each and a shared order_id field.
- Status values can be compared as exact text after trimming surrounding whitespace.

## Exclusions

- No write-back to either commerce or fulfilment system.
- No automatic resolution of mismatches or live synchronisation service.

## Commercial terms

- Fixed price: **GBP 1,125**
- Time box: **1 day**
- Pricing rule: GBP 750 per day plus GBP 125 per acceptance criterion; day count follows the documented scope threshold.
