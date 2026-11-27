import re
from functools import partial
from selenium.common.exceptions import TimeoutException
from .base_page import BasePage


class CartPage(BasePage):

    path = "/cart"
    TOTAL_PATTERN = re.compile(r"(sub)?total[^£]{0,40}£\s?([\d,]+\.\d{2})", re.IGNORECASE)  # text, not a locator

    ############################################################################
    # Cart line methods
    ############################################################################
    def count_items_in_cart(self) -> int:
        return sum(int(i.get_attribute("value") or 0) for i in self.find_elements(self._quantity_inputs))

    def is_cart_empty(self) -> bool:
        return not self.find_elements(self._quantity_inputs)

    def change_quantity(self, product_name: str, quantity: int):
        line = self._line_quantity.format(product_name)
        if not self.is_element_present(line):
            self.wait_until(
                partial(self.is_element_present, self._quantity_inputs),
                f"{product_name!r} is not in the cart",
            )
            line = self._quantity_inputs
        self.type_text(line, str(quantity))
        self.click_and_wait_for_new_page(self._update_button)

    def remove_product_from_cart(self, product_name: str):
        self.change_quantity(product_name, 0)

    ############################################################################
    # Total and checkout methods
    ############################################################################
    def get_cart_total(self) -> float:
        match = self.TOTAL_PATTERN.search(self.get_page_text())
        if match:
            return float(match.group(2).replace(",", ""))
        amounts = re.findall(r"£\s?[\d,]+\.\d{2}", self.get_element_text(self._cart_form))
        return self.money_to_float(amounts[-1])

    def click_checkout(self):
        """Click Check Out and wait for the next page."""
        try:
            self.driver.execute_script(
                "var button=document.getElementById('checkout'); if(button) button.scrollIntoView({block:'center'});"
            )
            self.click_and_wait_for_new_page(self._checkout_button)
        except TimeoutException:
            clicked = self.driver.execute_script(
                "var button=document.getElementById('checkout');"
                "if(!button) return false; button.click(); return true;"
            )
            if not clicked:
                raise TimeoutException("Check Out is not on the cart page")
            self.wait_until_url_contains("checkout")

    # --- Locators -------------------------------------------------------------
    _cart_form = "//*[@id='cart']"
    _quantity_inputs = "//*[@id='cart']//input[starts-with(@name,'updates')]"
    _line_quantity = ("//*[@id='cart']//div[contains(@class,'row')][.//a[contains(normalize-space(),'{}')]]"
                      "//input[starts-with(@name,'updates')]"
    )
    # Cart buttons
    _update_button = "//*[@id='update']"
    _checkout_button = "//*[@id='checkout']"
