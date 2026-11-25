"""Layout rules for page objects, checked on every run:  python -m unittest discover -s tests/unit

* one class per file in pages/;
* its locators are declared at the BOTTOM of the class, after the last method;
* methods never write a selector inline (no ``By.`` inside a method).
"""
import ast
import unittest
from pathlib import Path

PAGES = sorted(p for p in (Path(__file__).resolve().parents[2] / "pages").glob("*.py") if p.name != "__init__.py")


def layout_problems(source: str) -> list[str]:
    tree = ast.parse(source)
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    problems = [] if len(classes) == 1 else [f"{len(classes)} classes; a page file holds exactly one"]
    for cls in classes:
        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
        last_method = max((m.end_lineno for m in methods), default=cls.lineno)
        for node in cls.body:
            is_locator = isinstance(node, ast.Assign) and all(
                isinstance(t, ast.Name) and t.id.startswith("_") for t in node.targets
            )
            if is_locator and node.lineno < last_method:
                problems.append(f"line {node.lineno}: locator above a method; move it to the bottom")
        for method in methods:
            for node in ast.walk(method):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "By":
                    problems.append(f"line {node.lineno}: selector written inline in {cls.name}.{method.name}")
    return problems


class PageObjectLayout(unittest.TestCase):
    def test_every_page_file(self):
        self.assertTrue(PAGES)
        for path in PAGES:
            with self.subTest(path.name):
                self.assertEqual(layout_problems(path.read_text(encoding="utf-8")), [])

    def test_the_rule_catches_violations(self):
        sample = (
            "class A:\n"
            "    _title = (By.TAG_NAME, 'h1')\n"  # 2: above a method
            "    def read(self):\n"
            "        return self.find(By.ID, 'x')\n"  # 4: inline selector
            "class B:\n"  # second class
            "    pass\n"
        )
        problems = layout_problems(sample)
        self.assertEqual(problems[0], "2 classes; a page file holds exactly one")
        self.assertEqual([p.split(":")[0] for p in problems[1:]], ["line 2", "line 4"])


if __name__ == "__main__":
    unittest.main()
