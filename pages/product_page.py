from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class ProductPage(BasePage):
    URL_TEMPLATE = "/products/{path_name}"

    ############################################################################
    # Product detail methods
    ############################################################################
    def open_product_page(self, path_name: str):
        self.open_page(self.URL_TEMPLATE.format(path_name=path_name))

    def get_product_name(self) -> str:
        return self.get_element_text(self._title)

    def can_add_to_cart(self) -> bool:
        buttons = self.find_elements(self._add_button)
        if not buttons:
            return False
        button = buttons[0]
        label = (button.get_attribute("value") or button.text or "").lower()
        return button.is_enabled() and "sold out" not in label and "unavailable" not in label

    ############################################################################
    # Add to cart methods
    ############################################################################
    def add_to_cart(self, quantity: int = 1):
        """Add ``quantity`` items and wait until the store update."""
        if self.is_element_visible(self._quantity):
            self.type_text(self._quantity, str(quantity))
            self._submit_add_to_cart()
            return
        product_url = self.driver.current_url
        for _ in range(quantity):
            if "/products/" not in self.driver.current_url:
                self.driver.get(product_url)
            self._submit_add_to_cart()

    def _submit_add_to_cart(self):
        """Click Add to Cart and wait until the browser has loaded the next page."""
        self.driver.execute_script(
            "if (window.jQuery) {"
            " jQuery('.add-to-cart').off('click');"
            " jQuery('form.quickAdd').off('submit');"
            "}"
        )
        old_page = self.find_element(self._page)
        try:
            self.click_element(self._add_button)
        except TimeoutException:
            self.driver.execute_script(
                "var form=document.getElementById('product-form'); if (form) form.submit();"
            )
        try:
            self.wait_until(EC.staleness_of(old_page), "The add did not open the cart", timeout=8)
        except TimeoutException:
            self.driver.execute_script(
                "var form=document.getElementById('product-form'); if (form) form.submit();"
            )
            self.wait_until_url_contains("/cart")

    # --- Locators -------------------------------------------------------------
    _title = "//*[@itemprop='name']"
    _add_button = "//form[contains(@action,'/cart/add')]//*[@type='submit']"
    _quantity = "//form[contains(@action,'/cart/add')]//input[@name='quantity']"
