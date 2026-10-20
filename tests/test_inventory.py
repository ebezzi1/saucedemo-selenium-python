from operator import attrgetter

import pytest

from framework.data import Product, SortOption
from framework.pages import InventoryPage


@pytest.mark.smoke
def test_catalogue_lists_all_products(inventory: InventoryPage):
    assert sorted(inventory.product_names) == sorted(product.value for product in Product)
    assert all(price > 0 for price in inventory.product_prices)


def test_default_sort_is_name_ascending(inventory: InventoryPage):
    assert inventory.sort_dropdown.selected == SortOption.NAME_ASC
    assert inventory.product_names == sorted(inventory.product_names)


# What each option sorts by, and whether it's descending.
SORT_ORDER = {
    SortOption.NAME_ASC: (attrgetter("product_names"), False),
    SortOption.NAME_DESC: (attrgetter("product_names"), True),
    SortOption.PRICE_ASC: (attrgetter("product_prices"), False),
    SortOption.PRICE_DESC: (attrgetter("product_prices"), True),
}


@pytest.mark.parametrize("option", list(SortOption), ids=lambda option: option.name.lower())
def test_sorting(inventory: InventoryPage, option: SortOption):
    if option is SortOption.NAME_ASC:
        inventory.sort_by(SortOption.NAME_DESC)  # move off the default order first

    inventory.sort_by(option)

    read, descending = SORT_ORDER[option]
    assert inventory.active_sort.text == option
    assert read(inventory) == sorted(read(inventory), reverse=descending)


@pytest.mark.smoke
def test_add_and_remove_updates_cart_badge(inventory: InventoryPage):
    inventory.add_to_cart(Product.BACKPACK, Product.ONESIE)
    assert inventory.eventually(lambda: inventory.cart_count == 2)
    assert inventory.is_in_cart(Product.BACKPACK)

    inventory.remove_from_cart(Product.BACKPACK)
    assert inventory.eventually(lambda: inventory.cart_count == 1)
    assert not inventory.is_in_cart(Product.BACKPACK)


def test_reset_app_state_empties_cart(inventory: InventoryPage):
    inventory.add_to_cart(Product.BIKE_LIGHT, Product.FLEECE_JACKET)

    inventory.reset_app_state()

    assert inventory.eventually(lambda: inventory.cart_count == 0)


def test_product_images_are_unique(inventory: InventoryPage):
    sources = inventory.image_sources

    assert len(set(sources)) == len(sources), "Every product should show its own image"
