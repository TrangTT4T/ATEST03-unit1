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
        qty = self.find_all(*self._quantity)
        if qty:
            qty[0].clear()
            qty[0].send_keys(str(quantity))
            self._submit()
        else:
            # Theme without a quantity box: add the product N times.
            product_url = self.url
            for i in range(quantity):
                if i:
                    self.driver.get(product_url)
                self._submit()

    def _submit(self):
        # Wait for each POST to finish (redirect to /cart) before the next action;
        # without this the next driver.get() can cancel the request (found in the Unit 2 re-check).
        self.submit(*self._add_button)
        self.wait.until(lambda d: "/cart" in d.current_url and "/products/" not in d.current_url)

    # --- Locators -------------------------------------------------------------
    _title = (By.TAG_NAME, "h1")
    # The standard Shopify add-to-cart form
    _add_button = (By.CSS_SELECTOR, "form[action*='/cart/add'] [type='submit']")
    _quantity = (By.CSS_SELECTOR, "form[action*='/cart/add'] input[name='quantity']")
