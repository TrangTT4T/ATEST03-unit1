"""Base Page Object (Selenium WebDriver): navigation and the custom element methods every page uses.

Locators are plain XPath strings that describe the element, grouped under a comment that names
the area of the page, at the bottom of each class:

    # Cart table
    _cart_form = "//*[@id='cart']"
    # Product tiles
    _tile = "//a[contains(@href,'/products/{}')]"   # a template: self._tile.format(path_name)

``ElementFinder`` (helper_utility/helpers.py) reads each locator and gives Selenium the
``(By, criteria)`` pair: plain XPath by default, or "id=...", "name=...", "css=..." when needed.

Pages never call ``driver.find_element`` or ``WebDriverWait`` themselves. They pass a locator
string to the BasePage methods, which parse it, wait for the right state, log what they do and
fail with a message that names the locator. No method sleeps: every wait is for a state.

Layout of every page object (one class per file):

* methods grouped under ``####`` banners that name the area of the page (``# Scope: ...``);
* a docstring on every public method;
* a ``# --- Locators ---`` section at the BOTTOM of the class: XPath strings, grouped by area.
"""
import logging
import re
from functools import partial

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helper_utility.helpers import ElementFinder


class BasePage:
    MONEY_PATTERN = re.compile(r"£\s?([\d,]+\.\d{2})")  # a text pattern, not a locator

    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
        self.logger = logging.getLogger(type(self).__name__)  # behave shows these lines when a step fails
        self._element_finder = ElementFinder()  # locator string -> (By, criteria)

    ############################################################################
    # Data helpers (no browser needed)
    # Scope: Every page > prices
    ############################################################################
    @staticmethod
    def money_to_float(text: str) -> float:
        """'£1,120.00' -> 1120.0

        :param text: any text with one £ amount in it
        :return: the amount as a float
        """
        match = BasePage.MONEY_PATTERN.search(text)
        if not match:
            raise ValueError(f"No £ amount found in: {text!r}")
        return float(match.group(1).replace(",", ""))

    ############################################################################
    # Navigation methods
    # Scope: Every page
    ############################################################################
    def open_page(self, path: str | None = None):
        """Go to ``path`` on the store. With no path, use this page's own path, or the store root.

        :param path: path after the domain, e.g. "/cart"
        """
        target = path if path is not None else getattr(self.__class__, "path", "")
        url = f"{self.base_url}/{str(target).lstrip('/')}"
        self.logger.info("Open %s", url)
        self.driver.get(url)

    @property
    def current_url(self) -> str:
        """The address the browser is on now."""
        return self.driver.current_url

    def wait_until_url_contains(self, fragment: str, timeout: int | None = None):
        """Wait until the address contains ``fragment``, for example "/cart"."""
        self.wait_until(
            EC.url_contains(fragment),
            f"URL never contained {fragment!r} (now {self.current_url})",
            timeout,
        )

    ############################################################################
    # Locator methods
    # Scope: Every page > locators -> elements
    ############################################################################
    def find_element(self, locator: str, timeout: int | None = None):
        """Find one element, waiting until it is in the page.

        :param locator: locator string, e.g. "//*[@id='cart']"
        :param timeout: seconds; default is the page timeout
        :return: the WebElement
        :raises TimeoutException: when the element never appears
        """
        return self.wait_until(
            partial(self._element_finder.find_element, locator=locator),  # retried while not found
            f"Element {locator!r} not found",
            timeout,
        )

    def find_elements(self, locator: str) -> list:
        """Every element matching ``locator`` right now (no wait; an empty list is a valid answer).

        :param locator: locator string
        :return: list of WebElements
        """
        return self._element_finder.find_elements(self.driver, locator)

    def is_element_present(self, locator: str, driver=None) -> bool:
        """True when at least one element matches ``locator`` right now (no wait)."""
        return bool(self.find_elements(locator))

    ############################################################################
    # Action methods
    # Scope: Every page > click, type, submit
    ############################################################################
    def click_element(self, locator: str, timeout: int | None = None):
        """Wait until the element is visible and enabled, then click it.

        :param locator: XPath locator
        :param timeout: seconds; default is the page timeout
        """
        self.logger.info("Click %s", locator)
        self.wait_until(EC.element_to_be_clickable(self._element_finder.by_locator(locator)),
                        f"Element {locator!r} never became clickable", timeout).click()

    def click_and_wait_for_new_page(self, locator: str):
        """Click a form button and wait until the browser has replaced the old page.

        Without this, the next driver.get() can cancel the form POST (Day 4 findings F7/F8).

        :param locator: XPath locator of the submit button
        """
        old_page = self.find_element(self._page)
        self.click_element(locator)
        self.wait_until(EC.staleness_of(old_page), f"Clicking {locator!r} did not load a new page")

    def type_text(self, locator: str, text: str, clear: bool = True, secret: bool = False):
        """Type ``text`` into a field (cleared first by default).

        :param locator: XPath locator of the input
        :param text: text to type
        :param clear: empty the field first
        :param secret: a password: the log shows *** instead of the text
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
        """Wait for ``condition`` (an expected condition or ``lambda driver: ...``).

        :param condition: called with the driver until it returns a truthy value
        :param message: the error message when the time is up (name the locator or the state)
        :param timeout: seconds; default is the page timeout
        :return: the condition's truthy value
        :raises TimeoutException: with ``message``
        """
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(condition, message)

    def get_element_text(self, locator: str) -> str:
        """Visible text of the element; waits until the element shows some text.

        Selenium's ``.text`` is "" while an element is hidden or still off-screen, e.g. a catalog
        tile sliding in (the theme animates tiles with ``fadeInUpBig``): reading it as soon as it
        exists, or as soon as it counts as "visible", can return "" (Day 4 finding F15).
        """
        return self.wait_until(
            partial(self.first_match_text_if_shown, locator),
            f"Element {locator!r} never showed any text",
        )

    def first_match_text_if_shown(self, locator: str, driver=None) -> str | bool:
        """Text of the first match, or False while it is missing, blank, or being redrawn."""
        try:
            elements = self.find_elements(locator)
            return elements[0].text.strip() if elements else False
        except StaleElementReferenceException:
            return False

    def get_page_text(self) -> str:
        """All visible text of the page."""
        return self.get_element_text(self._page_body)

    def is_element_visible(self, locator: str, timeout: int = 0) -> bool:
        """True when the element is visible, waiting up to ``timeout`` seconds (0: check now).

        :param locator: XPath locator
        :param timeout: seconds to wait; never a fixed sleep
        :return: True or False, never an exception
        """
        try:
            self.wait_until(EC.visibility_of_element_located(self._element_finder.by_locator(locator)), "", timeout)
        except TimeoutException:
            self.logger.info("Element %s is not visible", locator)
            return False
        return True

    ############################################################################
    # Check methods (raise AssertionError with a readable message)
    # Scope: Every page > element state
    ############################################################################
    def element_should_be_visible(self, locator: str, error_msg: str | None = None):
        """Fail unless the element becomes visible within the page timeout.

        :param locator: XPath locator
        :param error_msg: message to fail with; default names the locator
        """
        if not self.is_element_visible(locator, self.timeout):
            raise AssertionError(error_msg or f"Element {locator!r} is not visible")

    def element_should_contain_text(self, locator: str, text: str, error_msg: str | None = None):
        """Fail unless the element's text contains ``text`` within the page timeout.

        :param locator: XPath locator
        :param text: expected part of the text
        :param error_msg: message to fail with; default names the locator and both texts
        """
        try:
            self.wait_until(EC.text_to_be_present_in_element(self._element_finder.by_locator(locator), text), "")
        except TimeoutException:
            matches = self.find_elements(locator)
            actual = matches[0].text if matches else "<no element>"
            raise AssertionError(error_msg or f"Element {locator!r} shows {actual!r}, expected to contain {text!r}")

    ############################################################################
    # Header methods
    # Scope: Every page > Header cart link, search results
    ############################################################################
    def get_header_cart_count(self) -> int:
        """N in "My Cart (N)". Reads textContent: the desktop link is often hidden, and Selenium's .text is then empty."""
        return self.wait_until(self.header_cart_count_if_shown, "The header never showed a cart count")

    def header_cart_count_if_shown(self, driver=None) -> int | bool:
        """The number in the header cart link, or False until that number is on the page."""
        match = re.search(r"\((\d+)\)", self._read_header_cart_text() or "")
        return int(match.group(1)) if match else False

    def _read_header_cart_text(self) -> str:
        _by, xpath = self._element_finder.by_locator(self._header_cart_link)
        return self.driver.execute_script(
            "var found=document.evaluate(arguments[0], document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);"
            "var text='';"
            "for (var i=0;i<found.snapshotLength;i++){ text += ' ' + (found.snapshotItem(i).textContent||''); }"
            "return text;",
            xpath,
        ) or ""

    def open_search_results(self, keyword: str):
        """Open the search results for ``keyword``.

        The results page has ``#keyword`` ("Showing results..." or "No results found...").
        That node is in the DOM; the full page source is too big to search reliably.
        """
        from urllib.parse import quote

        self.driver.get(f"{self.base_url}/search?type=product&q={quote(keyword)}")
        self.wait_until(
            self.is_search_page_loaded,
            f"Search results for {keyword!r} never loaded (now {self.current_url})",
        )
        if "Verify you are human" in (self.driver.title or ""):
            raise AssertionError(
                "Cloudflare asked to verify a human, so the search page did not open"
            )

    def is_search_page_loaded(self, driver) -> bool:
        """True when the results banner is in the page, or Cloudflare is asking for a human check."""
        return self.is_element_present(self._search_banner) or "Verify you are human" in (driver.title or "")

    # --- Locators -------------------------------------------------------------
    # Whole page
    _page = "//html"
    _page_body = "//body"
    # Header (on every page). Two cart links (desktop and mobile), both "My Cart (N)";
    # read with textContent, not .text: the desktop link is often hidden.
    _header_cart_link = "//a[contains(normalize-space(),'My Cart')]"
    # Search results banner: "Showing results..." or "No results found..."
    _search_banner = "//*[@id='keyword']"
