from __future__ import annotations

from selenium.webdriver.common.by import By

from framework.data import Customer
from framework.elements import Button, Input, Text
from framework.pages import cart_page
from framework.pages.base_page import AuthenticatedPage, ProductListPage, parse_price


class CheckoutInfoPage(AuthenticatedPage):
    path = "/checkout-step-one.html"

    first_name = Input(By.CSS_SELECTOR, "[data-test='firstName']")
    last_name = Input(By.CSS_SELECTOR, "[data-test='lastName']")
    postal_code = Input(By.CSS_SELECTOR, "[data-test='postalCode']")
    continue_button = Button(By.CSS_SELECTOR, "[data-test='continue']")
    cancel_button = Button(By.CSS_SELECTOR, "[data-test='cancel']")
    error = Text(By.CSS_SELECTOR, "[data-test='error']")

    def fill(self, customer: Customer) -> None:
        self.first_name.fill(customer.first_name)
        self.last_name.fill(customer.last_name)
        self.postal_code.fill(customer.postal_code)

    def continue_to_overview(self, customer: Customer) -> CheckoutOverviewPage:
        self.fill(customer)
        self.continue_button.click()
        return self.go_to(CheckoutOverviewPage)

    def cancel(self) -> cart_page.CartPage:
        self.cancel_button.click()
        return self.go_to(cart_page.CartPage)


class CheckoutOverviewPage(ProductListPage):
    path = "/checkout-step-two.html"

    subtotal_label = Text(By.CSS_SELECTOR, "[data-test='subtotal-label']")
    tax_label = Text(By.CSS_SELECTOR, "[data-test='tax-label']")
    total_label = Text(By.CSS_SELECTOR, "[data-test='total-label']")
    finish_button = Button(By.CSS_SELECTOR, "[data-test='finish']")

    @property
    def subtotal(self) -> float:
        return parse_price(self.subtotal_label.text)

    @property
    def tax(self) -> float:
        return parse_price(self.tax_label.text)

    @property
    def total(self) -> float:
        return parse_price(self.total_label.text)

    def finish(self) -> CheckoutCompletePage:
        self.finish_button.click()
        return self.go_to(CheckoutCompletePage)


class CheckoutCompletePage(AuthenticatedPage):
    path = "/checkout-complete.html"

    complete_header = Text(By.CSS_SELECTOR, "[data-test='complete-header']")
