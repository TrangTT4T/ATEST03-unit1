"""Catalog page: /collections/all"""
from .base_page import BasePage


class CatalogPage(BasePage):
    path = "/collections/all"

    ############################################################################
    # Product tile methods
    # Scope: Catalog > All products
    ############################################################################
    def tile_text(self, handle: str) -> str:
        """Text of one product tile (a link to /products/<handle>): name, price and "Sold Out"."""
        return self.get_text(self.locator(self._tile, handle=handle))

    # --- Locators -------------------------------------------------------------
    _tile = "css=a[href*='/products/{handle}']"
