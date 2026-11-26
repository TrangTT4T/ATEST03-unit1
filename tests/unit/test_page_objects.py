"""Layout rules for page objects, checked on every run:  python -m unittest discover -s tests/unit

* one class per file in pages/, and NOTHING outside it: only the docstring, imports and that class
  (a helper function or constant at module level belongs inside the class, e.g. BasePage.money_to_float);
* its methods are grouped under ``####`` banners, each naming its area with ``# Scope: ...``;
* every public method has a docstring;
* its locators are declared at the BOTTOM of the class, after the last method, as locator STRINGS
  ("css=...", "xpath=...", "name=..."), never ``(By, value)`` tuples;
* only base_page.py (parse_locator, the driver calls) uses ``By``, ``driver.find_element`` or
  ``WebDriverWait``: every other page uses the BasePage methods (find_element, click_element ...).
"""
import ast
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pages import BasePage  # noqa: E402

PAGES = sorted(p for p in (ROOT / "pages").glob("*.py") if p.name != "__init__.py")
BANNER = re.compile(r"^\s*#{20,}\n\s*# .+\n\s*# Scope: .+\n\s*#{20,}$", re.MULTILINE)
DRIVER_CALLS = re.compile(r"driver\.find_elements?\(|WebDriverWait\(")


def layout_problems(source: str, is_base_page: bool = False) -> list[str]:
    tree = ast.parse(source)
    lines = source.splitlines()
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    problems = [] if len(classes) == 1 else [f"{len(classes)} classes; a page file holds exactly one"]
    for node in tree.body:
        is_docstring = isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
        if not (is_docstring or isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef))):
            problems.append(f"line {node.lineno}: code outside the class; put it inside the page class")
    if not is_base_page:
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "By":
                problems.append(f"line {node.lineno}: By used in a page; write a locator string such as 'css=...'")
        for number, line in enumerate(lines, 1):
            if DRIVER_CALLS.search(line):
                problems.append(f"line {number}: driver call in a page; use the BasePage methods")
    for cls in classes:
        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
        if methods and not BANNER.search("\n".join(lines[cls.lineno - 1:cls.end_lineno])):
            problems.append(f"{cls.name}: no '####' banner with '# Scope: ...' above its methods")
        for method in methods:
            if not method.name.startswith("_") and ast.get_docstring(method) is None:
                problems.append(f"line {method.lineno}: {cls.name}.{method.name} has no docstring")
        last_method = max((m.end_lineno for m in methods), default=cls.lineno)
        for node in cls.body:
            is_locator = isinstance(node, ast.Assign) and all(
                isinstance(t, ast.Name) and t.id.startswith("_") for t in node.targets
            )
            if not is_locator:
                continue
            if node.lineno < last_method:
                problems.append(f"line {node.lineno}: locator above a method; move it to the bottom")
            if not (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
                problems.append(f"line {node.lineno}: a locator is a string such as 'css=...', not a tuple")
            else:
                try:
                    BasePage.parse_locator(node.value.value)
                except ValueError as error:
                    problems.append(f"line {node.lineno}: {error}")
    return problems


class PageObjectLayout(unittest.TestCase):
    def test_every_page_file(self):
        self.assertTrue(PAGES)
        for path in PAGES:
            with self.subTest(path.name):
                source = path.read_text(encoding="utf-8")
                self.assertEqual(layout_problems(source, is_base_page=path.name == "base_page.py"), [])

    def test_the_rule_catches_violations(self):
        sample = (
            "class A:\n"
            "    _title = (By.TAG_NAME, 'h1')\n"  # 2: above a method, a tuple, uses By
            "    def read(self):\n"  # 3: no docstring; no banner in the class
            "        return self.driver.find_element(By.ID, 'x')\n"  # 4: driver call, By
            "class B:\n"  # second class
            "    pass\n"
            "def money_to_float(text):\n"  # 7: a helper outside the class
            "    return 1.0\n"
            "TOTAL = 1\n"  # 9: a constant outside the class
        )
        self.assertEqual(layout_problems(sample), [
            "2 classes; a page file holds exactly one",
            "line 7: code outside the class; put it inside the page class",
            "line 9: code outside the class; put it inside the page class",
            "line 2: By used in a page; write a locator string such as 'css=...'",
            "line 4: By used in a page; write a locator string such as 'css=...'",
            "line 4: driver call in a page; use the BasePage methods",
            "A: no '####' banner with '# Scope: ...' above its methods",
            "line 3: A.read has no docstring",
            "line 2: locator above a method; move it to the bottom",
            "line 2: a locator is a string such as 'css=...', not a tuple",
        ])

    def test_the_expected_layout_passes(self):
        sample = (
            "class A(BasePage):\n"
            "    ######################################################\n"
            "    # Header methods\n"
            "    # Scope: Every page > Header\n"
            "    ######################################################\n"
            "    def title(self):\n"
            "        \"\"\"The page title.\"\"\"\n"
            "        return self.get_text(self._title)\n"
            "\n"
            "    # --- Locators ---\n"
            "    _title = \"css=[itemprop='name']\"\n"
        )
        self.assertEqual(layout_problems(sample), [])


if __name__ == "__main__":
    unittest.main()
