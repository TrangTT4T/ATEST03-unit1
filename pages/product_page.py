"""Product detail page: /products/<handle>"""
from selenium.webdriver.common.by import By

from .base_page import BasePage


class ProductPage(BasePage):
    def open_product(self, handle: str):
        return self.open(f"/products/{handle}")

    def title(self) -> str:
        return self.find(*self._title).text

    def can_add_to_cart(self) -> bool:
        buttons = self.find_all(*self._add_button)
        if not buttons:
            return False
        button = buttons[0]
        label = (button.get_attribute("value") or button.text or "").lower()
        return button.is_enabled() and "sold out" not in label and "unavailable" not in label

    def add_to_cart(self, quantity: int = 1):
        qty = [box for box in self.find_all(*self._quantity) if box.is_displayed()]
        if qty:
            qty[0].clear()
            qty[0].send_keys(str(quantity))
            self._add(expected_increase=quantity)
            return
        # Theme without a visible quantity box: add the product N times.
        product_url = self.url
        for _ in range(quantity):
            if "/products/" not in self.url:  # a non-AJAX theme moved to /cart after the last add
                self.driver.get(product_url)
            self._add(expected_increase=1)

    def _add(self, expected_increase: int):
        """Click Add to Cart and wait until the store has taken the product.

        The live theme adds with AJAX: jQuery posts /cart/add.js, updates the header and the page
        stays (Day 4 finding F11). Without JavaScript the form posts and the browser lands on /cart
        (finding F7). Wait for whichever happens - never for time, and never only for a navigation
        that an AJAX theme does not make.
        """
        before = self.mini_cart_count()
        self.click(*self._add_button)
        self.wait.until(
            lambda d: ("/cart" in d.current_url and "/products/" not in d.current_url)
            or (self.mini_cart_count_now() or 0) >= before + expected_increase
        )

    # --- Locators -------------------------------------------------------------
    _title = (By.TAG_NAME, "h1")
    # The standard Shopify add-to-cart form
    _add_button = (By.CSS_SELECTOR, "form[action*='/cart/add'] [type='submit']")
    _quantity = (By.CSS_SELECTOR, "form[action*='/cart/add'] input[name='quantity']")
