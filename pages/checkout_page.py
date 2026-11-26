"""Checkout page (Shopify checkout): reached from the cart; no payment is ever made."""
from .base_page import BasePage


class CheckoutPage(BasePage):
    ############################################################################
    # Order summary methods
    # Scope: Checkout > Order summary
    ############################################################################
    def is_shown(self) -> bool:
        """Wait until the checkout page is open."""
        self.wait_for_url_contains("checkout")
        return True

    def lists(self, product_name: str) -> bool:
        """Wait until the order summary shows ``product_name``."""
        self.page_should_contain_text(product_name, f"The checkout does not list {product_name!r}")
        return True
