from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from framework.browsers import SUPPORTED_BROWSERS, create_driver
from framework.data import STANDARD_USER, User
from framework.pages import InventoryPage, LoginPage

SCREENSHOT_DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("selenium")
    group.addoption(
        "--browser",
        default=os.getenv("BROWSER", "chrome"),
        choices=SUPPORTED_BROWSERS,
        help="Browser to run against (env: BROWSER)",
    )
    group.addoption(
        "--headless",
        action="store_true",
        default=os.getenv("HEADLESS", "").lower() in ("1", "true"),
        help="Run the browser headless (env: HEADLESS=true)",
    )
    group.addoption(
        "--base-url",
        default=os.getenv("BASE_URL", "https://www.saucedemo.com"),
        help="Application under test (env: BASE_URL)",
    )
    group.addoption("--timeout", type=float, default=10.0, help="Explicit wait timeout in seconds")


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("base_url")


@pytest.fixture(scope="session")
def timeout(pytestconfig: pytest.Config) -> float:
    return pytestconfig.getoption("timeout")


@pytest.fixture
def driver(pytestconfig: pytest.Config) -> Iterator[WebDriver]:
    web_driver = create_driver(
        pytestconfig.getoption("browser"), headless=pytestconfig.getoption("headless")
    )
    yield web_driver
    web_driver.quit()


@pytest.fixture
def login_page(driver: WebDriver, base_url: str, timeout: float) -> LoginPage:
    return LoginPage(driver, base_url, timeout).open()


@pytest.fixture
def login_as(driver: WebDriver, base_url: str, timeout: float):
    """Log in without the UI by seeding the session cookie SauceDemo uses.

    UI login is covered by ``test_login.py``; everywhere else this shortcut keeps tests fast
    and focused on the feature they actually exercise.
    """

    def _login(user: User = STANDARD_USER) -> InventoryPage:
        driver.get(base_url)
        driver.add_cookie({"name": "session-username", "value": user.username})
        return InventoryPage(driver, base_url, timeout).open()

    return _login


@pytest.fixture
def inventory(login_as) -> InventoryPage:
    return login_as(STANDARD_USER)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Attach a screenshot to the HTML report (and save it to disk) when a test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when not in ("setup", "call") or not report.failed:
        return
    web_driver: WebDriver | None = item.funcargs.get("driver")
    if web_driver is None:
        return

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    file_name = re.sub(r"[^\w.-]", "_", item.nodeid) + ".png"
    web_driver.save_screenshot(str(SCREENSHOT_DIR / file_name))

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.png(web_driver.get_screenshot_as_base64(), "Screenshot"))
        extras.append(pytest_html.extras.url(web_driver.current_url, "Page URL"))
        report.extras = extras
