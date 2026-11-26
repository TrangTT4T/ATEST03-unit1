"""Catalog page: /collections/all"""
from .base_page import BasePage


class CatalogPage(BasePage):
    path = "/collections/all"

    ############################################################################
    # Product tile methods
    # Scope: Catalog > All products
    ############################################################################
    def tile_text(self, path_name: str) -> str:
        """Text of one product tile, once its price has faded in.

        The theme animates tiles with fadeInUpBig. The name can appear before the £ price,
        and reading at that moment misses the price.
        """
        locator = self.locator(self._tile, path_name=path_name)

        def shows_price(driver) -> str | bool:
            try:
                elements = self.find_elements(locator)
                text = elements[0].text.strip() if elements else ""
            except Exception:
                return False
            return text if "£" in text else False

        return self.wait_until(shows_price, f"Tile {path_name!r} never showed its price")

    # --- Locators -------------------------------------------------------------
    _tile = "css=a[href*='/products/{path_name}']"  # the tile links to the product page
