"""Cart page: /cart"""
import re

from .base_page import BasePage


class CartPage(BasePage):
    path = "/cart"
    TOTAL_PATTERN = re.compile(r"(sub)?total[^£]{0,40}£\s?([\d,]+\.\d{2})", re.IGNORECASE)  # text, not a locator

    ############################################################################
    # Cart line methods
    # Scope: Cart page > Cart table
    ############################################################################
    def quantity_inputs(self) -> list:
        """The quantity box of every cart line (no wait: an empty cart has none)."""
        return self.find_elements(self._quantity_inputs)

    def total_quantity(self) -> int:
        """Sum of the quantity boxes: the number of items in the cart."""
        return sum(int(i.get_attribute("value") or 0) for i in self.quantity_inputs())

    def is_empty(self) -> bool:
        """True when the cart has no lines."""
        return not self.quantity_inputs()

    def set_quantity(self, product_name: str, quantity: int):
        """Type ``quantity`` in the line of ``product_name`` and click Update.

        Quantity 0 + Update removes the line (standard Shopify behaviour).
        """
        self.type_text(self.locator(self._line_quantity, name=product_name), str(quantity))
        self.click_and_wait_for_new_page(self._update_button)

    def remove(self, product_name: str):
        """Remove the line of ``product_name`` (quantity 0 + Update)."""
        self.set_quantity(product_name, 0)

    ############################################################################
    # Total and checkout methods
    # Scope: Cart page > Total, Check Out button
    ############################################################################
    def total(self) -> float:
        """The cart total in pounds, e.g. 55.0."""
        match = self.TOTAL_PATTERN.search(self.body_text())
        if match:
            return float(match.group(2).replace(",", ""))
        amounts = re.findall(r"£\s?[\d,]+\.\d{2}", self.get_text(self._cart_form))
        return self.money_to_float(amounts[-1])

    def checkout(self):
        """Click Check Out and wait for the next page."""
        self.click_and_wait_for_new_page(self._checkout_button)

    # --- Locators -------------------------------------------------------------
    _cart_form = "css=form[action*='/cart']"
    _quantity_inputs = "css=input[name^='updates']"
    # The quantity box in the same cart row as the product link
    _line_quantity = (
        "xpath=//a[normalize-space()='{name}']"
        "/ancestor::*[.//input[starts-with(@name,'updates')]][1]"
        "//input[starts-with(@name,'updates')]"
    )
    _update_button = "css=[name='update']"
    _checkout_button = "css=[name='checkout']"
