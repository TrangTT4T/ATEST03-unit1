"""Cart page: /cart"""
import re

from selenium.webdriver.common.by import By

from .base_page import BasePage, money_to_float

TOTAL = re.compile(r"(sub)?total[^£]{0,40}£\s?([\d,]+\.\d{2})", re.IGNORECASE)  # a text pattern, not a locator


class CartPage(BasePage):
    path = "/cart"

    def quantity_inputs(self):
        return self.find_all(*self._quantity_inputs)

    def total_quantity(self) -> int:
        return sum(int(i.get_attribute("value") or 0) for i in self.quantity_inputs())

    def is_empty(self) -> bool:
        return not self.quantity_inputs()

    def line_input(self, product_name: str):
        # The quantity box in the same cart row as the product link.
        return self.find(*self.locator(self._line_quantity, name=product_name))

    def set_quantity(self, product_name: str, quantity: int):
        # Setting a line to 0 and updating removes it (standard Shopify behaviour).
        box = self.line_input(product_name)
        box.clear()
        box.send_keys(str(quantity))
        self.submit(*self._update_button)

    def remove(self, product_name: str):
        self.set_quantity(product_name, 0)

    def total(self) -> float:
        match = TOTAL.search(self.body_text())
        if match:
            return float(match.group(2).replace(",", ""))
        form = self.find(*self._cart_form)
        amounts = re.findall(r"£\s?[\d,]+\.\d{2}", form.text)
        return money_to_float(amounts[-1])

    def checkout(self):
        self.submit(*self._checkout_button)

    # --- Locators -------------------------------------------------------------
    _cart_form = (By.CSS_SELECTOR, "form[action*='/cart']")
    _quantity_inputs = (By.CSS_SELECTOR, "input[name^='updates']")
    _line_quantity = (
        By.XPATH,
        "//a[normalize-space()='{name}']"
        "/ancestor::*[.//input[starts-with(@name,'updates')]][1]"
        "//input[starts-with(@name,'updates')]",
    )
    _update_button = (By.CSS_SELECTOR, "[name='update']")
    _checkout_button = (By.CSS_SELECTOR, "[name='checkout']")
