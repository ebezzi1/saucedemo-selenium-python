"""Known bugs in SauceDemo's broken demo accounts, pinned with strict xfails."""

import pytest

from framework.data import ERROR_USER, PROBLEM_USER, Customer, Product, SortOption
from framework.pages import CheckoutCompletePage

pytestmark = pytest.mark.defects


def known_defect(reason: str) -> pytest.MarkDecorator:
    """Expect an assertion failure; any other error (or a pass) fails the build."""
    return pytest.mark.xfail(reason=reason, strict=True, raises=AssertionError)


@known_defect("problem_user: every product shows the same 404 image")
def test_problem_user_product_images_are_unique(login_as):
    sources = login_as(PROBLEM_USER).image_sources

    assert len(set(sources)) == len(sources)


@known_defect("problem_user: sorting has no effect")
def test_problem_user_can_sort_by_price(login_as):
    inventory = login_as(PROBLEM_USER).sort_by(SortOption.PRICE_ASC)

    assert inventory.product_prices == sorted(inventory.product_prices)


@known_defect("problem_user: last name field does not accept input")
def test_problem_user_can_enter_last_name(login_as):
    checkout = login_as(PROBLEM_USER).add_to_cart(Product.BACKPACK).open_cart().checkout()

    checkout.fill(Customer())

    assert checkout.last_name.value == Customer().last_name


@known_defect("error_user: half the catalogue cannot be added to cart")
def test_error_user_can_add_every_product(login_as):
    inventory = login_as(ERROR_USER).add_to_cart(*Product)

    not_added = [product for product in Product if not inventory.is_in_cart(product)]
    assert not_added == []
    assert inventory.cart_count == len(Product)


@known_defect("error_user: Finish does not place the order")
def test_error_user_can_complete_checkout(login_as):
    overview = (
        login_as(ERROR_USER)
        .add_to_cart(Product.BACKPACK)
        .open_cart()
        .checkout()
        .continue_to_overview(Customer())
    )

    overview.finish_button.click()

    assert overview.page(CheckoutCompletePage).is_loaded()
