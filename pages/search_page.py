"""Search results page: /search?q=<keyword>"""
from .base_page import BasePage


class SearchPage(BasePage):
    ############################################################################
    # Search result methods
    # Scope: Search > Results page
    ############################################################################
    def result_names(self) -> list[str]:
        """Names of the products found (no wait: use after the results page has loaded)."""
        return [link.text for link in self.find_elements(self._result_links)]

    def no_results_shown(self) -> bool:
        """Wait for the store's "No results found for ..." message (an empty list alone proves nothing)."""
        self.element_should_be_visible(self._no_results_message, "The 'No results found' message is not shown")
        return True

    # --- Locators -------------------------------------------------------------
    _result_links = "css=a[href*='/products/']"
    _no_results_message = "xpath=//*[contains(text(), 'No results found for')]"
