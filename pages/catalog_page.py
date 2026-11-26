"""Catalog page: /collections/all"""
from functools import partial

from .base_page import BasePage


class CatalogPage(BasePage):
    path = "/collections/all"

    ############################################################################
    # Product tile methods
    # Scope: Catalog > All products
    ############################################################################
    def read_product_tile_text_now(self, path_name: str) -> str:
        """Text currently visible on one product tile. The price may not have faded in yet."""
        locator = self.fill_locator(self._tile, path_name=path_name)
        try:
            elements = self.find_elements_now(locator)
            return elements[0].text.strip() if elements else ""
        except Exception:
            return ""

    def tile_text_if_price_shown(self, path_name: str, driver=None) -> str | bool:
        """The tile text when its £ price is visible, otherwise False so the wait keeps looking."""
        text = self.read_product_tile_text_now(path_name)
        return text if "£" in text else False

    def get_product_tile_text(self, path_name: str) -> str:
        """Tile text once the £ price has faded in.

        The theme animates tiles with fadeInUpBig. The name can appear before the price,
        and reading at that moment misses it.
        """
        return self.wait_until(
            partial(self.tile_text_if_price_shown, path_name),
            f"Product {path_name!r} never showed its price",
        )

    # --- Locators -------------------------------------------------------------
    _tile = "xpath=//a[contains(@href,'/products/{path_name}')]"  # the tile links to the product page
