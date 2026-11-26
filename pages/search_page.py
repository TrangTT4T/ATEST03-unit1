"""Search results page: /search?q=<keyword>"""
from .base_page import BasePage


class SearchPage(BasePage):
    ############################################################################
    # Search result methods
    # Scope: Search > Results page
    ############################################################################
    def search_result_names(self) -> list[str]:
        """Product names once the tiles have faded in. Empty when the store says nothing matched.

        An empty grid right after navigation is not a result: the tiles are still loading
        (or still in fadeInUpBig, so their text is blank). Keep waiting.
        """
        found: dict[str, list[str]] = {}

        def results_are_ready(driver) -> bool:
            ready = self.loaded_search_results()
            if ready is None:
                return False
            found["names"] = ready
            return True

        self.wait_until(results_are_ready, "Search results never finished loading")
        return found["names"]

    def loaded_search_results(self) -> list[str] | None:
        """Names on the results grid, [] when nothing matched, None while the grid is still loading."""
        try:
            banner = self.find_elements(self._keyword)
            banner_text = banner[0].text if banner else ""
            if "No results found" in banner_text:
                return []
            names = [element.text.strip() for element in self.find_elements(self._result_names)]
        except Exception:
            return None
        if names and all(names):
            return names
        return None

    def shows_no_search_results(self) -> bool:
        """Wait for the store's "No results found for ..." message (an empty list alone proves nothing)."""
        self.element_should_contain_text(
            self._keyword, "No results found", "The 'No results found' message is not shown"
        )
        return True

    # --- Locators -------------------------------------------------------------
    _keyword = "css=#keyword"
    _result_names = "css=section.product-grid a[href*='/products/'] h3"
