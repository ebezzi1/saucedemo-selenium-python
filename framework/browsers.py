from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

SUPPORTED_BROWSERS = ("chrome", "firefox", "edge")
WINDOW_SIZE = (1440, 900)

# Chrome/Edge flag SauceDemo's shared demo password as "breached" and pop a native dialog
# that steals focus mid-test. Turning off the password manager keeps runs deterministic.
_CHROMIUM_PREFS = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False,
}


def _chromium_options(options: webdriver.ChromeOptions | webdriver.EdgeOptions, headless: bool):
    if headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}")
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_experimental_option("prefs", _CHROMIUM_PREFS)
    return options


def create_driver(browser: str, headless: bool = False) -> WebDriver:
    """Build a local WebDriver. Driver binaries are resolved by Selenium Manager."""
    match browser.lower():
        case "chrome":
            driver = webdriver.Chrome(
                options=_chromium_options(webdriver.ChromeOptions(), headless)
            )
        case "edge":
            driver = webdriver.Edge(options=_chromium_options(webdriver.EdgeOptions(), headless))
        case "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("-headless")
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(*WINDOW_SIZE)
        case _:
            raise ValueError(
                f"Unsupported browser {browser!r}, expected one of {SUPPORTED_BROWSERS}"
            )
    return driver
