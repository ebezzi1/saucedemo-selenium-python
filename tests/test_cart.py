from framework.data import Product
from framework.pages import InventoryPage


def test_cart_lists_added_products(inventory: InventoryPage):
    products = [Product.BACKPACK, Product.BOLT_TSHIRT, Product.RED_TSHIRT]
    inventory.add_to_cart(*products)

    cart = inventory.open_cart()

    assert sorted(cart.product_names) == sorted(products)
    assert cart.cart_count == len(products)


def test_empty_cart(inventory: InventoryPage):
    cart = inventory.open_cart()

    assert cart.product_names == []
    assert cart.cart_count == 0


def test_remove_product_from_cart(inventory: InventoryPage):
    cart = inventory.add_to_cart(Product.BACKPACK, Product.ONESIE).open_cart()

    cart.remove(Product.BACKPACK)

    assert cart.product_names == [Product.ONESIE]
    assert cart.cart_count == 1


def test_cart_persists_while_shopping(inventory: InventoryPage):
    cart = inventory.add_to_cart(Product.FLEECE_JACKET).open_cart()

    inventory = cart.continue_shopping()
    inventory.add_to_cart(Product.BIKE_LIGHT)

    assert inventory.is_in_cart(Product.FLEECE_JACKET)
    assert sorted(inventory.open_cart().product_names) == sorted(
        [Product.FLEECE_JACKET, Product.BIKE_LIGHT]
    )


def test_cart_survives_page_reload(inventory: InventoryPage):
    inventory.add_to_cart(Product.ONESIE)

    inventory.driver.refresh()
    inventory.wait_until_loaded()

    assert inventory.cart_count == 1
    assert inventory.is_in_cart(Product.ONESIE)
