"""Catalog page: /collections/all"""
from .base_page import BasePage


class CatalogPage(BasePage):
    path = "/collections/all"

    ############################################################################
    # Product tile methods
    # Scope: Catalog > All products
    ############################################################################
    def tile_text(self, url: str) -> str:
        """Text of one product tile (its ``url`` from dataset/products.json): name, price and "Sold Out"."""
        return self.get_text(self.locator(self._tile, url=url))

    # --- Locators -------------------------------------------------------------
    _tile = "css=a[href*='{url}']"  # the tile links to the product page
