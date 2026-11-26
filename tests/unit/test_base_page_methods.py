"""The custom BasePage methods (click_element, type_text, is_element_enabled, element_should_...),
with a fake WebDriver: no browser. Checks what they wait for, return, log and raise."""
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from selenium.common.exceptions import NoSuchElementException, TimeoutException  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402

from pages import BasePage  # noqa: E402


class FakeElement:
    def __init__(self, text="", enabled=True, visible=True):
        self.text, self.enabled, self.visible = text, enabled, visible
        self.typed, self.clicks, self.cleared = [], 0, False

    def is_displayed(self):
        return self.visible

    def is_enabled(self):
        return self.enabled

    def click(self):
        self.clicks += 1

    def clear(self):
        self.cleared = True

    def send_keys(self, text):
        self.typed.append(text)

    def get_attribute(self, name):
        return f"{name}-value"


class FakeDriver:
    current_url = "https://shop.test/"

    def __init__(self, elements):
        self.elements = elements  # {(By, value): FakeElement}
        self.lookups = []

    def find_element(self, by, value):
        self.lookups.append((by, value))
        if (by, value) not in self.elements:
            raise NoSuchElementException(value)
        return self.elements[(by, value)]

    def find_elements(self, by, value):
        return [self.elements[(by, value)]] if (by, value) in self.elements else []


def page_with(elements, timeout=1):
    return BasePage(FakeDriver(elements), "https://shop.test", timeout=timeout)


class LocatorStrings(unittest.TestCase):
    def test_methods_parse_the_locator_string(self):
        button = FakeElement()
        page = page_with({(By.CSS_SELECTOR, "#buy"): button})
        page.click_element("css=#buy")
        self.assertEqual(button.clicks, 1)
        self.assertEqual(page.driver.lookups[-1], (By.CSS_SELECTOR, "#buy"))

    def test_locator_fills_a_template(self):
        self.assertEqual(BasePage.locator("css=a[href*='{url}']", url="/products/grey-jacket"),
                         "css=a[href*='/products/grey-jacket']")


class Actions(unittest.TestCase):
    def test_type_text_clears_then_types(self):
        box = FakeElement()
        page_with({(By.NAME, "q"): box}).type_text("name=q", "jacket")
        self.assertTrue(box.cleared)
        self.assertEqual(box.typed, ["jacket"])

    def test_a_secret_is_never_logged(self):
        box = FakeElement()
        with self.assertLogs("BasePage", "INFO") as log:
            page_with({(By.NAME, "password"): box}).type_text("name=password", "Passw0rd!2026", secret=True)
        self.assertEqual(box.typed, ["Passw0rd!2026"])
        self.assertNotIn("Passw0rd", "\n".join(log.output))
        self.assertIn("***", "\n".join(log.output))

    def test_clicking_a_disabled_element_times_out_naming_the_locator(self):
        page = page_with({(By.ID, "buy"): FakeElement(enabled=False)})
        with self.assertRaises(TimeoutException) as error:
            page.click_element("id=buy", timeout=0)
        self.assertIn("'id=buy' never became clickable", str(error.exception))


class StateChecks(unittest.TestCase):
    def test_is_element_enabled_answers_without_sleeping(self):
        page = page_with({(By.ID, "on"): FakeElement(), (By.ID, "off"): FakeElement(enabled=False)})
        start = time.monotonic()
        self.assertTrue(page.is_element_enabled("id=on"))
        self.assertFalse(page.is_element_enabled("id=off"))
        self.assertFalse(page.is_element_enabled("id=missing"))  # missing: False, not an exception
        self.assertLess(time.monotonic() - start, 0.5)

    def test_is_element_visible(self):
        page = page_with({(By.ID, "shown"): FakeElement(), (By.ID, "hidden"): FakeElement(visible=False)})
        self.assertTrue(page.is_element_visible("id=shown"))
        self.assertFalse(page.is_element_visible("id=hidden"))

    def test_element_should_be_disabled(self):
        page = page_with({(By.ID, "on"): FakeElement(), (By.ID, "off"): FakeElement(enabled=False)})
        page.element_should_be_disabled("id=off")
        with self.assertRaisesRegex(AssertionError, "'id=on' is not disabled"):
            page.element_should_be_disabled("id=on")
        with self.assertRaisesRegex(AssertionError, "^Add to Cart must be disabled$"):
            page.element_should_be_disabled("id=on", "Add to Cart must be disabled")

    def test_element_should_contain_text_reports_the_actual_text(self):
        page = page_with({(By.ID, "total"): FakeElement(text="£50.00")}, timeout=0)
        page.element_should_contain_text("id=total", "£50.00")
        with self.assertRaisesRegex(AssertionError, r"'id=total' shows '£50.00', expected to contain '£55.00'"):
            page.element_should_contain_text("id=total", "£55.00")

    def test_element_should_be_visible_fails_with_an_assertion(self):
        page = page_with({}, timeout=0)
        with self.assertRaisesRegex(AssertionError, "'css=.missing' is not visible"):
            page.element_should_be_visible("css=.missing")


if __name__ == "__main__":
    unittest.main()
