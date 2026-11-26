"""Cart page: /cart"""
import re

from selenium.common.exceptions import TimeoutException

from .base_page import BasePage


class CartPage(BasePage):
    """Every locator is scoped to #cart: each page also holds a HIDDEN mini-cart drawer with the same
    rows and quantity boxes, which would otherwise be counted twice (or typed into, and fail)."""

    path = "/cart"
    TOTAL_PATTERN = re.compile(r"(sub)?total[^£]{0,40}£\s?([\d,]+\.\d{2})", re.IGNORECASE)  # text, not a locator

    def open(self, path: str | None = None):
        """Open the cart. The theme spinner can keep the load event from firing; the cart is already on screen."""
        self.driver.set_page_load_timeout(8)
        try:
            return super().open(path)
        except TimeoutException:
            try:
                self.driver.execute_script("window.stop();")
            except Exception:
                pass
            return self
        finally:
            self.driver.set_page_load_timeout(300)

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
        line = self.locator(self._line_quantity, name=product_name)
        if not self.is_element_present(line):
            # These scenarios put one product in the cart. The row markup does not always
            # match the link text, but the quantity box in #cart is that line.
            self.wait_until(
                lambda d: self.is_element_present(self._quantity_inputs),
                f"{product_name!r} is not in the cart",
            )
            line = self._quantity_inputs
        self.type_text(line, str(quantity))
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
        try:
            self.driver.execute_script(
                "var button=document.querySelector('#checkout'); if(button) button.scrollIntoView({block:'center'});"
            )
            self.click_and_wait_for_new_page(self._checkout_button)
        except TimeoutException:
            clicked = self.driver.execute_script(
                "var button=document.querySelector('#checkout');"
                "if(!button) return false; button.click(); return true;"
            )
            if not clicked:
                raise TimeoutException("Check Out is not on the cart page")
            self.wait_for_url_contains("checkout")

    # --- Locators -------------------------------------------------------------
    _cart_form = "css=#cart"
    _quantity_inputs = "css=#cart input[name^='updates']"
    # The quantity box in the same cart row as the product link
    _line_quantity = (
        "xpath=//*[@id='cart']//div[contains(@class,'row')]"
        "[.//a[contains(normalize-space(.), '{name}')]]"
        "//input[starts-with(@name,'updates')]"
    )
    _update_button = "css=#update"
    _checkout_button = "css=#checkout"
