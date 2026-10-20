from __future__ import annotations

from typing import Self

from selenium.webdriver.common.by import By

from framework.data import Product, SortOption
from framework.elements import Button, Collection, Dropdown, Text
from framework.pages import cart_page, login_page
from framework.pages.base_page import AuthenticatedPage


def parse_price(text: str) -> float:
    return float(text.strip().lstrip("$"))


class InventoryPage(AuthenticatedPage):
    path = "/inventory.html"

    sort_dropdown = Dropdown(By.CSS_SELECTOR, "[data-test='product-sort-container']")
    active_sort = Text(By.CSS_SELECTOR, "[data-test='active-option']")
    item_names = Collection(By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    item_prices = Collection(By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    item_images = Collection(By.CSS_SELECTOR, "img.inventory_item_img")
    add_to_cart_button = Button(By.CSS_SELECTOR, "[data-test='add-to-cart-{slug}']")
    remove_button = Button(By.CSS_SELECTOR, "[data-test='remove-{slug}']")

    @property
    def product_names(self) -> list[str]:
        self.item_names.wait_for_any()
        return self.item_names.texts

    @property
    def product_prices(self) -> list[float]:
        self.item_prices.wait_for_any()
        return [parse_price(text) for text in self.item_prices.texts]

    @property
    def image_sources(self) -> list[str]:
        return [img.get_attribute("src") for img in self.item_images.wait_for_any()]

    def sort_by(self, option: SortOption) -> Self:
        self.sort_dropdown.select(option)
        return self

    def add_to_cart(self, *products: Product) -> Self:
        for product in products:
            self.add_to_cart_button.with_args(slug=product.slug).click()
        return self

    def remove_from_cart(self, *products: Product) -> Self:
        for product in products:
            self.remove_button.with_args(slug=product.slug).click()
        return self

    def is_in_cart(self, product: Product) -> bool:
        return self.remove_button.with_args(slug=product.slug).is_displayed()

    def open_cart(self) -> cart_page.CartPage:
        self.cart_link.click()
        return self.go_to(cart_page.CartPage)

    def logout(self) -> login_page.LoginPage:
        self.menu_button.click()
        self.logout_link.click()
        return self.go_to(login_page.LoginPage)
