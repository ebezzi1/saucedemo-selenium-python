# SauceDemo UI Test Automation: Selenium 4 + pytest

[![UI tests](https://github.com/ebezzi1/saucedemo-selenium-python/actions/workflows/ui-tests.yml/badge.svg)](https://github.com/ebezzi1/saucedemo-selenium-python/actions/workflows/ui-tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Selenium](https://img.shields.io/badge/selenium-4-43B02A)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

End-to-end UI tests for [SauceDemo](https://www.saucedemo.com), a demo e-commerce store. Built
with Selenium 4, pytest and the Page Object Model, and run in CI on Chrome, Firefox and Edge.

## Selenium foundations covered

| Concept | Where |
| --- | --- |
| Locators: CSS, ID and XPath | page objects in `framework/pages/` |
| Explicit waits, no `sleep` | `BaseElement` (visibility, clickability, invisibility, stale retries) |
| Page Object Model | one class per page, shared header in `AuthenticatedPage` |
| Dropdowns (`Select`) | product sorting |
| Alerts | `test_browser_interactions.py`: accept and read the error_user sort alert |
| Mouse actions (`ActionChains`) | hover highlight on a product name |
| JavaScript execution | read and clear the cart in `localStorage` |
| Fixtures, setup and teardown | `tests/conftest.py`: driver, login page, logged-in inventory |
| Parametrisation and markers | users, sort options and validation cases; `smoke` and `defects` markers |
| Cross-browser and headless | `--browser chrome/firefox/edge`, `--headless` |
| Reporting | HTML report with a screenshot and URL of each failed test |
| CI | GitHub Actions: ruff lint gate, then a browser × Python matrix |

## How the page objects work

Elements are declared once, as class attributes, and located only when a test uses them:

```python
class LoginPage(BasePage):
    username = Input(By.CSS_SELECTOR, "[data-test='username']")
    login_button = Button(By.CSS_SELECTOR, "[data-test='login-button']")
```

Each element is a [descriptor](https://docs.python.org/3/howto/descriptor.html). Reading
`page.username` hands back a copy bound to that page's driver, so every action runs through an
explicit wait. Templated locators such as `"[data-test='remove-{slug}']"` are filled in with
`with_args(slug=...)`, and navigation is fluent and typed:

```python
complete = (
    inventory.add_to_cart(Product.BACKPACK)
    .open_cart()
    .checkout()
    .continue_to_overview(customer)
    .finish()
)
```

## Test coverage

| Suite | What it checks |
| --- | --- |
| `test_login.py` | Every valid account, locked-out user, missing or wrong credentials, error dismissal, protected-route redirect, logout |
| `test_inventory.py` | Catalogue contents, all four sort orders, add/remove and the cart badge, reset app state, image integrity |
| `test_cart.py` | Cart contents, empty cart, removal, persistence across navigation and reload |
| `test_checkout.py` | Full purchase with subtotal, 8% tax and total checked against catalogue prices; required fields; cancel |
| `test_browser_interactions.py` | Alerts, hover, JavaScript and XPath lookups |
| `test_known_defects.py` | Bugs in SauceDemo's deliberately broken accounts |

### Known defects

Each defect is pinned with a strict `xfail` that only accepts an assertion failure. If a bug is
fixed, or a locator breaks, the build turns red.

| Account | Defect |
| --- | --- |
| `problem_user` | Every product shows the same broken (404) image |
| `problem_user` | Sorting has no effect |
| `problem_user` | Last-name field on checkout does not accept input |
| `error_user` | 3 of 6 products cannot be added to the cart |
| `error_user` | "Finish" does not place the order |

## Project structure

```
framework/
├── browsers.py            # WebDriver factory (chrome / firefox / edge, headless)
├── data.py                # Users, products, sort options, customer data
├── elements/
│   ├── base_element.py    # Lazy element with explicit waits
│   └── elements.py        # Button, Input, Dropdown, Collection, Text, Link
└── pages/
    ├── base_page.py       # BasePage, AuthenticatedPage, ProductListPage
    ├── login_page.py
    ├── inventory_page.py
    ├── cart_page.py
    └── checkout_pages.py  # Info → Overview → Complete
tests/
├── conftest.py            # CLI options, fixtures, screenshot-on-failure hook
└── test_*.py
```

## Getting started

Requires Python 3.11+ and Chrome, Firefox or Edge. Selenium Manager downloads the matching driver.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running tests

```bash
pytest                                   # all tests, Chrome, headed
pytest --headless -n auto                # headless, in parallel
pytest --browser firefox --headless      # another browser
pytest -m smoke                          # critical path only
pytest -m "not defects"                  # skip the known-defect suite
```

| Option | Env var | Default |
| --- | --- | --- |
| `--browser {chrome,firefox,edge}` | `BROWSER` | `chrome` |
| `--headless` | `HEADLESS=true` | off |
| `--base-url` | `BASE_URL` | `https://www.saucedemo.com` |
| `--timeout` | | `10` seconds |

Every run writes an HTML report to `reports/report.html`. Screenshots of failed tests are saved
to `reports/screenshots/`.

## Code quality

```bash
ruff check .
ruff format --check .
```
