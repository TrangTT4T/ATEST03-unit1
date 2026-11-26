"""Locator strings -> Selenium (By, value): BasePage.parse_locator()."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from selenium.webdriver.common.by import By  # noqa: E402

from pages import BasePage  # noqa: E402


class ParseLocator(unittest.TestCase):
    def test_every_prefix(self):
        cases = {
            "css=#cart": (By.CSS_SELECTOR, "#cart"),
            "xpath=//a[contains(., 'My Cart')]": (By.XPATH, "//a[contains(., 'My Cart')]"),
            "id=cart": (By.ID, "cart"),
            "name=q": (By.NAME, "q"),
            "tag=html": (By.TAG_NAME, "html"),
            "link=Forgot your password?": (By.LINK_TEXT, "Forgot your password?"),
            "partial_link=Forgot": (By.PARTIAL_LINK_TEXT, "Forgot"),
            "class=errors": (By.CLASS_NAME, "errors"),
        }
        for locator, expected in cases.items():
            with self.subTest(locator):
                self.assertEqual(BasePage.parse_locator(locator), expected)

    def test_a_value_may_contain_equals_signs(self):
        self.assertEqual(BasePage.parse_locator("css=input[name='q']"), (By.CSS_SELECTOR, "input[name='q']"))
        self.assertEqual(BasePage.parse_locator("xpath=//input[@name='q']"), (By.XPATH, "//input[@name='q']"))

    def test_no_prefix_means_xpath_or_css(self):
        self.assertEqual(BasePage.parse_locator("//h1"), (By.XPATH, "//h1"))
        self.assertEqual(BasePage.parse_locator("(//a)[1]"), (By.XPATH, "(//a)[1]"))
        self.assertEqual(BasePage.parse_locator("input[name='q']"), (By.CSS_SELECTOR, "input[name='q']"))

    def test_bad_locators_fail_loudly(self):
        for bad in ("", "   ", "css=", ("css", "#cart")):
            with self.subTest(bad), self.assertRaises(ValueError):
                BasePage.parse_locator(bad)


if __name__ == "__main__":
    unittest.main()
