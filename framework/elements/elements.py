from __future__ import annotations

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from framework.elements.base_element import BaseElement


class Button(BaseElement):
    pass


class Link(BaseElement):
    @property
    def href(self) -> str | None:
        return self.get_attribute("href")


class Text(BaseElement):
    pass


class Input(BaseElement):
    def fill(self, value: str) -> None:
        element = self.find()
        element.clear()
        element.send_keys(value)

    @property
    def value(self) -> str:
        return self.find().get_attribute("value") or ""

    @property
    def has_error(self) -> bool:
        return "error" in (self.find().get_attribute("class") or "").split()


class Dropdown(BaseElement):
    def _select(self) -> Select:
        return Select(self.find())

    def select(self, visible_text: str) -> None:
        self._select().select_by_visible_text(visible_text)

    @property
    def selected(self) -> str:
        return self._select().first_selected_option.text

    @property
    def options(self) -> list[str]:
        return [option.text for option in self._select().options]


class Collection(BaseElement):
    """Every element matching a common locator. An empty collection is a valid state."""

    def find_all(self) -> list[WebElement]:
        return self.driver.find_elements(*self.locator)

    def wait_for_any(self) -> list[WebElement]:
        return self._wait().until(
            EC.visibility_of_all_elements_located(self.locator), f"{self!r} had no visible items"
        )

    @property
    def texts(self) -> list[str]:
        # React may re-render the list between locating and reading it, so retry on staleness.
        # The list is wrapped in a tuple so that an empty (falsy) result still ends the wait.
        (texts,) = self._wait().until(
            lambda _: ([element.text for element in self.find_all()],),
            f"Could not read {self!r}",
        )
        return texts

    def __len__(self) -> int:
        return len(self.find_all())
