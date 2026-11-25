"""Requirement traceability, built from requirement tags and the outcome of every scenario.

A requirement tag names WHAT the scenario proves (@add_to_cart, @secure_login ...). The registry
(dataset/requirements.json) maps each tag to its Day 1 id (REQ-01 ...), title and risk; any tag that
is a registry key is a requirement tag.

Pure logic (no behave, no browser), so it is unit-tested; tests/environment.py records each
scenario in ``after_scenario`` and writes the matrix in ``after_all``:

    reports/traceability.md    for people (trainer, BA, PO): one row per requirement
    reports/traceability.csv   for tools and spreadsheets

A requirement's status is decided by its worst scenario:
    FAIL      at least one scenario failed (or its hooks failed)
    PASS      every scenario that ran passed
    NOT RUN   it has scenarios, but none ran (skipped by tags: @manual, @wip, @data-creating)
    NO TEST   no scenario carries its tag - a coverage gap
"""
import csv
import io
import json
from dataclasses import dataclass, field
from pathlib import Path

FAILED = {"failed", "error", "hook_error"}


@dataclass(frozen=True)
class Requirement:
    tag: str  # add_to_cart
    id: str  # REQ-01
    title: str
    risk: str
    level: str


@dataclass(frozen=True)
class ScenarioResult:
    feature: str
    name: str
    tags: frozenset
    status: str  # behave's Status name: passed, failed, skipped, untested, hook_error ...


@dataclass
class Row:
    requirement: Requirement
    results: list = field(default_factory=list)

    def count(self, *statuses: str) -> int:
        return sum(1 for r in self.results if r.status in statuses)

    @property
    def status(self) -> str:
        if not self.results:
            return "NO TEST"
        if self.count(*FAILED):
            return "FAIL"
        if self.count("passed"):
            return "PASS"
        return "NOT RUN"


def load_requirements(path: Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))["requirements"]
    return {tag: Requirement(tag, r["id"], r["title"], r["risk"], r["level"]) for tag, r in data.items()}


def build_matrix(requirements: dict, results: list) -> list:
    """One row per registered requirement (in id order), with the scenarios tagged with it."""
    rows = {tag: Row(req) for tag, req in requirements.items()}
    for result in results:
        for tag in sorted(result.tags & rows.keys()):
            rows[tag].results.append(result)
    return sorted(rows.values(), key=lambda row: row.requirement.id)


def untraced(requirements: dict, results: list) -> list:
    """Scenarios without a requirement tag: they test something nobody asked for, or the tag is missing."""
    return [r for r in results if not r.tags & requirements.keys()]


HEADER = ["Requirement", "Tag", "Title", "Risk", "Level", "Scenarios", "Passed", "Failed", "Not run", "Status"]


def _cells(row: Row) -> list:
    req = row.requirement
    return [req.id, f"@{req.tag}", req.title, req.risk, req.level, len(row.results), row.count("passed"),
            row.count(*FAILED), len(row.results) - row.count("passed") - row.count(*FAILED), row.status]


def to_markdown(rows: list, extra: list) -> str:
    lines = ["# Requirement traceability", "",
             "| " + " | ".join(HEADER) + " |", "|" + "---|" * len(HEADER)]
    lines += ["| " + " | ".join(str(c) for c in _cells(row)) + " |" for row in rows]
    lines += ["", "## Scenarios per requirement", ""]
    for row in rows:
        lines.append(f"- **{row.requirement.id}** `@{row.requirement.tag}` {row.requirement.title}: {row.status}")
        lines += [f"  - `{r.status}` {r.feature}: {r.name}" for r in row.results]
    if extra:
        lines += ["", "## Scenarios without a requirement tag", ""]
        lines += [f"- `{r.status}` {r.feature}: {r.name}" for r in extra]
    return "\n".join(lines) + "\n"


def to_csv(rows: list) -> str:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(HEADER)
    writer.writerows(_cells(row) for row in rows)
    return out.getvalue()


def write_reports(requirements_file: Path, results: list, folder: Path) -> list:
    requirements = load_requirements(requirements_file)
    rows = build_matrix(requirements, results)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "traceability.md").write_text(to_markdown(rows, untraced(requirements, results)), encoding="utf-8")
    (folder / "traceability.csv").write_text(to_csv(rows), encoding="utf-8")
    return rows
