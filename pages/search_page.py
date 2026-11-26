"""Search results page: /search?q=<keyword>"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class SearchPage(BasePage):
    def result_names(self) -> list[str]:
        return [link.text for link in self.find_all(*self._result_links)]

    def no_results_shown(self) -> bool:
        """Waits for the store's "No results found for ..." message (an empty list alone proves nothing)."""
        self.wait.until(EC.visibility_of_element_located(self._no_results_message))
        return True

    # --- Locators -------------------------------------------------------------
    _result_links = (By.CSS_SELECTOR, "a[href*='/products/']")
    _no_results_message = (By.XPATH, "//*[contains(text(), 'No results found for')]")
