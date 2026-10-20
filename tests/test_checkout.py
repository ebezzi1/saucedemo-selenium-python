import pytest

from framework.data import TAX_RATE, Customer, Product
from framework.pages import CheckoutInfoPage, InventoryPage


@pytest.fixture
def checkout_info(inventory: InventoryPage) -> CheckoutInfoPage:
    return inventory.add_to_cart(Product.BACKPACK).open_cart().checkout()


@pytest.mark.smoke
def test_end_to_end_purchase(inventory: InventoryPage):
    products = [Product.BACKPACK, Product.BOLT_TSHIRT, Product.ONESIE]
    expected_prices = dict(zip(inventory.product_names, inventory.product_prices, strict=True))

    overview = (
        inventory.add_to_cart(*products).open_cart().checkout().continue_to_overview(Customer())
    )

    assert sorted(overview.product_names) == sorted(products)
    expected_subtotal = round(sum(expected_prices[product] for product in products), 2)
    assert overview.subtotal == expected_subtotal
    assert overview.tax == round(expected_subtotal * TAX_RATE, 2)
    assert overview.total == round(overview.subtotal + overview.tax, 2)

    complete = overview.finish()

    assert complete.complete_header.text == "Thank you for your order!"
    assert complete.cart_count == 0


@pytest.mark.parametrize(
    ("customer", "expected_error"),
    [
        (Customer(first_name=""), "Error: First Name is required"),
        (Customer(last_name=""), "Error: Last Name is required"),
        (Customer(postal_code=""), "Error: Postal Code is required"),
    ],
    ids=["missing-first-name", "missing-last-name", "missing-postal-code"],
)
def test_checkout_requires_customer_details(
    checkout_info: CheckoutInfoPage, customer: Customer, expected_error: str
):
    checkout_info.fill(customer)
    checkout_info.continue_button.click()

    assert checkout_info.error.text == expected_error
    assert checkout_info.is_current()


def test_cancel_checkout_returns_to_cart(checkout_info: CheckoutInfoPage):
    cart = checkout_info.cancel()

    assert cart.product_names == [Product.BACKPACK]
