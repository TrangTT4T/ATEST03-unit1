"""Tags in the real feature files: every scenario proves exactly one requirement, no typos.

    python -m unittest discover -s tests/unit
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str) -> dict:
    return json.loads((ROOT / "dataset" / name).read_text(encoding="utf-8"))


class FeatureTags(unittest.TestCase):
    def setUp(self):
        from behave.parser import parse_file

        self.requirements = _load("requirements.json")["requirements"]  # tag -> REQ id, title, risk
        groups = _load("tags.json")
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
