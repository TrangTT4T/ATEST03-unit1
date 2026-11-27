from .base_page import BasePage


class CheckoutPage(BasePage):
    ############################################################################
    # Order summary methods
    ############################################################################
    def is_checkout_page_open(self) -> bool:
        """Wait until the checkout page is open."""
        self.wait_until_url_contains("checkout")
        return True

    def is_product_in_order_summary(self, product_name: str) -> bool:
        """Wait until the order summary shows ``product_name``."""
        self.element_should_contain_text(self._page_body, product_name, f"The checkout does not list {product_name!r}")
        return True
