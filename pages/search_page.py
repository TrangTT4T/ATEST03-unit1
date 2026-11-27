from .base_page import BasePage


class SearchPage(BasePage):
    ############################################################################
    # Search result methods
    ############################################################################
    def get_search_result_names(self) -> list[str]:
        ready = self.wait_until(self.search_result_names_if_loaded, "Search results never finished loading")
        return ready[0]

    def search_result_names_if_loaded(self, driver=None) -> tuple[list[str]] | bool:
        ready = self.read_search_result_names_now()
        if ready is None:
            return False
        return (ready,)

    def read_search_result_names_now(self) -> list[str] | None:
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

    def is_no_results_message_shown(self) -> bool:
        self.element_should_contain_text(
            self._keyword, "No results found", "The 'No results found' message is not shown"
        )
        return True

    # --- Locators -------------------------------------------------------------
    _keyword = "//*[@id='keyword']"
    _result_names = "//section[@class='product-grid']//a[contains(@href,'/products/')]//h3"
