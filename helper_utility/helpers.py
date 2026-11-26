"""Helper: everything the steps and the pages share, in one class.

* Step helpers: Helper.get_product_from_dataset(context, name), Helper.create_page_object(context, CartPage).
* Element finder (used by BasePage): reads a locator string and tells Selenium how to find it, the same
  idea as the team's selenium_wrapper/elementfinder.py. A locator is plain XPath with no prefix (the
  default, and what every page writes), or "prefix=criteria" / "prefix:criteria": "id=cart", "name=q",
  "css=#cart", "link=Forgot your password?", "partial link=Forgot", "tag_name=h1", "class_name=errors".

Kept outside tests/steps so behave never loads it twice.
"""
import re

from selenium.webdriver.common.by import By


class Helper:
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

    ############################################################################
    # Step helpers
    # Scope: tests/steps > test data, page objects
    ############################################################################
    @staticmethod
    def get_product_from_dataset(context, product_name):
        """Return the test data of one product from dataset/products.json: path-name, price, status.

        Fails the step with a clear message when the name is not in the file.
        """
        try:
            return context.products[product_name]
        except KeyError:
            raise AssertionError(f"Unknown product {product_name!r}: add it to dataset/products.json")

    @staticmethod
    def create_page_object(context, page_class):
        """Create a page object (e.g. CartPage) bound to this scenario's browser, base URL and timeout."""
        return page_class(context.driver, context.base_url, context.timeout)

    ############################################################################
    # Element finder
    # Scope: BasePage > locator string -> (By, criteria) -> elements
    ############################################################################
    def by_locator(self, locator: str) -> tuple[str, str]:
        """The (By, criteria) pair Selenium needs for ``locator``.

        "//*[@id='cart']" -> (By.XPATH, "//*[@id='cart']");  "id=cart" or "id:cart" -> (By.ID, "cart")

        A locator starting with "/" or "(" is XPath (prefix "default"). Otherwise any word before
        the first "=" or ":" is the prefix, so a typo such as "nmae=q" fails here with a clear
        message instead of being sent to Selenium as XPath.

        :param locator: locator string, plain XPath or "prefix=criteria"
        :return: (strategy, criteria) for driver.find_element(s) and expected_conditions
        :raises ValueError: when the locator is empty or its prefix is not supported
        """
        if not isinstance(locator, str) or not locator.strip():
            raise ValueError(f"A locator is a non-empty string, got {locator!r}")
        locator = locator.strip()
        prefix, criteria = "default", locator
        if not locator.startswith(("/", "(")):
            match = re.match(r"([A-Za-z_ ]+?)\s*[=:]\s*(.*)", locator, re.DOTALL)
            if match:
                prefix, criteria = match.group(1).strip().lower(), match.group(2)
        strategy = self._strategies.get(prefix)
        if strategy is None:
            raise ValueError(f"Element locator with prefix '{prefix}' is not supported: {locator!r}")
        return strategy, criteria

    def find_element(self, driver, locator: str):
        """The first element matching ``locator``.

        :param driver: the WebDriver
        :param locator: locator string
        :return: the WebElement
        :raises NoSuchElementException: when nothing matches (raised by Selenium; its message names the selector)
        """
        return driver.find_element(*self.by_locator(locator))

    def find_elements(self, driver, locator: str) -> list:
        """Every element matching ``locator`` (an empty list when nothing matches).

        :param driver: the WebDriver
        :param locator: locator string
        :return: list of WebElements
        """
        return driver.find_elements(*self.by_locator(locator))
