"""Catalog page: /collections/all"""
from selenium.webdriver.common.by import By

from .base_page import BasePage


class CatalogPage(BasePage):
    path = "/collections/all"

    def tile_text(self, handle: str) -> str:
        # Each product tile is a link to /products/<handle> holding name, price and "Sold Out".
        return self.find(*self.locator(self._tile, handle=handle)).text

    # --- Locators -------------------------------------------------------------
    _tile = (By.CSS_SELECTOR, "a[href*='/products/{handle}']")
