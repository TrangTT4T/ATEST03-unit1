"""Traceability: the matrix logic, and the tags in the real feature files.

    python -m unittest discover -s tests/unit
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from helper_utility.traceability import (  # noqa: E402
    Requirement,
    ScenarioResult,
    build_matrix,
    load_requirements,
    to_csv,
    to_markdown,
    untraced,
)

REQS = {
    "add_to_cart": Requirement("add_to_cart", "REQ-01", "Cart", "R01", "Critical"),
    "secure_login": Requirement("secure_login", "REQ-02", "Login", "R02", "High"),
    "search_products": Requirement("search_products", "REQ-03", "Search", "R03", "Medium"),
    "create_account": Requirement("create_account", "REQ-04", "Account", "R04", "Medium"),
}


def result(name, status, *tags):
    return ScenarioResult("x.feature", name, frozenset(tags), status)


class Matrix(unittest.TestCase):
    def test_the_worst_scenario_decides(self):
        rows = build_matrix(REQS, [
            result("a", "passed", "add_to_cart"), result("b", "failed", "add_to_cart"),       # -> FAIL
            result("c", "passed", "secure_login"), result("d", "skipped", "secure_login"),    # -> PASS
            result("e", "skipped", "search_products", "data-creating"),                       # -> NOT RUN
        ])                                                                                     # create_account: NO TEST
        self.assertEqual([r.status for r in rows], ["FAIL", "PASS", "NOT RUN", "NO TEST"])

    def test_a_hook_error_is_a_failure(self):
        rows = build_matrix(REQS, [result("a", "hook_error", "add_to_cart")])
        self.assertEqual(rows[0].status, "FAIL")

    def test_rows_follow_the_requirement_ids_and_other_tags_are_ignored(self):
        rows = build_matrix(REQS, [result("a", "passed", "cart", "smoke", "add_to_cart")])
        self.assertEqual([r.requirement.id for r in rows], ["REQ-01", "REQ-02", "REQ-03", "REQ-04"])
        self.assertEqual(len(rows[0].results), 1)

    def test_reports(self):
        results = [result("a", "passed", "add_to_cart"), result("orphan", "passed", "smoke")]
        rows = build_matrix(REQS, results)
        self.assertEqual([r.name for r in untraced(REQS, results)], ["orphan"])
        markdown = to_markdown(rows, untraced(REQS, results))
        self.assertIn("| REQ-01 | @add_to_cart | Cart | R01 | Critical | 1 | 1 | 0 | 0 | PASS |", markdown)
        self.assertIn("## Scenarios without a requirement tag", markdown)
        self.assertEqual(to_csv(rows).splitlines()[1], "REQ-01,@add_to_cart,Cart,R01,Critical,1,1,0,0,PASS")


class FeatureFiles(unittest.TestCase):
    """The real feature files against the real registries (no browser)."""

    def setUp(self):
        from behave.parser import parse_file

        self.requirements = load_requirements(ROOT / "dataset" / "requirements.json")
        groups = json.loads((ROOT / "dataset" / "tags.json").read_text(encoding="utf-8"))
        self.vocabulary = {tag for name, tags in groups.items() if not name.startswith("_") for tag in tags}
        self.features = [parse_file(str(p)) for p in sorted((ROOT / "tests" / "features").glob("*.feature"))]
        self.scenarios = [(Path(f.filename).name, s) for f in self.features for s in f.walk_scenarios()]

    def test_every_scenario_proves_exactly_one_requirement(self):
        for feature, scenario in self.scenarios:
            tags = set(scenario.effective_tags) & self.requirements.keys()
            with self.subTest(f"{feature}: {scenario.name}"):
                self.assertEqual(len(tags), 1, f"tag it with one of {sorted(self.requirements)}")

    def test_every_requirement_has_a_scenario(self):
        covered = {t for _, s in self.scenarios for t in s.effective_tags}
        self.assertEqual(sorted(self.requirements.keys() - covered), [])

    def test_every_tag_is_known(self):
        """A typo such as @add_to_card would otherwise just be an extra tag nobody notices."""
        known = self.vocabulary | self.requirements.keys()
        used = {t for f in self.features for t in f.tags} | {t for _, s in self.scenarios for t in s.effective_tags}
        self.assertEqual(sorted(used - known), [], "add new tags to dataset/tags.json or requirements.json")

    def test_requirement_tags_do_not_clash_with_other_tags(self):
        self.assertEqual(sorted(self.vocabulary & self.requirements.keys()), [])


if __name__ == "__main__":
    unittest.main()
