from __future__ import annotations

import re

from selenium.webdriver.common.by import By

from framework.data import Customer
from framework.elements import Button, Collection, Input, Text
from framework.pages import cart_page
from framework.pages.base_page import AuthenticatedPage


def _amount(label: str) -> float:
    """Extract the money value from a label such as ``"Tax: $2.40"``."""
    match = re.search(r"\$(\d+(?:\.\d+)?)", label)
    if not match:
        raise ValueError(f"No amount found in {label!r}")
    return float(match.group(1))


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


class CheckoutOverviewPage(AuthenticatedPage):
    path = "/checkout-step-two.html"

    item_names = Collection(By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    subtotal_label = Text(By.CSS_SELECTOR, "[data-test='subtotal-label']")
    tax_label = Text(By.CSS_SELECTOR, "[data-test='tax-label']")
    total_label = Text(By.CSS_SELECTOR, "[data-test='total-label']")
    finish_button = Button(By.CSS_SELECTOR, "[data-test='finish']")

    @property
    def product_names(self) -> list[str]:
        return self.item_names.texts

    @property
    def subtotal(self) -> float:
        return _amount(self.subtotal_label.text)

    @property
    def tax(self) -> float:
        return _amount(self.tax_label.text)

    @property
    def total(self) -> float:
        return _amount(self.total_label.text)

    def finish(self) -> CheckoutCompletePage:
        self.finish_button.click()
        return self.go_to(CheckoutCompletePage)


class CheckoutCompletePage(AuthenticatedPage):
    path = "/checkout-complete.html"

    complete_header = Text(By.CSS_SELECTOR, "[data-test='complete-header']")
