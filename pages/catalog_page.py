"""Catalog page: /collections/all"""
from .base_page import BasePage


class CatalogPage(BasePage):
    path = "/collections/all"

    ############################################################################
    # Product tile methods
    # Scope: Catalog > All products
    ############################################################################
    def product_tile_text(self, path_name: str) -> str:
        """Text currently visible on one product tile. The price may not have faded in yet."""
        locator = self.locator(self._tile, path_name=path_name)
        try:
            elements = self.find_elements(locator)
            return elements[0].text.strip() if elements else ""
        except Exception:
            return ""

    def text_when_product_price_shown(self, path_name: str) -> str | bool:
        """The tile text when its £ price is visible, otherwise False so the wait keeps looking."""
        text = self.product_tile_text(path_name)
        return text if "£" in text else False

    def shows_product_price(self, path_name: str) -> str:
        """Tile text once the £ price has faded in.

        The theme animates tiles with fadeInUpBig. The name can appear before the price,
        and reading at that moment misses it.
        """
        return self.wait_until(
            lambda driver: self.text_when_product_price_shown(path_name),
            f"Product {path_name!r} never showed its price",
        )

    # --- Locators -------------------------------------------------------------
    _tile = "css=a[href*='/products/{path_name}']"  # the tile links to the product page
