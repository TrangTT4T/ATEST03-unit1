"""Product detail page: /products/<handle>"""
from .base_page import BasePage


class ProductPage(BasePage):
    ############################################################################
    # Product detail methods
    # Scope: Product page > Name, price, stock
    ############################################################################
    def open_product(self, handle: str):
        """Open /products/<handle> (the handle comes from dataset/products.json)."""
        return self.open(f"/products/{handle}")

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
        """Click Add to Cart and wait until the store has taken the product.

        The live theme adds with AJAX: jQuery posts /cart/add.js, updates the header and the page
        stays (Day 4 finding F11). Without JavaScript the form posts and the browser lands on /cart
        (finding F7). Wait for whichever happens - never for time, and never only for a navigation
        that an AJAX theme does not make.
        """
        before = self.mini_cart_count()
        self.click_element(self._add_button)
        self.wait_until(
            lambda d: ("/cart" in d.current_url and "/products/" not in d.current_url)
            or (self.mini_cart_count_now() or 0) >= before + expected_increase,
            f"The cart never took the product (header count stayed at {before})",
        )

    # --- Locators -------------------------------------------------------------
    # itemprop="name" (schema.org markup) is the product name; the shop's first <h1> is its logo (F14).
    _title = "css=[itemprop='name']"
    # The standard Shopify add-to-cart form
    _add_button = "css=form[action*='/cart/add'] [type='submit']"
    _quantity = "css=form[action*='/cart/add'] input[name='quantity']"
