"""Search results page: /search?q=<keyword>"""
from .base_page import BasePage


class SearchPage(BasePage):
    ############################################################################
    # Search result methods
    # Scope: Search > Results page
    ############################################################################
    def get_search_result_names(self) -> list[str]:
        """Product names once the tiles have faded in. Empty when the store says nothing matched.

        An empty grid right after navigation is not a result: the tiles are still loading
        (or still in fadeInUpBig, so their text is blank). Keep waiting.
        """
        ready = self.wait_until(self.search_result_names_if_loaded, "Search results never finished loading")
        return ready[0]

    def search_result_names_if_loaded(self, driver=None) -> tuple[list[str]] | bool:
        """A one-item tuple of the names once the grid has settled, or False while it is loading."""
        ready = self.read_search_result_names_now()
        if ready is None:
            return False
        return (ready,)

    def read_search_result_names_now(self) -> list[str] | None:
        """Names on the results grid, [] when nothing matched, None while the grid is still loading."""
        try:
            banner = self.find_elements_now(self._keyword)
            banner_text = banner[0].text if banner else ""
            if "No results found" in banner_text:
                return []
            names = [element.text.strip() for element in self.find_elements_now(self._result_names)]
        except Exception:
            return None
        if names and all(names):
            return names
        return None

    def is_no_results_message_shown(self) -> bool:
        """Wait for the store's "No results found for ..." message (an empty list alone proves nothing)."""
        self.element_should_contain_text(
            self._keyword, "No results found", "The 'No results found' message is not shown"
        )
        return True

    # --- Locators -------------------------------------------------------------
    _keyword = "xpath=//*[@id='keyword']"
    _result_names = "xpath=//section[contains(concat(' ',normalize-space(@class),' '),' product-grid ')]//a[contains(@href,'/products/')]//h3"
