from __future__ import annotations

from selenium.webdriver.common.by import By

from framework.data import User
from framework.elements import Button, Input, Text
from framework.pages.base_page import BasePage
from framework.pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    path = "/"

    username = Input(By.CSS_SELECTOR, "[data-test='username']")
    password = Input(By.CSS_SELECTOR, "[data-test='password']")
    login_button = Button(By.CSS_SELECTOR, "[data-test='login-button']")
    error = Text(By.CSS_SELECTOR, "[data-test='error']")
    dismiss_error_button = Button(By.CSS_SELECTOR, "[data-test='error-button']")
    ready_marker = login_button

    def submit(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()

    def login_as(self, user: User) -> InventoryPage:
        self.submit(user.username, user.password)
        return self.go_to(InventoryPage)
