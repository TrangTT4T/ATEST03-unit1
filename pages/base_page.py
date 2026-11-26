"""Base Page Object (Selenium WebDriver): navigation and the custom element methods every page uses.

Locators are STRINGS with a strategy prefix, so pages never import ``By``:

    _search_box = "name=q"
    _mini_cart  = "xpath=//a[contains(., 'My Cart')]"
    _tile       = "css=a[href*='/products/{path_name}']"  # a template, filled with locator()

``parse_locator()`` below turns the string into the ``(By, value)`` pair Selenium needs.
Prefixes: css, xpath, id, name, tag, link, partial_link, class. No prefix: a value starting with
"//", "(/" or "./" is XPath, anything else is CSS.

Pages never call ``driver.find_element`` or ``WebDriverWait`` themselves. They pass a locator
string to the BasePage methods, which parse it, wait for the right state, log what they do and
fail with a message that names the locator. No method sleeps: every wait is for a state.

Layout of every page object (one class per file), checked by tests/unit/test_page_objects.py:

* methods grouped under ``####`` banners that name the area of the page (``# Scope: ...``);
* a docstring on every public method;
* a ``# --- Locators ---`` section at the BOTTOM of the class, with locator strings only.
"""
import logging
import re

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    path = "/"
    MONEY_PATTERN = re.compile(r"£\s?([\d,]+\.\d{2})")  # a text pattern, not a locator

    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
        self.logger = logging.getLogger(type(self).__name__)  # behave shows these lines when a step fails

    ############################################################################
    # Locator and data helpers (no browser needed)
    # Scope: Every page > locator strings, prices
    ############################################################################
    @staticmethod
    def parse_locator(locator: str) -> tuple[str, str]:
        """'name=q' -> (By.NAME, 'q');  "//a[@id='x']" -> (By.XPATH, "//a[@id='x']");  'input.q' -> (By.CSS_SELECTOR, ...)

        :param locator: a locator string, with or without a strategy prefix
        :return: the (By, value) pair for driver.find_element / expected_conditions
        """
        strategies = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "link": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT,
            "class": By.CLASS_NAME,
        }
        if not isinstance(locator, str) or not locator.strip():
            raise ValueError(f"A locator is a non-empty string such as 'css=#cart', got {locator!r}")
        prefix, separator, value = locator.partition("=")
        if separator and prefix.strip() in strategies:
            if not value.strip():
                raise ValueError(f"Locator {locator!r} has a strategy but no value")
            return strategies[prefix.strip()], value.strip()
        if locator.startswith(("//", "(/", "./")):
            return By.XPATH, locator
        return By.CSS_SELECTOR, locator

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
    def open(self, path: str | None = None):
        """Go to ``path`` (default: this page's own path) on the store.

        :param path: path after the base URL, e.g. "/cart"
        :return: this page, for chaining
        """
        self.logger.info("Open %s", path or self.path)
        self.driver.get(self.base_url + (path or self.path))
        return self

    @property
    def url(self) -> str:
        """The current URL."""
        return self.driver.current_url

    def wait_for_url_contains(self, fragment: str, timeout: int | None = None):
        """Wait until the URL contains ``fragment``.

        :param fragment: text the URL must contain, e.g. "/search"
        :param timeout: seconds; default is the page timeout
        :return: this page
        """
        self.wait_until(EC.url_contains(fragment), f"URL never contained {fragment!r} (now {self.url})", timeout)
        return self

    ############################################################################
    # Locator methods
    # Scope: Every page > locator strings -> elements
    ############################################################################
    @staticmethod
    def locator(template: str, **values) -> str:
        """Fill a locator template: ``locator(self._tile, path_name="grey-jacket")``.

        :param template: locator string with ``{name}`` fields
        :return: the locator string with the fields filled in
        """
        return template.format(**values)

    def find_element(self, locator: str, timeout: int | None = None):
        """Wait until the element is in the page and return it.

        :param locator: locator string, e.g. "css=#cart"
        :param timeout: seconds; default is the page timeout
        :return: the WebElement
        """
        return self.wait_until(EC.presence_of_element_located(self.parse_locator(locator)),
                               f"Element {locator!r} not found", timeout)

    def find_elements(self, locator: str) -> list:
        """All elements matching ``locator`` right now (no wait; an empty list is a valid answer).

        :param locator: locator string
        :return: list of WebElements
        """
        return self.driver.find_elements(*self.parse_locator(locator))

    def is_element_present(self, locator: str) -> bool:
        """True when at least one element matches ``locator`` right now (no wait)."""
        return bool(self.find_elements(locator))

    ############################################################################
    # Action methods
    # Scope: Every page > click, type, submit
    ############################################################################
    def click_element(self, locator: str, timeout: int | None = None):
        """Wait until the element is visible and enabled, then click it.

        :param locator: locator string
        :param timeout: seconds; default is the page timeout
        :return: this page
        """
        self.logger.info("Click %s", locator)
        self.wait_until(EC.element_to_be_clickable(self.parse_locator(locator)),
                        f"Element {locator!r} never became clickable", timeout).click()
        return self

    def click_and_wait_for_new_page(self, locator: str):
        """Click a form button and wait until the browser has replaced the old page.

        Without this, the next driver.get() can cancel the form POST (Day 4 findings F7/F8).

        :param locator: locator string of the submit button
        :return: this page
        """
        old_page = self.find_element(self._html)
        self.click_element(locator)
        self.wait_until(EC.staleness_of(old_page), f"Clicking {locator!r} did not load a new page")
        return self

    def type_text(self, locator: str, text: str, clear: bool = True, secret: bool = False):
        """Type ``text`` into a field (cleared first by default).

        :param locator: locator string of the input
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

    def press_enter(self, locator: str):
        """Press Enter in a field (e.g. submit a search).

        :param locator: locator string of the input
        :return: this page
        """
        self.find_element(locator).send_keys(Keys.ENTER)
        return self

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

    def wait_for_element_visible(self, locator: str, timeout: int | None = None):
        """Wait until the element is visible and return it.

        :param locator: locator string
        :param timeout: seconds; default is the page timeout
        :return: the WebElement
        """
        return self.wait_until(EC.visibility_of_element_located(self.parse_locator(locator)),
                               f"Element {locator!r} never became visible", timeout)

    def get_text(self, locator: str) -> str:
        """Visible text of the element; waits until the element shows some text.

        Selenium's ``.text`` is "" while an element is hidden or still off-screen, e.g. a catalog
        tile sliding in (the theme animates tiles with ``fadeInUpBig``): reading it as soon as it
        exists, or as soon as it counts as "visible", can return "" (Day 4 finding F15).

        :param locator: locator string
        :return: the element's visible text
        :raises TimeoutException: when the element never shows any text
        """
        def first_match_text(driver) -> str | bool:
            try:
                elements = self.find_elements(locator)
                return elements[0].text.strip() if elements else False  # "" = not shown yet: keep waiting
            except StaleElementReferenceException:
                return False

        return self.wait_until(first_match_text, f"Element {locator!r} never showed any text")

    def get_all_texts(self, locator: str) -> list[str]:
        """Visible text of every match, once each one shows its text; [] when nothing matches.

        :param locator: locator string of the items, e.g. the search result links
        :return: their texts, in page order
        """
        texts: list[str] = []

        def every_item_shows_text(driver) -> bool:
            try:
                texts[:] = [element.text.strip() for element in self.find_elements(locator)]
            except StaleElementReferenceException:  # the list re-rendered: read again
                return False
            return all(texts)  # also True for no match at all

        self.wait_until(every_item_shows_text, f"Some {locator!r} never showed their text")
        return texts

    def get_attribute(self, locator: str, name: str) -> str | None:
        """Attribute ``name`` of the element (waits for it to exist)."""
        return self.find_element(locator).get_attribute(name)

    def body_text(self) -> str:
        """All visible text of the page."""
        return self.get_text(self._body)

    def is_element_visible(self, locator: str, timeout: int = 0) -> bool:
        """True when the element is visible, waiting up to ``timeout`` seconds (0: check now).

        :param locator: locator string
        :param timeout: seconds to wait; never a fixed sleep
        :return: True or False, never an exception
        """
        try:
            self.wait_until(EC.visibility_of_element_located(self.parse_locator(locator)), "", timeout)
        except TimeoutException:
            self.logger.info("Element %s is not visible", locator)
            return False
        return True

    def is_element_enabled(self, locator: str, timeout: int = 0) -> bool:
        """True when the element exists and is enabled, waiting up to ``timeout`` seconds (0: check now).

        :param locator: locator string
        :param timeout: seconds to wait; never a fixed sleep
        :return: True or False, never an exception
        """
        try:
            self.wait_until(lambda d: d.find_element(*self.parse_locator(locator)).is_enabled(), "", timeout)
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
            self.logger.info("Element %s is disabled or missing", locator)
            return False
        self.logger.info("Element %s is enabled", locator)
        return True

    ############################################################################
    # Check methods (raise AssertionError with a readable message)
    # Scope: Every page > element state
    ############################################################################
    def element_should_be_visible(self, locator: str, error_msg: str | None = None):
        """Fail unless the element becomes visible within the page timeout.

        :param locator: locator string
        :param error_msg: message to fail with; default names the locator
        :return: this page
        """
        if not self.is_element_visible(locator, self.timeout):
            raise AssertionError(error_msg or f"Element {locator!r} is not visible")
        return self

    def element_should_be_disabled(self, locator: str, error_msg: str | None = None):
        """Fail unless the element is disabled (it must exist).

        :param locator: locator string
        :param error_msg: message to fail with; default names the locator
        :return: this page
        """
        if self.find_element(locator).is_enabled():
            raise AssertionError(error_msg or f"Element {locator!r} is not disabled")
        return self

    def element_should_contain_text(self, locator: str, text: str, error_msg: str | None = None):
        """Fail unless the element's text contains ``text`` within the page timeout.

        :param locator: locator string
        :param text: expected part of the text
        :param error_msg: message to fail with; default names the locator and both texts
        :return: this page
        """
        try:
            self.wait_until(EC.text_to_be_present_in_element(self.parse_locator(locator), text), "")
        except TimeoutException:
            matches = self.find_elements(locator)
            actual = matches[0].text if matches else "<no element>"
            raise AssertionError(error_msg or f"Element {locator!r} shows {actual!r}, expected to contain {text!r}")
        return self

    def page_should_contain_text(self, text: str, error_msg: str | None = None):
        """Fail unless the page shows ``text`` within the page timeout.

        :param text: expected text
        :param error_msg: message to fail with
        :return: this page
        """
        return self.element_should_contain_text(self._body, text, error_msg or f"The page never showed {text!r}")

    ############################################################################
    # Header methods
    # Scope: Every page > Header (mini-cart, search box)
    ############################################################################
    def mini_cart_count(self) -> int:
        """N in "My Cart (N)". Reads textContent: the desktop link is often hidden, and Selenium's .text is then empty."""
        def read(driver) -> int | bool:
            match = re.search(r"\((\d+)\)", self._header_cart_text() or "")
            return int(match.group(1)) if match else False

        return self.wait_until(read, "The header never showed a cart count")

    def mini_cart_count_now(self) -> int | None:
        """The header count right now, or None while the page changes. No wait: for wait conditions."""
        try:
            match = re.search(r"\((\d+)\)", self._header_cart_text() or "")
        except Exception:
            return None
        return int(match.group(1)) if match else None

    def _header_cart_text(self) -> str:
        return self.driver.execute_script(
            "var nodes=document.querySelectorAll('a.cart, a.toggle-drawer');"
            "var text='';"
            "for (var i=0;i<nodes.length;i++){ text += ' ' + (nodes[i].textContent||''); }"
            "return text;"
        ) or ""

    def search(self, keyword: str):
        """Open the search results for ``keyword``.

        Submitting the header form can be intercepted: the URL changes to /search but the
        results document, including #keyword, never loads. A direct navigation does load it.
        """
        from urllib.parse import quote

        self.type_text(self._search_box, keyword)
        self.driver.get(f"{self.base_url}/search?type=product&q={quote(keyword)}")
        self.page_should_contain_text("Search Results", f"Search results for {keyword!r} never loaded")
        return self

    # --- Locators -------------------------------------------------------------
    _html = "tag=html"
    _body = "tag=body"
    # Header (on every page)
    _mini_cart = "xpath=//a[contains(., 'My Cart')]"
    _search_box = "name=q"
    _search_banner = "css=#keyword"
