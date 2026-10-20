from __future__ import annotations

from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from framework.elements import BaseElement, Button, Link, Text

DEFAULT_TIMEOUT = 10.0


class BasePage:
    """Common behaviour for every page. Subclasses set ``path`` relative to the base URL."""

    path: str = "/"
    # Element whose visibility proves the page has rendered, not just that the URL changed.
    ready_marker: BaseElement | None = None

    def __init__(self, driver: WebDriver, base_url: str, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.path}"

    def open(self) -> Self:
        self.driver.get(self.url)
        return self.wait_until_loaded()

    def wait_until_loaded(self) -> Self:
        WebDriverWait(self.driver, self.timeout).until(
            EC.url_to_be(self.url), f"Expected to be on {self.url}, was {self.driver.current_url}"
        )
        if self.ready_marker is not None:
            self.ready_marker.find()
        return self

    def is_current(self) -> bool:
        return self.driver.current_url == self.url

    def go_to(self, page_cls: type[BasePage]) -> BasePage:
        """Construct another page sharing this page's driver and settings, once it has loaded."""
        return page_cls(self.driver, self.base_url, self.timeout).wait_until_loaded()


class AuthenticatedPage(BasePage):
    """A page behind login, which shares the header, burger menu and cart badge."""

    title = Text(By.CSS_SELECTOR, "[data-test='title']")
    menu_button = Button(By.ID, "react-burger-menu-btn")
    logout_link = Link(By.CSS_SELECTOR, "[data-test='logout-sidebar-link']")
    reset_app_state_link = Link(By.CSS_SELECTOR, "[data-test='reset-sidebar-link']")
    close_menu_button = Button(By.ID, "react-burger-cross-btn")
    cart_link = Link(By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    cart_badge = Text(By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")
    ready_marker = title

    @property
    def cart_count(self) -> int:
        return int(self.cart_badge.text) if self.cart_badge.is_displayed() else 0

    def open_cart(self):
        from framework.pages.cart_page import CartPage

        self.cart_link.click()
        return self.go_to(CartPage)

    def logout(self):
        from framework.pages.login_page import LoginPage

        self.menu_button.click()
        self.logout_link.click()
        return self.go_to(LoginPage)

    def reset_app_state(self) -> Self:
        self.menu_button.click()
        self.reset_app_state_link.click()
        self.close_menu_button.click()
        return self
