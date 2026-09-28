# Engineering Trial Generator

Engineering Trial Generator turns a described business problem and a capability evidence catalogue into a small, checkable paid trial definition. It writes a Markdown proposal appendix and a JSON record with the artifact, acceptance criteria, assumptions, exclusions, fixed price, time box, and claim coverage.

Every in-scope capability claim must exactly match a capability recorded for an existing project and that capability must include at least one evidence pointer. Unsupported claims stay visible and are excluded from the promised scope.

## Quickstart

The project uses Python 3.10 or later and the standard library. Pytest is needed only to run the test suite. No model, network access, GPU package, or external download is used.

```powershell
python -m engineering_trial_generator fixtures --out .\fixtures
python -m engineering_trial_generator generate `
  --problem .\fixtures\invoice-reconciliation.problem.json `
  --evidence .\fixtures\capability-evidence.json `
  --out .\trial-definitions
python -m engineering_trial_generator check --trial .\trial-definitions\invoice-reconciliation.json
python -m engineering_trial_generator report --out .\trial-definitions\demo
```

To use the installed command name, install this local project with `python -m pip install -e .`, then replace `python -m engineering_trial_generator` with `engineering-trial-generator`. Inputs can be UTF-8 JSON or plain text problem files. JSON allows explicit `required_claims`, an `acceptance_profile` for generated criteria, optional explicit `acceptance_checks`, assumptions, exclusions, and an artifact specification. The sample profiles supply measurable counts and fields; the generator turns those facts into criteria with an owner and verification method. Without a known profile or explicit checks, criteria are generated from the artifact and claim scope. Plain text uses conservative keyword inference for the three known example domains. Other plain text receives one generic claim, which remains unsupported unless the evidence catalogue has that exact claim.

The `fixtures` command writes three `*.problem.json` files and one `capability-evidence.json` file. `generate` writes `<problem-id>.md` and `<problem-id>.json`. `check` takes a JSON trial definition and returns exit code 1 when it finds violations. `report` writes all three sample trial pairs and `index.md` with a mapped-versus-unsupported claim summary.

## Architecture

```text
Problem JSON or text                 Capability evidence JSON
          |                                      |
          v                                      v
     problem parser                         evidence loader
          \                                      /
           \                                    /
            v                                  v
             exact normalized claim mapper
                 |                    |
          mapped with pointers    unsupported list
                 \                    /
                  v                  v
                  trial definition builder
                    |              |
                    v              v
               Markdown          JSON
                                   |
                                   v
                     acceptance-criteria checker

fixtures --> synthetic inputs
report ----> three fixture runs plus coverage index
```

The mapper lowercases claims, removes punctuation, and collapses whitespace. It accepts exact normalized matches only, then uses the first matching project in evidence-file order. It does not infer support from a project description, a similar phrase, or a demo label. Each match carries the project name and every pointer listed beside that capability. Claims without a match appear under **Unsupported claims** and are appended to the exclusions. If a problem has no supported claims, the generated scope is a readiness note, not implementation of the unsupported capability.

The checker reads the structured JSON trial. Every acceptance criterion needs a non-empty condition, a named owner, and a verification method with a concrete action. Conditions need a number, threshold, exact value, or explicit rule such as `each` or `every`. Vague phrases such as `high quality`, `robust`, or `easy to use` produce findings, even when the criterion has other fields.

## HONESTY BOUNDARY

All sample problems, project names, evidence pointers, test counts, demo URLs, sample inputs, and expected results are fictional synthetic fixtures. They are not real clients, projects, deployments, or trial results. The fixture generator and report label that material as synthetic. Synthetic pointers use the `synthetic://` scheme and do not link to external services. For user-provided evidence, the tool checks that a pointer string is present but does not independently inspect its target or verify the underlying project.

This tool is a scoping aid that helps write checkable trial definitions. It is not a guarantee of outcomes. Its demo claims no real engagements. For user-provided inputs, the output repeats the scoping limitation and requires the parties to confirm scope and evidence before relying on the proposal.

## Fixture catalogue

| Problem | Required capability claims | Fictional project evidence |
| --- | --- | --- |
| Invoice reconciliation errors | Parse invoice CSV rows; compare totals and flag mismatches | Synthetic Ledger Linter, source pointers and named test-case counts |
| Support documents nobody trusts | Extract sections and citations; validate links and required sections | Synthetic Doc Trust Checker, source pointers and named test-case counts |
| Manual order syncing | Compare two order exports; produce a mismatch report | Synthetic Order Pair Diff, source pointers and named test-case counts |

The evidence file contains three invented projects. Every pointer is marked with `synthetic://`; the displayed test counts and demo pages are fictional metadata. Expected row counts in the sample acceptance criteria describe fixed synthetic test inputs, not observed customer outcomes.

## Claim-to-evidence mapping

Problem JSON can list `required_claims` as strings. Evidence JSON contains `projects`, each with a `name` and `capabilities`; every capability has a `claim` and a non-empty `evidence_pointers` list. A capability without a pointer cannot support a claim. Matching is deterministic and exact after normalization, which prevents the tool from turning related wording into invented proof. A claim with no match is included in the flagged unsupported list, counted in the coverage summary, and excluded from implementation promises. The mapper does not fetch or inspect pointer targets, so the evidence catalogue owner remains responsible for confirming that each pointer supports its claim.

Example evidence entry:

```json
{
  "name": "Synthetic Ledger Linter",
  "capabilities": [
    {
      "claim": "parse invoice CSV rows",
      "evidence_pointers": [
        "synthetic://ledger-linter/src/csv_reader.py",
        "synthetic://ledger-linter/tests/test_csv_reader.py#6-cases"
      ]
    }
  ]
}
```

## Pricing rule

The fixed price is `GBP 750 per day + GBP 125 per acceptance criterion`. A trial is one day when it has at most three criteria and at most two mapped claims. More than three criteria or more than two mapped claims makes it a two-day trial. Unsupported claims are excluded and do not increase the price. The rule is deterministic and shown in every trial definition. It is a starter pricing convention, not a market estimate.

No randomness is used, so there is no random seed. JSON key order, UTF-8 encoding, Markdown rendering, and file naming are stable. Output contains no timestamps. Repeating a command with the same input bytes produces byte-identical Markdown and JSON.

## Development

```powershell
python -m pytest
```
