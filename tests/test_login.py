import pytest

from framework.data import LOCKED_OUT_USER, PASSWORD, STANDARD_USER, USERS_THAT_CAN_LOG_IN, User
from framework.pages import InventoryPage, LoginPage


def visit_inventory_directly(login_page: LoginPage) -> None:
    login_page.driver.get(login_page.page(InventoryPage).url)
    login_page.wait_until_loaded()


@pytest.mark.smoke
@pytest.mark.parametrize("user", USERS_THAT_CAN_LOG_IN, ids=lambda user: user.username)
def test_valid_users_can_log_in(login_page: LoginPage, user: User):
    inventory = login_page.login_as(user)

    assert inventory.title.text == "Products"


def test_locked_out_user_is_rejected(login_page: LoginPage):
    login_page.submit(LOCKED_OUT_USER.username, LOCKED_OUT_USER.password)

    assert login_page.error.text == "Epic sadface: Sorry, this user has been locked out."
    assert login_page.is_current()


@pytest.mark.parametrize(
    ("username", "password", "expected_error"),
    [
        ("", PASSWORD, "Epic sadface: Username is required"),
        (STANDARD_USER.username, "", "Epic sadface: Password is required"),
        (
            STANDARD_USER.username,
            "wrong_password",
            "Epic sadface: Username and password do not match any user in this service",
        ),
        (
            "unknown_user",
            PASSWORD,
            "Epic sadface: Username and password do not match any user in this service",
        ),
    ],
    ids=["missing-username", "missing-password", "wrong-password", "unknown-user"],
)
def test_invalid_credentials_show_error(
    login_page: LoginPage, username: str, password: str, expected_error: str
):
    login_page.submit(username, password)

    assert login_page.error.text == expected_error
    assert login_page.username.has_error
    assert login_page.password.has_error


def test_error_message_can_be_dismissed(login_page: LoginPage):
    login_page.submit("", "")
    login_page.dismiss_error_button.click()

    login_page.error.wait_until_invisible()
    assert not login_page.username.has_error


def test_protected_page_requires_login(login_page: LoginPage):
    visit_inventory_directly(login_page)

    assert (
        login_page.error.text
        == "Epic sadface: You can only access '/inventory.html' when you are logged in."
    )


@pytest.mark.smoke
def test_logout_ends_session(login_page: LoginPage):
    login_page.login_as(STANDARD_USER).logout()

    visit_inventory_directly(login_page)
    assert "when you are logged in" in login_page.error.text
