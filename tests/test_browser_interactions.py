from framework.data import ERROR_USER, Product, SortOption
from framework.pages import InventoryPage

SORT_ERROR = "Sorting is broken! This error has been reported to Backtrace."


def test_alert_is_read_and_accepted(login_as):
    inventory = login_as(ERROR_USER).sort_by(SortOption.NAME_DESC)

    assert inventory.accept_alert() == SORT_ERROR
    assert inventory.active_sort.text == SortOption.NAME_ASC


def test_hovering_a_product_highlights_its_name(inventory: InventoryPage):
    name = inventory.product_title.with_args(name=Product.BACKPACK)
    resting_color = name.css("color")

    name.hover()

    assert inventory.eventually(lambda: name.css("color") != resting_color)


def test_cart_is_stored_in_local_storage(inventory: InventoryPage):
    inventory.add_to_cart(Product.BACKPACK, Product.ONESIE)
    assert inventory.eventually(lambda: len(inventory.stored_cart()) == inventory.cart_count == 2)

    inventory.clear_stored_cart()
    inventory.driver.refresh()
    inventory.wait_until_loaded()

    assert inventory.cart_count == 0


def test_price_lookup_by_product_name(inventory: InventoryPage):
    assert inventory.price_of(Product.BACKPACK) == 29.99
    assert inventory.price_of(Product.RED_TSHIRT) == 15.99
