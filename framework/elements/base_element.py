from __future__ import annotations

from copy import copy

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class BaseElement:
    """A lazily-located UI element declared as a class attribute on a page object.

    Elements are descriptors: declaring ``username = Input(By.ID, "user-name")`` on a page
    gives every page instance a bound element that is located only when it is used, with
    an explicit wait. This keeps page objects declarative and free of ``find_element`` noise.
    """

    def __init__(self, by: str, selector: str, timeout: float | None = None) -> None:
        self.by = by
        self.selector = selector
        self.timeout = timeout
        self.name = self.__class__.__name__
        self._driver: WebDriver | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"{owner.__name__}.{name}"

    def __get__(self, page, owner=None):
        if page is None:
            return self
        bound = copy(self)
        bound._driver = page.driver
        bound.timeout = self.timeout or page.timeout
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
        """Return a copy whose locator is formatted with ``kwargs`` (for parametrised locators)."""
        formatted = copy(self)
        formatted.selector = self.selector.format(**kwargs)
        return formatted

    def _wait(self, timeout: float | None = None) -> WebDriverWait:
        return WebDriverWait(
            self.driver,
            timeout or self.timeout,
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

    def get_attribute(self, name: str) -> str | None:
        return self.find().get_attribute(name)

    def is_displayed(self) -> bool:
        """Non-waiting visibility check, safe to use for asserting absence."""
        elements = self.driver.find_elements(*self.locator)
        return bool(elements) and elements[0].is_displayed()

    def wait_until_invisible(self, timeout: float | None = None) -> None:
        self._wait(timeout).until(
            EC.invisibility_of_element_located(self.locator), f"{self!r} is still visible"
        )
