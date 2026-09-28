# Trial definition: Support documents nobody trusts

> Fictional synthetic fixture example. This tool is a scoping aid, not a guarantee of outcomes. The demo claims no real engagements.

**Fixture status:** SYNTHETIC
**Scope status:** evidence-backed scope

## Problem

A support team wants a repeatable way to inspect a fixed set of help documents for broken links and missing required sections.

## Evidence limit

Evidence pointers are supplied by the input and are not independently inspected by this tool.

## Exact artifact to be returned

**Support documentation audit bundle**. A runnable standard-library checker and three CSV result files.

Files:
- `source-map.csv`
- `link-results.csv`
- `issues.csv`
- `README.md`

The artifact is limited to the mapped capabilities and listed acceptance criteria.

## Claim-to-evidence mapping

Coverage: 2 mapped, 0 flagged unsupported.

### Coverage table

| Claim | Status | Project | Evidence pointers |
| --- | --- | --- | --- |
| extract document sections and citations | MAPPED | Synthetic Doc Trust Checker | `synthetic://doc-trust/src/section_index.py`, `synthetic://doc-trust/tests/test_section_index.py#7-cases` |
| validate links and required sections | MAPPED | Synthetic Doc Trust Checker | `synthetic://doc-trust/src/doc_checks.py`, `synthetic://doc-trust/tests/test_doc_checks.py#9-cases`, `synthetic://doc-trust/demo/index.html` |

### Mapped claims

- **extract document sections and citations** maps to **Synthetic Doc Trust Checker**.
  - Evidence pointer: `synthetic://doc-trust/src/section_index.py`
  - Evidence pointer: `synthetic://doc-trust/tests/test_section_index.py#7-cases`
- **validate links and required sections** maps to **Synthetic Doc Trust Checker**.
  - Evidence pointer: `synthetic://doc-trust/src/doc_checks.py`
  - Evidence pointer: `synthetic://doc-trust/tests/test_doc_checks.py#9-cases`
  - Evidence pointer: `synthetic://doc-trust/demo/index.html`

### Unsupported claims

- None.

## Acceptance criteria

### AC-01

- Condition: source-map.csv contains exactly 12 data rows, each with non-empty source_id, section_heading, citation_locator values.
- Owner: Buyer
- Verification method: Count source-map.csv rows and inspect the 3 required columns for blank cells.

### AC-02

- Condition: link-results.csv contains exactly 12 data rows: 10 PASS and 2 FAIL status values.
- Owner: Buyer
- Verification method: Count data rows and compare the status column values with the required totals.

### AC-03

- Condition: issues.csv contains exactly 4 data rows: 2 broken-link findings and 2 missing-section findings.
- Owner: Buyer
- Verification method: Count issues.csv rows and group finding_type values into the 2 required categories.

## Assumptions

- The buyer supplies a frozen bundle of 12 UTF-8 help documents and a required-section list.
- The trial checks local copies and does not crawl or change a live help centre.

## Exclusions

- No rewrite or factual review of support content.
- No live website monitoring or content-management integration.

## Commercial terms

- Fixed price: **GBP 1,125**
- Time box: **1 day**
- Pricing rule: GBP 750 per day plus GBP 125 per acceptance criterion; day count follows the documented scope threshold.
