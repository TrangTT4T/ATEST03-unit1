"""Product detail page: /products/<path-name>"""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class ProductPage(BasePage):
    URL_TEMPLATE = "/products/{path_name}"  # path_name = "path-name" in dataset/products.json

    ############################################################################
    # Product detail methods
    # Scope: Product page > Name, price, stock
    ############################################################################
    def open_product_page(self, path_name: str):
        """Open /products/<path_name>; ``path_name`` comes from dataset/products.json, e.g. "grey-jacket"."""
        self.open_page(self.URL_TEMPLATE.format(path_name=path_name))

    def get_product_name(self) -> str:
        """The product name."""
        return self.get_element_text(self._title)

    def can_add_to_cart(self) -> bool:
        """False for a sold-out product: no button, a disabled one, or one labelled "Sold Out"."""
        buttons = self.find_elements(self._add_button)
        if not buttons:
            return False
        button = buttons[0]
        label = (button.get_attribute("value") or button.text or "").lower()
        return button.is_enabled() and "sold out" not in label and "unavailable" not in label

    ############################################################################
    # Add to cart methods
    # Scope: Product page > Add to cart form
    ############################################################################
    def add_to_cart(self, quantity: int = 1):
        """Add ``quantity`` items and wait until the store has taken every one."""
        if self.is_element_visible(self._quantity):
            self.type_text(self._quantity, str(quantity))
            self._submit_add_to_cart()
            return
        # Theme without a visible quantity box: add the product N times.
        product_url = self.current_url
        for _ in range(quantity):
            if "/products/" not in self.current_url:  # a non-AJAX theme moved to /cart after the last add
                self.driver.get(product_url)
            self._submit_add_to_cart()

    def _submit_add_to_cart(self):
        """Click Add to Cart and wait until the browser has loaded the next page.

        The theme's click handler only submits the form after a fly-to-cart animation, and
        that animation often never finishes. Turn the handler off so the click posts the form.
        If the button cannot be clicked, submit the form directly.
        """
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
            # Stale html means the new document has loaded. URL "/cart" alone is too early:
            # it also matches /cart/add while the POST is still going out.
            self.wait_until(EC.staleness_of(old_page), "The add did not open the cart", timeout=8)
        except TimeoutException:
            self.driver.execute_script(
                "var form=document.getElementById('product-form'); if (form) form.submit();"
            )
            self.wait_until_url_contains("/cart")

    # --- Locators -------------------------------------------------------------
    # Product details. itemprop="name" (schema.org) is the name; the first <h1> is the shop logo (F14).
    _title = "//*[@itemprop='name']"
    # Add to cart form (standard Shopify)
    _add_button = "//form[contains(@action,'/cart/add')]//*[@type='submit']"
    _quantity = "//form[contains(@action,'/cart/add')]//input[@name='quantity']"
