"""ElementFinder: reads a locator string and tells Selenium how to find the element.

Same idea as the team's selenium_wrapper/elementfinder.py. A locator is either

* plain XPath with no prefix (the default, and what every page in this project writes):
  "//*[@id='cart']", "(//a)[1]";
* or "prefix=criteria" / "prefix:criteria" for another strategy:
  "id=cart", "name=q", "css=#cart", "link=Forgot your password?", "partial link=Forgot",
  "tag_name=h1", "class_name=errors", "xpath=//h1".
"""
from selenium.webdriver.common.by import By


class ElementFinder:
    def __init__(self):
        strategies = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "link": By.LINK_TEXT,
            "partial link": By.PARTIAL_LINK_TEXT,
            "css": By.CSS_SELECTOR,
            "tag_name": By.TAG_NAME,
            "class_name": By.CLASS_NAME,
            "default": By.XPATH,
        }
        self._strategies = strategies

    def by_locator(self, locator: str) -> tuple[str, str]:
        """The (By, criteria) pair Selenium needs for ``locator``.

        "//*[@id='cart']" -> (By.XPATH, "//*[@id='cart']");  "id=cart" -> (By.ID, "cart")

        :param locator: locator string, plain XPath or "prefix=criteria"
        :return: (strategy, criteria) for driver.find_element(s) and expected_conditions
        :raises ValueError: when the locator is empty or its prefix is not supported
        """
        if not isinstance(locator, str) or not locator.strip():
            raise ValueError(f"A locator is a non-empty string, got {locator!r}")
        prefix, criteria = self._parse_locator(locator.strip())
        prefix = "default" if prefix is None else prefix
        strategy = self._strategies.get(prefix)
        if strategy is None:
            raise ValueError(f"Element locator with prefix '{prefix}' is not supported")
        return strategy, criteria

    def find_all(self, driver, locator: str) -> list:
        """Every element matching ``locator`` right now (no wait; an empty list is a valid answer).

        :param driver: the WebDriver
        :param locator: locator string
        :return: list of WebElements
        """
        return driver.find_elements(*self.by_locator(locator))

    def _parse_locator(self, locator: str) -> tuple[str | None, str]:
        """("id", "cart") for "id=cart" or "id:cart"; (None, locator) for plain XPath."""
        if locator.startswith(("/", "(")):
            return None, locator
        for separator in ("=", ":"):
            prefix, found, criteria = locator.partition(separator)
            if found and prefix.strip().lower() in self._strategies:
                return prefix.strip().lower(), criteria.strip()
        return None, locator
