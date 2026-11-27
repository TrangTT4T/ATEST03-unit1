import logging
import re
from functools import partial
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import quote
from helper_utility.helpers import Helper


class BasePage:
    MONEY_PATTERN = re.compile(r"£\s?([\d,]+\.\d{2})")  # a text pattern, not a locator

    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
        self.logger = logging.getLogger(type(self).__name__)  # behave shows these lines when a step fails
        self._helper = Helper()  # reads locators: locator string -> (By, criteria)

    ############################################################################
    # Data helpers (no browser needed)
    ############################################################################
    @staticmethod
    def money_to_float(text: str) -> float:
        """
        :param text: text with £ amount in it
        :return: the amount as a float
        """
        match = BasePage.MONEY_PATTERN.search(text)
        if not match:
            raise ValueError(f"No £ amount found in: {text!r}")
        return float(match.group(1).replace(",", ""))

    ############################################################################
    # Navigation methods
    ############################################################################
    def open_page(self, path: str | None = None):
        """Go to ``path`` on the store
        :param path: path name after the domain
        """
        target = path if path is not None else getattr(self.__class__, "path", "")
        url = f"{self.base_url}/{str(target).lstrip('/')}"
        self.logger.info("Open %s", url)
        self.driver.get(url)

    def wait_until_url_contains(self, fragment: str, timeout: int | None = None):
        """Wait until the address contains ``fragment``, for example "/cart"."""
        self.wait_until(
            EC.url_contains(fragment),
            f"URL never contained {fragment!r} (now {self.driver.current_url})",
            timeout,
        )

    ############################################################################
    # Locator methods
    ############################################################################
    def find_element(self, locator: str, timeout: int | None = None):
        """
        :param locator: locator string
        :param timeout: seconds
        :return: the WebElement
        """
        return self.wait_until(
            EC.presence_of_element_located(self._helper.by_locator(locator)),
            f"Element {locator!r} not found",
            timeout,
        )

    def find_elements(self, locator: str) -> list:
        """
        :param locator: locator string
        :return: list of WebElements
        """
        return self.driver.find_elements(*self._helper.by_locator(locator))

    def is_element_present(self, locator: str, driver=None) -> bool:
        return bool(self.find_elements(locator))

    ############################################################################
    # Action methods
    ############################################################################
    def click_element(self, locator: str, timeout: int | None = None):
        """Wait until the element is visible and enabled, then click it.
        :param locator: XPath locator
        :param timeout: seconds; default is the page timeout
        """
        self.logger.info("Click %s", locator)
        self.wait_until(EC.element_to_be_clickable(self._helper.by_locator(locator)),
                        f"Element {locator!r} never became clickable", timeout).click()

    def click_and_wait_for_new_page(self, locator: str):
        old_page = self.find_element(self._page)
        self.click_element(locator)
        self.wait_until(EC.staleness_of(old_page), f"Clicking {locator!r} did not load a new page")

    def type_text(self, locator: str, text: str, clear: bool = True, secret: bool = False):
        """Type ``text`` into a field
        :param locator: XPath locator of the input
        :param text: text to type
        :param clear: empty the field first
        :param secret: if password the log will show *** instead of the text
        :return: the input element
        """
        self.logger.info("Type %r into %s", "***" if secret else text, locator)
        element = self.find_element(locator)
        if clear:
            element.clear()
        element.send_keys(text)
        return element

    ############################################################################
    # Wait and read methods
    # Scope: Every page > element state and text
    ############################################################################
    def wait_until(self, condition, message: str, timeout: int | None = None):
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            return wait.until(condition, message)
        except TimeoutException:
            if message:
                self.logger.error(message)
            raise

    def get_element_text(self, locator: str) -> str:
        """Waits until the element shows text."""
        return self.wait_until(
            partial(self.first_match_text_if_shown, locator),
            f"Element {locator!r} never showed any text",
        )

    def first_match_text_if_shown(self, locator: str, driver=None) -> str | bool:
        try:
            elements = self.find_elements(locator)
            return elements[0].text.strip() if elements else False
        except StaleElementReferenceException:
            return False

    def get_page_text(self) -> str:
        """All visible text of the page."""
        return self.get_element_text(self._page_body)

    def is_element_visible(self, locator: str, timeout: int = 0) -> bool:
        """True when the element is visible
        :param locator: XPath locator
        :param timeout: timeout wait
        :return: True or False
        """
        try:
            self.wait_until(EC.visibility_of_element_located(self._helper.by_locator(locator)), "", timeout)
        except TimeoutException:
            self.logger.info("Element %s is not visible", locator)
            return False
        return True

    ############################################################################
    # Check methods element contain or display
    ############################################################################
    def element_should_be_visible(self, locator: str, error_msg: str | None = None):
        if not self.is_element_visible(locator, self.timeout):
            raise AssertionError(error_msg or f"Element {locator!r} is not visible")

    def element_should_contain_text(self, locator: str, text: str, error_msg: str | None = None):
        try:
            self.wait_until(EC.text_to_be_present_in_element(self._helper.by_locator(locator), text), "")
        except TimeoutException:
            matches = self.find_elements(locator)
            actual = matches[0].text if matches else "<no element>"
            raise AssertionError(error_msg or f"Element {locator!r} shows {actual!r}, expected to contain {text!r}")

    ############################################################################
    # Header methods
    ############################################################################
    def get_header_cart_count(self) -> int:
        return self.wait_until(self.header_cart_count_if_shown, "The header never showed a cart count")

    def header_cart_count_if_shown(self, driver=None) -> int | bool:
        try:
            text = " ".join(link.get_attribute("textContent") or "" for link in self.find_elements(self._header_cart_link))
        except StaleElementReferenceException:
            return False
        match = re.search(r"\((\d+)\)", text)
        return int(match.group(1)) if match else False

    def open_search_results(self, keyword: str):
        self.driver.get(f"{self.base_url}/search?type=product&q={quote(keyword)}")
        self.wait_until(
            self.is_search_page_loaded,
            f"Search results for {keyword!r} never loaded (now {self.driver.current_url})",
        )
        if "Verify you are human" in (self.driver.title or ""):
            raise AssertionError(
                "Cloudflare asked to verify a human, so the search page did not open"
            )

    def is_search_page_loaded(self, driver) -> bool:
        return self.is_element_present(self._search_banner) or "Verify you are human" in (driver.title or "")

    # --- Locators -------------------------------------------------------------
    _page = "//html"
    _page_body = "//body"
    _header_cart_link = "//a[contains(normalize-space(),'My Cart')]"
    _search_banner = "//*[@id='keyword']"
