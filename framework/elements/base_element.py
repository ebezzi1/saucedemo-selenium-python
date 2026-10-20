from __future__ import annotations

from copy import copy

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

DEFAULT_TIMEOUT = 10.0


class BaseElement:
    """A page attribute that binds to the page's driver and is located lazily, with waits."""

    def __init__(self, by: str, selector: str) -> None:
        self.by = by
        self.selector = selector
        self.timeout = DEFAULT_TIMEOUT
        self.name = self.__class__.__name__
        self._driver: WebDriver | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"{owner.__name__}.{name}"

    def __get__(self, page, owner=None):
        if page is None:
            return self
        bound = copy(self)
        bound._driver = page.driver
        bound.timeout = page.timeout
        return bound

    def __repr__(self) -> str:
        return f"<{self.name} {self.by}={self.selector!r}>"

    @property
    def locator(self) -> tuple[str, str]:
        return self.by, self.selector

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            raise RuntimeError(f"{self!r} is not bound to a page")
        return self._driver

    def with_args(self, **kwargs: str) -> BaseElement:
        """Fill in a templated locator, e.g. ``"[data-test='remove-{slug}']"``."""
        formatted = copy(self)
        formatted.selector = self.selector.format(**kwargs)
        return formatted

    def _wait(self) -> WebDriverWait:
        return WebDriverWait(
            self.driver,
            self.timeout,
            ignored_exceptions=[StaleElementReferenceException],
        )

    def find(self) -> WebElement:
        return self._wait().until(
            EC.visibility_of_element_located(self.locator), f"{self!r} was not visible"
        )

    def click(self) -> None:
        self._wait().until(
            EC.element_to_be_clickable(self.locator), f"{self!r} not clickable"
        ).click()

    @property
    def text(self) -> str:
        return self.find().text

    def is_displayed(self) -> bool:
        """Non-waiting visibility check, safe to use for asserting absence."""
        elements = self.driver.find_elements(*self.locator)
        return bool(elements) and elements[0].is_displayed()

    def wait_until_invisible(self) -> None:
        self._wait().until(
            EC.invisibility_of_element_located(self.locator), f"{self!r} is still visible"
        )
