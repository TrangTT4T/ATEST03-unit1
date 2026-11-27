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
    # Scope: BasePage > locator string -> (By, criteria)
    ############################################################################
    def by_locator(self, locator: str) -> tuple[str, str]:
        """
        :param locator: locator string
        :return: (strategy, criteria) to find element(s)
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
