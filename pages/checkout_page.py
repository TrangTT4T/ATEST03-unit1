"""Checkout page (Shopify checkout): reached from the cart; no payment is ever made."""
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class CheckoutPage(BasePage):
    def is_shown(self) -> bool:
        self.wait.until(EC.url_contains("checkout"))
        return True

    def lists(self, product_name: str) -> bool:
        self.wait.until(lambda d: product_name in self.body_text())
        return True
