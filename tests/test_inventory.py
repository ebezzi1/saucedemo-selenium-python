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


@pytest.mark.parametrize("option", list(SortOption), ids=lambda option: option.name.lower())
def test_sorting(inventory: InventoryPage, option: SortOption):
    inventory.sort_by(option)

    assert inventory.active_sort.text == option
    match option:
        case SortOption.NAME_ASC:
            assert inventory.product_names == sorted(inventory.product_names)
        case SortOption.NAME_DESC:
            assert inventory.product_names == sorted(inventory.product_names, reverse=True)
        case SortOption.PRICE_ASC:
            assert inventory.product_prices == sorted(inventory.product_prices)
        case SortOption.PRICE_DESC:
            assert inventory.product_prices == sorted(inventory.product_prices, reverse=True)


@pytest.mark.smoke
def test_add_and_remove_updates_cart_badge(inventory: InventoryPage):
    inventory.add_to_cart(Product.BACKPACK, Product.ONESIE)
    assert inventory.cart_count == 2
    assert inventory.is_in_cart(Product.BACKPACK)

    inventory.remove_from_cart(Product.BACKPACK)
    assert inventory.cart_count == 1
    assert not inventory.is_in_cart(Product.BACKPACK)


def test_reset_app_state_empties_cart(inventory: InventoryPage):
    inventory.add_to_cart(Product.BIKE_LIGHT, Product.FLEECE_JACKET)

    inventory.reset_app_state()

    assert inventory.cart_count == 0


def test_product_images_are_unique(inventory: InventoryPage):
    sources = inventory.image_sources

    assert len(set(sources)) == len(sources), "Every product should show its own image"
