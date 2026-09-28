"""Generate the three synthetic demo trials and their coverage index."""

from __future__ import annotations

from pathlib import Path

from .fixtures import sample_evidence, sample_problems
from .generator import build_trial, write_trial


def create_report(output_dir: str | Path) -> tuple[list[Path], Path]:
    """Write three trial pairs and a plainly labelled synthetic demo index."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    evidence = sample_evidence()
    written: list[Path] = []
    summaries: list[str] = []
    for problem in sample_problems():
        trial = build_trial(problem, evidence)
        markdown_path, json_path = write_trial(trial, target)
        written.extend([markdown_path, json_path])
        coverage = trial["claim_coverage"]
        summaries.append(
            f"| [{trial['title']}]({markdown_path.name}) | {coverage['mapped_count']} | {coverage['unsupported_count']} | [{json_path.name}]({json_path.name}) |"
        )
    index = target / "index.md"
    index.write_text(
        "\n".join(
            [
                "# Engineering Trial Generator demo index",
                "",
                "> All sample problems, projects, pointers, and results on this page are fictional synthetic fixtures. This tool is a scoping aid, not a guarantee of outcomes. The demo claims no real engagements.",
                "",
                "| Trial | Mapped claims | Flagged unsupported | JSON definition |",
                "| --- | ---: | ---: | --- |",
                *summaries,
                "",
            ]
        ),
        encoding="utf-8",
    )
    written.append(index)
    return written, index
