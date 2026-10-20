from __future__ import annotations

from typing import Self

from selenium.webdriver.common.by import By

from framework.data import Product
from framework.elements import Button, Collection
from framework.pages.base_page import AuthenticatedPage


class CartPage(AuthenticatedPage):
    path = "/cart.html"

    item_names = Collection(By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    remove_button = Button(By.CSS_SELECTOR, "[data-test='remove-{slug}']")
    continue_shopping_button = Button(By.CSS_SELECTOR, "[data-test='continue-shopping']")
    checkout_button = Button(By.CSS_SELECTOR, "[data-test='checkout']")

    @property
    def product_names(self) -> list[str]:
        return self.item_names.texts

    def remove(self, product: Product) -> Self:
        self.remove_button.with_args(slug=product.slug).click()
        return self

    def continue_shopping(self):
        from framework.pages.inventory_page import InventoryPage

        self.continue_shopping_button.click()
        return self.go_to(InventoryPage)

    def checkout(self):
        from framework.pages.checkout_pages import CheckoutInfoPage

        self.checkout_button.click()
        return self.go_to(CheckoutInfoPage)
