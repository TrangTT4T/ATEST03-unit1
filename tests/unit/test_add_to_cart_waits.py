"""ProductPage.add_to_cart waits for the store, whichever way the theme adds (Day 4 findings F7, F11).

A fake WebDriver (no browser) plays both themes: AJAX (the page stays, the header count rises a few
polls later) and a plain form post (the browser lands on /cart).
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from selenium.common.exceptions import NoSuchElementException, TimeoutException  # noqa: E402

from pages import ProductPage  # noqa: E402


class FakeElement:
    def __init__(self, driver, kind):
        self.driver, self.kind = driver, kind

    @property
    def text(self):
        return f"My Cart ({self.driver.count})" if self.kind == "header" else ""

    def is_displayed(self):
        return True

    def is_enabled(self):
        return True

    def click(self):
        self.driver.clicked()


class FakeDriver:
    def __init__(self, ajax: bool, delay_polls: int = 3, works: bool = True):
        self.ajax, self.delay, self.works = ajax, delay_polls, works
        self.count, self.pending, self.polls = 0, 0, 0
        self.current_url = "https://shop.test/products/grey-jacket"

    def clicked(self):
        if not self.works:
            return
        if self.ajax:
            self.pending += 1
        else:
            self.count += 1
            self.current_url = "https://shop.test/cart"

    def find_element(self, by, value):
        self.polls += 1
        if self.pending and self.polls % self.delay == 0:  # the AJAX answer arrives later
            self.count += self.pending
            self.pending = 0
        if "My Cart" in value:
            return FakeElement(self, "header")
        if "submit" in value:
            return FakeElement(self, "button")
        raise NoSuchElementException(value)

    def find_elements(self, by, value):
        return []  # no visible quantity box: add N times

    def get(self, url):
        self.current_url = url


def product_page(driver):
    return ProductPage(driver, "https://shop.test", timeout=2)


class AddToCartWaits(unittest.TestCase):
    def test_ajax_theme_waits_for_the_header_count(self):
        driver = FakeDriver(ajax=True)
        product_page(driver).add_to_cart(2)
        self.assertEqual(driver.count, 2)
        self.assertIn("/products/", driver.current_url)  # an AJAX add never leaves the page

    def test_form_post_theme_waits_for_the_cart_page_and_comes_back(self):
        driver = FakeDriver(ajax=False)
        product_page(driver).add_to_cart(2)
        self.assertEqual(driver.count, 2)

    def test_an_add_the_store_never_takes_times_out(self):
        with self.assertRaises(TimeoutException):
            product_page(FakeDriver(ajax=True, works=False)).add_to_cart(1)


if __name__ == "__main__":
    unittest.main()
