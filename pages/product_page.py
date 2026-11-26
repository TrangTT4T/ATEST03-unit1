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
    def open_product(self, path_name: str):
        """Open /products/<path_name>; ``path_name`` comes from dataset/products.json, e.g. "grey-jacket"."""
        return self.open(self.URL_TEMPLATE.format(path_name=path_name))

    def title(self) -> str:
        """The product name."""
        return self.get_text(self._title)

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
            self._add(expected_increase=quantity)
            return
        # Theme without a visible quantity box: add the product N times.
        product_url = self.url
        for _ in range(quantity):
            if "/products/" not in self.url:  # a non-AJAX theme moved to /cart after the last add
                self.driver.get(product_url)
            self._add(expected_increase=1)

    def _add(self, expected_increase: int):
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
        old_page = self.find_element(self._html)
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
            self.wait_for_url_contains("/cart")

    # --- Locators -------------------------------------------------------------
    # itemprop="name" (schema.org markup) is the product name; the shop's first <h1> is its logo (F14).
    _title = "css=[itemprop='name']"
    # The standard Shopify add-to-cart form
    _add_button = "css=form[action*='/cart/add'] [type='submit']"
    _quantity = "css=form[action*='/cart/add'] input[name='quantity']"
