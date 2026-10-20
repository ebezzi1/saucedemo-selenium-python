"""SauceDemo ships deliberately broken accounts. These tests run the same checks as the
standard-user suite against them and are marked ``xfail(strict=True)``: they document the
defects, and the build turns red if a defect is ever silently fixed (or if the check stops
detecting it).
"""

import time

import pytest

from framework.data import (
    ERROR_USER,
    PERFORMANCE_GLITCH_USER,
    PROBLEM_USER,
    STANDARD_USER,
    Customer,
    Product,
    SortOption,
)
from framework.pages import CheckoutCompletePage

pytestmark = pytest.mark.defects


@pytest.mark.xfail(strict=True, reason="problem_user: every product shows the same 404 image")
def test_problem_user_product_images_are_unique(login_as):
    sources = login_as(PROBLEM_USER).image_sources

    assert len(set(sources)) == len(sources)


@pytest.mark.xfail(strict=True, reason="problem_user: sorting has no effect")
def test_problem_user_can_sort_by_price(login_as):
    inventory = login_as(PROBLEM_USER).sort_by(SortOption.PRICE_ASC)

    assert inventory.product_prices == sorted(inventory.product_prices)


@pytest.mark.xfail(strict=True, reason="problem_user: last name field does not accept input")
def test_problem_user_can_enter_last_name(login_as):
    checkout = login_as(PROBLEM_USER).add_to_cart(Product.BACKPACK).open_cart().checkout()

    checkout.fill(Customer())

    assert checkout.last_name.value == Customer().last_name


@pytest.mark.xfail(strict=True, reason="error_user: half the catalogue cannot be added to cart")
def test_error_user_can_add_every_product(login_as):
    inventory = login_as(ERROR_USER)

    for product in Product:
        inventory.add_to_cart_button.with_args(slug=product.slug).click()

    not_added = [product for product in Product if not inventory.is_in_cart(product)]
    assert not_added == []
    assert inventory.cart_count == len(Product)


@pytest.mark.xfail(strict=True, reason="error_user: Finish does not place the order")
def test_error_user_can_complete_checkout(login_as):
    overview = (
        login_as(ERROR_USER)
        .add_to_cart(Product.BACKPACK)
        .open_cart()
        .checkout()
        .continue_to_overview(Customer())
    )

    overview.finish_button.click()

    assert overview.go_to(CheckoutCompletePage).is_current()


@pytest.mark.slow
def test_performance_glitch_user_login_is_slower(login_page, driver):
    """Not a functional defect: measure it, so a regression in either direction is visible."""

    def timed_login(user) -> float:
        driver.delete_all_cookies()
        login_page.open()
        start = time.perf_counter()
        login_page.login_as(user).item_names.wait_for_any()
        return time.perf_counter() - start

    baseline = timed_login(STANDARD_USER)
    glitched = timed_login(PERFORMANCE_GLITCH_USER)

    assert glitched > baseline + 2, f"standard {baseline:.2f}s vs glitch {glitched:.2f}s"
