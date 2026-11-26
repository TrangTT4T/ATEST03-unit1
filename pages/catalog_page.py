"""Catalog page: /collections/all"""
from .base_page import BasePage


class CatalogPage(BasePage):
    path = "/collections/all"

    ############################################################################
    # Product tile methods
    # Scope: Catalog > All products
    ############################################################################
    def tile_text(self, path_name: str) -> str:
        """Text of one product tile (its "path-name" in dataset/products.json): name, price and "Sold Out"."""
        return self.get_text(self.locator(self._tile, path_name=path_name))

    # --- Locators -------------------------------------------------------------
    _tile = "css=a[href*='/products/{path_name}']"  # the tile links to the product page
