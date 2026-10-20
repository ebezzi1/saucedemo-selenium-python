# SauceDemo UI Test Automation — Selenium 4 + pytest

[![UI tests](https://github.com/ebezzi1/saucedemo-selenium-python/actions/workflows/ui-tests.yml/badge.svg)](https://github.com/ebezzi1/saucedemo-selenium-python/actions/workflows/ui-tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Selenium](https://img.shields.io/badge/selenium-4-43B02A)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

An end-to-end UI test framework for [SauceDemo](https://www.saucedemo.com), a demo e-commerce
store. It uses Selenium 4 and pytest with the Page Object Model and runs in CI against Chrome
and Firefox.

## Highlights

- **Declarative page objects:** elements are descriptors (`username = Input(By.CSS_SELECTOR, ...)`)
  that are located lazily with explicit waits. Tests never call `find_element` or `sleep`.
- **Typed element wrappers:** `Button`, `Input`, `Dropdown`, `Collection`, `Text` and `Link`
  hold the Selenium plumbing, including retries on stale elements while React re-renders.
- **Parametrised locators:** `add_to_cart_button.with_args(slug=product.slug)` replaces
  per-product locators.
- **Fluent navigation:** `inventory.add_to_cart(...).open_cart().checkout().continue_to_overview(customer).finish()`
- **Fast setup:** tests that aren't about login sign in by seeding the session cookie. Login
  itself is covered through the UI in `test_login.py`.
- **Data-driven tests:** users, products, sort options and validation cases are parametrised
  from enums and dataclasses.
- **Defect tracking:** the site's deliberately broken accounts are covered by
  `xfail(strict=True)` tests. They document each bug and turn the build red if a bug
  disappears or the check stops detecting it.
- **Failure diagnostics:** a screenshot and the page URL are attached to the HTML report for
  every failed test.
- **Parallel and cross-browser:** `pytest-xdist` runs the tests in parallel, and Chrome,
  Firefox and Edge are selected with `--browser`. Selenium Manager resolves the drivers.
- **CI:** GitHub Actions runs a lint gate (ruff), then a Chrome and Firefox matrix. Reports are
  uploaded as artifacts, and a weekly scheduled run catches changes to the site.

## Test coverage

| Suite | What it checks |
| --- | --- |
| `test_login.py` | Every valid account, locked-out user, missing or wrong credentials, error dismissal, protected-route redirect, logout |
| `test_inventory.py` | Catalogue contents, all four sort orders, add/remove and cart badge, reset app state, image integrity |
| `test_cart.py` | Cart contents, empty cart, removal, persistence across navigation and page reload |
| `test_checkout.py` | Full purchase with subtotal, 8% tax and total checked against catalogue prices; required-field validation; cancel |
| `test_known_defects.py` | `problem_user` and `error_user` bugs (strict xfail) and the `performance_glitch_user` slowdown (timed) |

Known defects caught by the suite:

| Account | Defect |
| --- | --- |
| `problem_user` | Every product shows the same broken (404) image |
| `problem_user` | Sorting has no effect |
| `problem_user` | Last-name field on checkout does not accept input |
| `error_user` | 3 of 6 products cannot be added to the cart |
| `error_user` | "Finish" does not place the order |
| `performance_glitch_user` | Login takes about 5 s, compared with about 0.2 s for `standard_user` |

## Project structure

```
framework/
├── browsers.py            # WebDriver factory (chrome / firefox / edge, headless)
├── data.py                # Users, products, sort options, customer data
├── elements/
│   ├── base_element.py    # Descriptor-based lazy element with explicit waits
│   └── elements.py        # Button, Input, Dropdown, Collection, Text, Link
└── pages/
    ├── base_page.py       # BasePage + AuthenticatedPage (header, menu, cart badge)
    ├── login_page.py
    ├── inventory_page.py
    ├── cart_page.py
    └── checkout_pages.py  # Info -> Overview -> Complete
tests/
├── conftest.py            # CLI options, driver/login fixtures, screenshot-on-failure hook
└── test_*.py
```

## Getting started

Requires Python 3.11+ and Chrome or Firefox installed locally.

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

An HTML report is written to `reports/report.html` on every run. Screenshots of failed tests
are saved to `reports/screenshots/`.

## Code quality

```bash
ruff check .
ruff format --check .
```
