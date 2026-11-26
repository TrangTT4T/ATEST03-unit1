"""The Day 4 framework review, automated: every checklist rule that code can check is a test.

    python -m unittest discover -s tests/unit

A rule that only lives in a review document erodes; a rule that fails the run does not. What stays a
human review: whether a scenario is the RIGHT example for its requirement, and naming.
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FEATURES = sorted((ROOT / "tests" / "features").glob("*.feature"))
STEP_FILES = sorted((ROOT / "tests" / "steps").glob("*.py"))
CODE_FILES = [*STEP_FILES, *sorted((ROOT / "pages").glob("*.py")), *sorted((ROOT / "helper_utility").glob("*.py")),
              ROOT / "tests" / "environment.py"]
MAX_STEPS = 7


def _parsed():
    from behave.parser import parse_file

    return [parse_file(str(path)) for path in FEATURES]


class FrameworkReview(unittest.TestCase):
    """The Day 4 checklist: declarative Gherkin, reusable steps, layering, stability."""

    # --- Declarative Gherkin: feature files say WHAT the customer does, never HOW ---------------
    IMPERATIVE = re.compile(r"https?://|\bclicks?\b|\bwaits?\b|\bxpath\b|\bcss\b|\bseconds?\b|#\w|//", re.IGNORECASE)

    def test_no_url_selector_click_or_wait_in_steps(self):
        problems = [
            f"{path.name}:{number}: {line.strip()}"
            for path in FEATURES
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            if re.match(r"\s*(Given|When|Then|And|But)\b", line) and self.IMPERATIVE.search(line)
        ]
        self.assertEqual(problems, [])

    def test_scenarios_stay_short(self):
        too_long = [
            f"{Path(f.filename).name}: {s.name} has {len(list(s.all_steps))} steps"
            for f in _parsed()
            for s in f.walk_scenarios()
            if len(list(s.all_steps)) > MAX_STEPS
        ]
        self.assertEqual(too_long, [], f"at most {MAX_STEPS} steps (background included)")

    # --- Step definitions: defined once, used, and talking only to page objects ----------------
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as folder:
            usage = Path(folder, "usage.txt")
            subprocess.run(
                [sys.executable, "-m", "behave", "--dry-run", "--no-junit", "--no-summary",
                 "--tags", "not @nothing", "-f", "steps.usage", "-o", str(usage)],
                cwd=ROOT, check=False, capture_output=True, text=True,
            )
            cls.usage = usage.read_text(encoding="utf-8")

    def test_no_unused_or_undefined_steps(self):
        self.assertIn("@given(", self.usage, "behave's steps.usage report is empty")
        problems = self.usage[self.usage.find("UNUSED STEP"):] if "UNUSED STEP" in self.usage else ""
        problems += self.usage[self.usage.find("UNDEFINED STEPS"):] if "UNDEFINED STEPS" in self.usage else ""
        self.assertEqual(problems, "", f"\n{problems}")

    def test_no_near_duplicate_step_texts(self):
        """Same sentence up to parameters and plural s (Day 4 finding F1: 'item' / 'items')."""
        texts = re.findall(r"@(?:given|when|then|step)\(\s*r?['\"](.+?)['\"]\s*[,)]", "".join(
            p.read_text(encoding="utf-8") for p in STEP_FILES))
        normalised = [
            re.sub(r"s\b", "", re.sub(r"\{[^}]*\}|\(\?P<\w+>[^)]*\)|\"", "X", t).replace("s?", "").lower())
            for t in texts
        ]
        duplicates = sorted({n for n in normalised if normalised.count(n) > 1})
        self.assertEqual(duplicates, [])

    def test_steps_use_page_objects_not_selenium(self):
        offenders = [
            f"{path.name}:{number}"
            for path in STEP_FILES
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            if re.search(r"context\.driver|\bBy\.|find_elements?\(|from selenium", line)
        ]
        self.assertEqual(offenders, [], "locators and driver calls belong in pages/")

    def test_no_prices_in_step_code(self):
        offenders = [p.name for p in STEP_FILES if re.search(r"£\s?\d", p.read_text(encoding="utf-8"))]
        self.assertEqual(offenders, [], "prices come from the feature file or dataset/products.json")

    # --- Stability -------------------------------------------------------------------------------
    def test_no_fixed_waits(self):
        offenders = [p.name for p in CODE_FILES if re.search(r"\bsleep\(", p.read_text(encoding="utf-8"))]
        self.assertEqual(offenders, [], "wait for a state (WebDriverWait), never for time")


if __name__ == "__main__":
    unittest.main()
